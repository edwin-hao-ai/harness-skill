import pytest

from harness_gen.paths import PathSafetyError, safe_join


def test_safe_join_within_root(tmp_path):
    result = safe_join(tmp_path, "harness/platform/design.md")
    assert str(result).startswith(str(tmp_path.resolve()))
    assert result.name == "design.md"


def test_safe_join_rejects_traversal(tmp_path):
    with pytest.raises(PathSafetyError):
        safe_join(tmp_path, "../escape.md")


def test_safe_join_rejects_absolute(tmp_path):
    with pytest.raises(PathSafetyError):
        safe_join(tmp_path, "/etc/passwd")
