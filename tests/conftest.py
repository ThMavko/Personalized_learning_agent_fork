import copy
import json
import os
import sys

import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "src"))


@pytest.fixture
def state():
    """Copia dello stato reale di esempio, modificabile senza effetti collaterali."""
    with open(os.path.join(ROOT, "data", "curriculum_state.json"), encoding="utf-8") as f:
        return copy.deepcopy(json.load(f))
