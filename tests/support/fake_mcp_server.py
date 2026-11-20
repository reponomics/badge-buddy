#!/usr/bin/env python3
"""A stdio stand-in for the Best Practices MCP server, serving the test records.

``FAKE_MCP_MODE`` selects a failure: ``tool_error`` returns an error result,
``exit`` stops before answering the tool call, and ``stall`` never answers it.
"""

import json
import os
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from criteria_records import RECORDS

MODE = os.environ.get("FAKE_MCP_MODE", "")


def reply(request_id, result):
    print(
        json.dumps({"jsonrpc": "2.0", "id": request_id, "result": result}), flush=True
    )


for line in sys.stdin:
    message = json.loads(line)
    method = message.get("method")
    if method == "initialize":
        reply(
            message["id"],
            {
                "protocolVersion": message["params"]["protocolVersion"],
                "capabilities": {"tools": {}},
                "serverInfo": {"name": "fake-bestpractices", "version": "0"},
            },
        )
    elif method == "tools/call":
        if MODE == "exit":
            sys.exit(3)
        if MODE == "stall":
            time.sleep(60)
        # A real server may interleave notifications with responses.
        print(
            json.dumps(
                {"jsonrpc": "2.0", "method": "notifications/message", "params": {}}
            ),
            flush=True,
        )
        arguments = message["params"]["arguments"]
        level = arguments.get("level")
        if MODE == "tool_error" or level not in RECORDS:
            payload = {
                "schema_version": 1,
                "error": {"code": "invalid_level", "message": "No such level."},
            }
            reply(
                message["id"],
                {
                    "content": [{"type": "text", "text": json.dumps(payload)}],
                    "isError": True,
                },
            )
            continue
        payload = {
            "schema_version": 2,
            "level": level,
            "detail": arguments.get("detail"),
            "criteria": RECORDS[level],
        }
        result = {
            "content": [{"type": "text", "text": json.dumps(payload)}],
            "isError": False,
        }
        if MODE != "text_only":
            result["structuredContent"] = payload
        reply(message["id"], result)
