from harness_gen import managed_block
from harness_gen.managed_block import END_MARKER, START_MARKER


def test_new_file_wraps_body():
    out = managed_block.merge(None, "hello")
    assert out.startswith(START_MARKER)
    assert "hello" in out
    assert out.rstrip().endswith(END_MARKER)


def test_new_file_with_prefix():
    out = managed_block.merge(None, "body", prefix_if_new="---\nx: 1\n---")
    assert out.startswith("---\nx: 1\n---")
    assert START_MARKER in out


def test_append_preserves_existing_content():
    existing = "# My own notes\n\nkeep me"
    out = managed_block.merge(existing, "harness body")
    assert "# My own notes" in out
    assert "keep me" in out
    assert "harness body" in out


def test_replace_updates_block_only():
    existing = (
        "# Top\n\n"
        f"{START_MARKER}\nold body\n{END_MARKER}\n\n"
        "# Bottom kept"
    )
    out = managed_block.merge(existing, "new body")
    assert "new body" in out
    assert "old body" not in out
    assert "# Top" in out
    assert "# Bottom kept" in out


def test_idempotent_across_runs():
    first = managed_block.merge(None, "body")
    second = managed_block.merge(first, "body")
    assert first == second


def test_idempotent_after_append():
    existing = "user content"
    first = managed_block.merge(existing, "body")
    second = managed_block.merge(first, "body")
    assert first == second
    # only one block ever
    assert first.count(START_MARKER) == 1
