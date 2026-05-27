import pytest

from harness_gen.template import (
    TemplateError,
    find_residual_placeholders,
    render,
)


def test_render_substitutes_keys():
    out = render("Hello {{name}} from {{place}}", {"name": "A", "place": "B"})
    assert out == "Hello A from B"


def test_render_handles_spaced_placeholders():
    assert render("{{ name }}", {"name": "X"}) == "X"


def test_render_raises_on_missing_key():
    with pytest.raises(TemplateError) as exc:
        render("{{present}} {{missing}}", {"present": "ok"})
    assert "missing" in str(exc.value)


def test_find_residual_placeholders():
    assert find_residual_placeholders("clean text") == []
    assert find_residual_placeholders("a {{x}} b {{y}}") == ["{{x}}", "{{y}}"]
