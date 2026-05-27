"""Make the bundled generator package importable from tests."""

import json
import sys
from pathlib import Path

import pytest

_SCRIPTS = Path(__file__).resolve().parent.parent / "skills" / "harness-skill" / "scripts"
sys.path.insert(0, str(_SCRIPTS))

FIXTURES = Path(__file__).resolve().parent / "fixtures"


@pytest.fixture
def simple_data() -> dict:
    return json.loads((FIXTURES / "simple-response.json").read_text(encoding="utf-8"))


@pytest.fixture
def voice_data() -> dict:
    return json.loads((FIXTURES / "voice-response.json").read_text(encoding="utf-8"))
