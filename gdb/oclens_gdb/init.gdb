# OCLens GDB bootstrap — sourced by `oclens debug`.
python
import os
import sys
from pathlib import Path

repo = Path(os.environ.get("OCLENS_ROOT", ".")).resolve()
gdb_pkg = Path(os.environ.get("OCLENS_GDB_PKG", repo / "gdb")).resolve()
if str(gdb_pkg) not in sys.path:
    sys.path.insert(0, str(gdb_pkg))

import oclens_gdb
oclens_gdb.register_extension()
print("OCLens: GDB extension loaded")
end
