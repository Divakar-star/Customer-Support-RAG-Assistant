import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.core.config import get_settings  # noqa: E402
from app.core.constants import SUPPORTED_EXTENSIONS  # noqa: E402
from app.ingestion.pipeline import ingest_file  # noqa: E402
from app.storage.sqlite import init_db  # noqa: E402


def main() -> None:
    init_db()
    settings = get_settings()
    raw_dir = Path(settings.raw_dir)
    raw_dir.mkdir(parents=True, exist_ok=True)

    files = sorted(p for p in raw_dir.iterdir() if p.suffix.lower() in SUPPORTED_EXTENSIONS)
    if not files:
        print(f"No documents found in {raw_dir}. Add PDF/TXT/MD files and re-run.")
        return

    for path in files:
        result = ingest_file(str(path))
        print(
            f"{path.name}: {result['status']} "
            f"({result['chunks_created']} chunks) -> {result['document_id']}"
        )


if __name__ == "__main__":
    main()
