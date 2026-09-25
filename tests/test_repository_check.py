from scripts.repository_check import forbidden, local_links, suspected_secret


def test_runtime_material_is_excluded():
    for path in [
        "testbed/secrets/pg_password.txt",
        "output/chroma/chroma.sqlite3",
        "output/audit-cache/sample.json",
        "output/runtime-raw/events.json",
        ".venv/a.py",
        ".env.local",
        "tmp/pdfs/page.png",
    ]:
        assert forbidden(path)
    for path in [
        ".env.example",
        "docs/SECURITY.md",
        "data/development/postgres-secret.yaml",
        "output/rag-smoke.json",
    ]:
        assert not forbidden(path)


def test_credentials_detected_without_treating_fixture_as_credential():
    assert suspected_secret(("ghp_" + "a" * 36).encode())
    assert suspected_secret(("AKIA" + "A" * 16).encode())
    assert not suspected_secret(b"POSTGRES_PASSWORD: fixture-only")


def test_document_link_selection():
    text = "[Local](ARCHITECTURE.md) [Web](https://example.org) [Part](#scope) [File](a%20b.md#item)"
    assert list(local_links(text)) == ["ARCHITECTURE.md", "a b.md"]
