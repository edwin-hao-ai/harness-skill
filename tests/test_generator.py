import pytest

from harness_gen import generate
from harness_gen.managed_block import START_MARKER
from harness_gen.model import InterviewResponse
from harness_gen.template import find_residual_placeholders

V1_WHOLE_FILES = [
    "harness-map.md",
    "harness/platform/spec.md",
    "harness/platform/design.md",
    "harness/platform/architecture.md",
    "harness/domain/use-cases.md",
    "harness/application/project-structure.md",
    "harness/interface/user-guide.md",
    "memory/memory.md",
    "memory/decisions.md",
]
V1_ENTRY_FILES = ["AGENTS.md", "CLAUDE.md", ".cursor/rules/harness.mdc"]


def _generate(data, tmp_path, **kwargs):
    response = InterviewResponse.from_dict(data)
    return response, generate(response, root=tmp_path, **kwargs)


def test_generates_full_v1_set(simple_data, tmp_path):
    _, result = _generate(simple_data, tmp_path)
    assert result.ok
    for rel in V1_WHOLE_FILES + V1_ENTRY_FILES:
        assert (tmp_path / rel).exists(), f"missing {rel}"


def test_no_residual_placeholders(simple_data, tmp_path):
    _generate(simple_data, tmp_path)
    for path in tmp_path.rglob("*.md"):
        assert find_residual_placeholders(path.read_text(encoding="utf-8")) == []


def test_voice_doc_only_when_enabled(simple_data, voice_data, tmp_path):
    _generate(simple_data, tmp_path / "novoice")
    assert not (tmp_path / "novoice" / "harness/platform/voice.md").exists()

    _generate(voice_data, tmp_path / "voice")
    assert (tmp_path / "voice" / "harness/platform/voice.md").exists()


def test_content_reflects_interview(simple_data, tmp_path):
    _generate(simple_data, tmp_path)
    # Product requirements (features) live in spec.md, not design.md.
    spec = (tmp_path / "harness/platform/spec.md").read_text(encoding="utf-8")
    assert "TaskFlow" in spec
    assert "任务看板" in spec
    # design.md is the engineering design doc (constraints), not a feature list.
    design = (tmp_path / "harness/platform/design.md").read_text(encoding="utf-8")
    assert "TaskFlow" in design
    assert "约束程度" in design
    use_cases = (tmp_path / "harness/domain/use-cases.md").read_text(encoding="utf-8")
    assert "任务看板" in use_cases  # use-case mapping for each feature


def test_skips_existing_without_force(simple_data, tmp_path):
    target = tmp_path / "harness/platform/design.md"
    target.parent.mkdir(parents=True)
    target.write_text("USER CONTENT", encoding="utf-8")

    _, result = _generate(simple_data, tmp_path)
    assert "harness/platform/design.md" in result.skipped
    assert target.read_text(encoding="utf-8") == "USER CONTENT"


def test_force_overwrites_existing(simple_data, tmp_path):
    target = tmp_path / "harness/platform/design.md"
    target.parent.mkdir(parents=True)
    target.write_text("USER CONTENT", encoding="utf-8")

    _, result = _generate(simple_data, tmp_path, force=True)
    assert "harness/platform/design.md" in result.updated
    assert "USER CONTENT" not in target.read_text(encoding="utf-8")


def test_entry_files_preserve_user_content(simple_data, tmp_path):
    agents = tmp_path / "AGENTS.md"
    agents.write_text("# My rules\n\nkeep this", encoding="utf-8")

    _generate(simple_data, tmp_path)
    text = agents.read_text(encoding="utf-8")
    assert "# My rules" in text
    assert "keep this" in text
    assert START_MARKER in text


def test_regeneration_is_idempotent_for_entry_files(simple_data, tmp_path):
    _generate(simple_data, tmp_path)
    first = (tmp_path / "AGENTS.md").read_text(encoding="utf-8")
    _generate(simple_data, tmp_path)  # second run
    second = (tmp_path / "AGENTS.md").read_text(encoding="utf-8")
    assert first == second
    assert second.count(START_MARKER) == 1


def test_harness_map_lists_layers(simple_data, tmp_path):
    _generate(simple_data, tmp_path)
    harness_map = (tmp_path / "harness-map.md").read_text(encoding="utf-8")
    assert "Platform Layer" in harness_map
    assert "Memory Layer" in harness_map
    assert "harness/platform/design.md" in harness_map


def test_missing_template_dir_records_failure(simple_data, tmp_path):
    _, result = _generate(simple_data, tmp_path, templates_dir=tmp_path / "nope")
    assert not result.ok
    assert len(result.failed) > 0
