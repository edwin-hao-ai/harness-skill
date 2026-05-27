import pytest

from harness_gen.model import InterviewResponse, ResponseError


def test_from_dict_parses_simple(simple_data):
    response = InterviewResponse.from_dict(simple_data)
    assert response.project.project_name == "TaskFlow"
    assert len(response.project.core_features) == 2
    assert response.architecture.architecture_pattern == "monolith"
    assert response.personality.voice_enabled is False
    assert response.prototype.output_format == "html"


def test_voice_personality(voice_data):
    response = InterviewResponse.from_dict(voice_data)
    assert response.personality.voice_enabled is True
    assert response.personality.tone == "friendly"
    assert response.personality.formality == 3


def test_missing_project_name_raises(simple_data):
    simple_data["projectExploration"]["projectName"] = ""
    with pytest.raises(ResponseError):
        InterviewResponse.from_dict(simple_data)


def test_unknown_pattern_raises(simple_data):
    simple_data["architecture"]["architecturePattern"] = "quantum"
    with pytest.raises(ResponseError):
        InterviewResponse.from_dict(simple_data)


def test_response_is_immutable(simple_data):
    response = InterviewResponse.from_dict(simple_data)
    with pytest.raises(Exception):
        response.project.project_name = "Mutated"  # type: ignore[misc]
