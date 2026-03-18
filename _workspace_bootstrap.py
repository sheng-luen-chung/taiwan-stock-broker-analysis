from pathlib import Path
import sys


def ensure_src_on_path() -> None:
    repo_root = Path(__file__).resolve().parent
    src_path = repo_root / "src"
    src_text = str(src_path)
    if src_text not in sys.path:
        sys.path.insert(0, src_text)