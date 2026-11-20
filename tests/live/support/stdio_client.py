"""Small bounded stdio client for plugin integration tests, not an MCP SDK."""

import contextlib
import json
import os
import signal
import subprocess
import tempfile
import threading


class StdioClient:
    def __init__(self, process):
        self.process = process
        self.next_id = 0

    def send(self, message):
        self.process.stdin.write(json.dumps(message) + "\n")
        self.process.stdin.flush()

    def request(self, method, params=None):
        self.next_id += 1
        request_id = self.next_id
        self.send(
            {
                "jsonrpc": "2.0",
                "id": request_id,
                "method": method,
                "params": params or {},
            }
        )
        for line in self.process.stdout:
            message = json.loads(line)
            if message.get("id") != request_id:
                continue
            if "error" in message:
                raise AssertionError(f"MCP request failed: {message['error']}")
            return message["result"]
        raise AssertionError(f"MCP server stopped before answering {method}")

    def call(self, name, arguments, *, error=None):
        result = self.request("tools/call", {"name": name, "arguments": arguments})
        payload = result.get("structuredContent")
        if payload is None:
            payload = json.loads(result["content"][0]["text"])
        if error is not None:
            if (
                not result.get("isError")
                or payload.get("error", {}).get("code") != error
            ):
                raise AssertionError(f"Expected {error}, received {payload}")
        elif result.get("isError"):
            raise AssertionError(f"{name} failed: {payload}")
        return payload


def stop(process):
    try:
        if os.name == "posix":
            os.killpg(process.pid, signal.SIGKILL)
        else:
            process.kill()
    except ProcessLookupError:
        pass


@contextlib.contextmanager
def server_session(command, *, environment=None, timeout=60):
    """Initialize one server; cap startup, requests, and shutdown together."""
    with tempfile.TemporaryFile(mode="w+t", encoding="utf-8") as errors:
        try:
            with subprocess.Popen(
                command,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=errors,
                encoding="utf-8",
                env={**os.environ, **(environment or {})},
                start_new_session=os.name == "posix",
            ) as process:
                timed_out = threading.Event()

                def on_timeout():
                    timed_out.set()
                    stop(process)

                watchdog = threading.Timer(timeout, on_timeout)
                watchdog.start()
                try:
                    client = StdioClient(process)
                    client.initialize = client.request(
                        "initialize",
                        {
                            "protocolVersion": "2025-06-18",
                            "capabilities": {},
                            "clientInfo": {
                                "name": "badge-buddy-contract-test",
                                "version": "1",
                            },
                        },
                    )
                    client.send(
                        {"jsonrpc": "2.0", "method": "notifications/initialized"}
                    )
                    yield client
                finally:
                    # Keep the launcher unreaped until the timer is joined and
                    # its group is stopped, including any pipe-holding child.
                    watchdog.cancel()
                    watchdog.join()
                    if not timed_out.is_set():
                        stop(process)
        except (AssertionError, OSError, ValueError) as exc:
            errors.seek(0)
            raise AssertionError(f"{exc}\n{errors.read()[-2000:]}") from exc
