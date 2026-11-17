"""Run the test suite, then package the app into dist/expense-mate-v<VERSION>.zip.

Usage:
    python build.py                # run tests, then package
    python build.py --skip-tests   # package only
"""
import subprocess
import sys
import zipfile
from pathlib import Path

VERSION = "1.0"
ROOT = Path(__file__).resolve().parent
DIST = ROOT / "dist"
ARTIFACT = DIST / f"expense-mate-v{VERSION}.zip"
FILES = ["app.py", "requirements.txt"]
DIRS = ["templates"]


def run_tests():
    print("==> Running tests")
    result = subprocess.run([sys.executable, "-m", "pytest", "tests"], cwd=ROOT)
    if result.returncode != 0:
        print("Tests failed. Build aborted.", file=sys.stderr)
        sys.exit(result.returncode)


def collect_files():
    paths = [ROOT / name for name in FILES]
    for d in DIRS:
        paths += [
            p for p in sorted((ROOT / d).rglob("*"))
            if p.is_file() and "__pycache__" not in p.parts and p.suffix != ".pyc"
        ]
    missing = [p for p in paths if not p.exists()]
    if missing:
        print("Missing files: " + ", ".join(str(p.relative_to(ROOT)) for p in missing), file=sys.stderr)
        sys.exit(1)
    return paths


def package():
    print(f"==> Packaging {ARTIFACT.relative_to(ROOT)}")
    DIST.mkdir(exist_ok=True)
    ARTIFACT.unlink(missing_ok=True)
    with zipfile.ZipFile(ARTIFACT, "w", zipfile.ZIP_DEFLATED) as zf:
        for path in collect_files():
            arcname = path.relative_to(ROOT).as_posix()
            zf.write(path, arcname)
            print(f"    added {arcname}")
    print(f"==> Done: {ARTIFACT}")


def main():
    if "--skip-tests" not in sys.argv[1:]:
        run_tests()
    package()


if __name__ == "__main__":
    main()
