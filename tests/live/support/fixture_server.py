"""Run the installed, pinned server with synthetic HTTP and isolated storage.

The parent launches this file with ``python -I`` inside the uvx environment, so
imports resolve to the published package, never the adjacent MCP checkout.
"""

import json
import sys
from pathlib import Path

import httpx2
from best_practices_mcp.http import BadgeAppHTTP
from best_practices_mcp.server import create_server

PROJECT = {
    "id": 123,
    "name": "Badge Buddy contract fixture",
    "repo_url": "https://example.org/fixture",
    "homepage_url": "https://example.org/fixture",
    "badge_level": "in_progress",
    "badge_percentage_0": 12,
    "description_good_status": "Met",
    "description_good_justification": "The fixture documents its purpose.",
    "contribution_status": "Met",
    "contribution_justification": "See https://example.org/fixture/contributing.",
}


def main() -> None:
    root = Path(sys.argv[1]).resolve(strict=True)

    def respond(request):
        with (root / "requests.jsonl").open("a", encoding="utf-8") as log:
            log.write(
                json.dumps({"method": request.method, "url": str(request.url)}) + "\n"
            )
        if request.method != "GET" or request.url.host != "www.bestpractices.dev":
            raise AssertionError(f"Unexpected request: {request.method} {request.url}")
        if request.url.path == "/projects.json":
            return httpx2.Response(200, json=[PROJECT])
        if request.url.path == "/projects/123.json":
            return httpx2.Response(200, json=PROJECT)
        raise AssertionError(f"Unexpected fixture path: {request.url.path}")

    def http_factory():
        return BadgeAppHTTP(transport=httpx2.MockTransport(respond))

    create_server(http_factory=http_factory, data_root=root / "drafts").run(
        transport="stdio"
    )


if __name__ == "__main__":
    main()
