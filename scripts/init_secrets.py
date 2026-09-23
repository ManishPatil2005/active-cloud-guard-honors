"""Generate local lab credentials without displaying or committing them."""

from pathlib import Path
import secrets


def main():
    directory = Path(__file__).resolve().parents[1] / "testbed" / "secrets"
    directory.mkdir(parents=True, exist_ok=True)
    for name in ("pg_password.txt", "minio_password.txt"):
        path = directory / name
        if not path.exists():
            with path.open("x", encoding="utf-8") as stream:
                stream.write(secrets.token_urlsafe(32))
    print("Local credentials ready; values not displayed.")


if __name__ == "__main__":
    main()
