from pathlib import Path

import validate
from harness_gen import generate
from harness_gen.model import InterviewResponse

SKILL_DIR = Path(__file__).resolve().parent.parent / "skills" / "harness-skill"


def test_validate_skill_passes_on_real_skill():
    assert validate.validate_skill(SKILL_DIR) == []


def test_validate_skill_flags_name_mismatch(tmp_path):
    skill = tmp_path / "wrong-name"
    skill.mkdir()
    (skill / "SKILL.md").write_text(
        "---\nname: something-else\ndescription: x\n---\n", encoding="utf-8"
    )
    issues = validate.validate_skill(skill)
    assert any("不一致" in i for i in issues)


def test_validate_output_passes_on_generated_tree(simple_data, tmp_path):
    response = InterviewResponse.from_dict(simple_data)
    generate(response, root=tmp_path)
    assert validate.validate_output(tmp_path) == []


def test_validate_output_detects_residue(tmp_path):
    (tmp_path / "doc.md").write_text("# Title\n\n{{unfilled}}\n", encoding="utf-8")
    issues = validate.validate_output(tmp_path)
    assert any("占位符残留" in i for i in issues)


def test_validate_output_detects_dead_link(tmp_path):
    (tmp_path / "doc.md").write_text("# T\n\n[gone](missing.md)\n", encoding="utf-8")
    issues = validate.validate_output(tmp_path)
    assert any("死链" in i for i in issues)


def test_validate_output_detects_empty_doc(tmp_path):
    (tmp_path / "empty.md").write_text("", encoding="utf-8")
    issues = validate.validate_output(tmp_path)
    assert any("空文档" in i for i in issues)
