from pathlib import Path
import sys
import pytest
from fastapi.testclient import TestClient

# Ensure root directory is on sys.path
root_dir = Path(__file__).resolve().parent.parent.parent
if str(root_dir) not in sys.path:
  sys.path.insert(0, str(root_dir))

from backend.app.main import app


@pytest.fixture(scope="module")
def client():
  with TestClient(app) as c:
    yield c