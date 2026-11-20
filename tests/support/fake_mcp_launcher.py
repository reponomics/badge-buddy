"""A bounded stand-in for a launcher whose child inherits the MCP pipes."""

import os
import subprocess
import sys
from pathlib import Path

survivor = Path(sys.argv[1])
child = subprocess.Popen(
    [
        sys.executable,
        "-c",
        "import sys, time; from pathlib import Path; "
        "time.sleep(2); Path(sys.argv[1]).write_text('child survived')",
        str(survivor),
    ]
)
survivor.with_suffix(".started").write_text(str(child.pid))
if os.environ.get("FAKE_MCP_MODE") == "launcher_exit":
    # Model a launcher that has exited while its child still owns the MCP pipe.
    os._exit(0)
if os.environ.get("FAKE_MCP_MODE") == "invalid_json":
    print("not JSON", flush=True)
# Even the broken client finishes once this child exits: a regression cannot hang CI.
child.wait()
