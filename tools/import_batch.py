#!/usr/bin/env python3
"""按 tools/import_manifest.json 批量导入单篇。"""

import json
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
WORK = ROOT / "_work" / "pages"


def main() -> int:
    manifest = json.loads((HERE / "import_manifest.json").read_text(encoding="utf-8"))
    base = manifest["archive_base"]
    failed = []
    for job in manifest["jobs"]:
        src = job.get("source") or (base + job["path"])
        cmd = [
            sys.executable, "-X", "utf8", str(HERE / "import_page.py"),
            "--file", str(WORK / job["file"]),
            "--title", job["title"],
            "--author", job["author"],
            "--source", src,
            "--mode", job["mode"],
        ]
        if job.get("selector"):
            cmd += ["--selector", job["selector"]]
        for c in job.get("cut", []):
            cmd += ["--cut", c]
        print("\n" + "-" * 60)
        r = subprocess.run(cmd)
        if r.returncode != 0:
            failed.append(job["title"])
    print("\n" + "=" * 60)
    print(f"完成 {len(manifest['jobs']) - len(failed)}/{len(manifest['jobs'])}")
    if failed:
        print("失败:", "、".join(failed))
    return 2 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
