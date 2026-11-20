"""Read badge criteria from the plugin's Best Practices MCP server.

The board shows official criterion text, which the server packages and returns
through its ``get_criteria`` tool. This module starts the server registered in
the plugin's ``.mcp.json``, makes that one call over stdio, and stops it.
"""

from __future__ import annotations

import json
import os
import signal
import subprocess
import tempfile
import threading
from pathlib import Path
from typing import IO, Any

DEFAULT_CONFIG = Path(__file__).resolve().parents[2] / ".mcp.json"
SERVER_NAME = "bestpractices"
TIMEOUT_SECONDS = 60
_PROTOCOL_VERSION = "2025-06-18"
_CLIENT = {"name": "badge-buddy-board", "version": "1"}


class CriteriaUnavailable(RuntimeError):
    """The server could not be started or did not return the criteria."""


def server_command(
    config_path: Path = DEFAULT_CONFIG,
) -> tuple[list[str], dict[str, str]]:
    """Return the stdio command and extra environment registered for the server."""

    try:
        config = json.loads(Path(config_path).read_text(encoding="utf-8"))
        server = config["mcpServers"][SERVER_NAME]
        command = [server["command"], *server.get("args", [])]
        environment = dict(server.get("env", {}))
    except (OSError, ValueError, KeyError, TypeError) as exc:
        raise CriteriaUnavailable(
            f"{config_path} does not register a {SERVER_NAME!r} stdio server"
        ) from exc
    if not all(isinstance(part, str) and part for part in command) or not all(
        isinstance(key, str) and isinstance(value, str)
        for key, value in environment.items()
    ):
        raise CriteriaUnavailable(f"{config_path} has an invalid {SERVER_NAME!r} entry")
    return command, environment


def fetch_criteria(
    level: str,
    *,
    config_path: Path = DEFAULT_CONFIG,
    timeout: float = TIMEOUT_SECONDS,
) -> list[dict[str, Any]]:
    """Return the full criterion records of one badge level, as the server orders them."""

    command, environment = server_command(config_path)
    with tempfile.TemporaryFile() as errors:
        try:
            # The command is the plugin's own server registration, read from its .mcp.json.
            process = subprocess.Popen(  # noqa: S603
                command,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=errors,
                env={**os.environ, **environment},
                encoding="utf-8",
                start_new_session=os.name == "posix",
            )
        except OSError as exc:
            raise CriteriaUnavailable(f"could not start {command[0]!r}: {exc}") from exc

        # uvx launches a child that inherits the pipes; stop the whole group so
        # that child cannot keep a read blocked after its launcher is killed.
        timed_out = threading.Event()

        def on_timeout() -> None:
            timed_out.set()
            _stop_server(process)

        watchdog = threading.Timer(timeout, on_timeout)
        watchdog.start()
        try:
            with process:
                try:
                    return _call_get_criteria(process.stdin, process.stdout, level)  # type: ignore[arg-type]
                finally:
                    # Cancel and join before reaping the launcher, so the timer
                    # cannot later signal a process group whose ID was reused.
                    watchdog.cancel()
                    watchdog.join()
                    # The timeout already stopped the group. Signaling it again
                    # after the launcher exited can fail and mask the read error.
                    if not timed_out.is_set():
                        _stop_server(process)
        except (OSError, ValueError, KeyError, TypeError) as exc:
            errors.seek(0)
            detail = errors.read().decode("utf-8", errors="replace").strip()
            message = f"the {SERVER_NAME} MCP server did not return criteria for {level}: {exc}"
            raise CriteriaUnavailable(
                f"{message}\n{detail[-2000:]}" if detail else message
            ) from exc


def _stop_server(process: subprocess.Popen[str]) -> None:
    """Stop the isolated POSIX process group, or just the child on other systems.

    Windows process-tree termination is not provided by this stdlib client; its
    timeout can only stop a directly launched server, not a launcher's children.
    """
    try:
        if os.name == "posix":
            os.killpg(process.pid, signal.SIGKILL)
        else:
            process.kill()
    except ProcessLookupError:
        pass


def _call_get_criteria(
    stdin: IO[str], stdout: IO[str], level: str
) -> list[dict[str, Any]]:
    _send(
        stdin,
        {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "initialize",
            "params": {
                "protocolVersion": _PROTOCOL_VERSION,
                "capabilities": {},
                "clientInfo": _CLIENT,
            },
        },
    )
    _response(stdout, 1)
    _send(stdin, {"jsonrpc": "2.0", "method": "notifications/initialized"})
    _send(
        stdin,
        {
            "jsonrpc": "2.0",
            "id": 2,
            "method": "tools/call",
            "params": {
                "name": "get_criteria",
                "arguments": {"level": level, "detail": "full"},
            },
        },
    )
    result = _response(stdout, 2)
    payload = result.get("structuredContent")
    if payload is None:
        payload = json.loads(result["content"][0]["text"])
    if result.get("isError"):
        raise ValueError(payload.get("error", {}).get("message", "get_criteria failed"))
    criteria = payload["criteria"]
    if payload.get("level") != level or not isinstance(criteria, list) or not criteria:
        raise ValueError("unexpected get_criteria result")
    return criteria


def _send(stdin: IO[str], message: dict[str, Any]) -> None:
    stdin.write(json.dumps(message) + "\n")
    stdin.flush()


def _response(stdout: IO[str], request_id: int) -> dict[str, Any]:
    """Read messages until the response to ``request_id``, skipping notifications."""

    while True:
        line = stdout.readline()
        if not line:
            raise ValueError("the server stopped before answering")
        message = json.loads(line)
        if message.get("id") != request_id:
            continue
        if "error" in message:
            raise ValueError(message["error"].get("message", "request failed"))
        return message["result"]
