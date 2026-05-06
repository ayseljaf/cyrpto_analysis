"""Shared pytest configuration and fixtures."""
import pytest
import os
from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).parent.parent

# Ensure Airflow writes only inside repository during tests.
TEST_AIRFLOW_HOME = PROJECT_ROOT / ".tmp" / "airflow_home"
TEST_AIRFLOW_LOGS = TEST_AIRFLOW_HOME / "logs"
TEST_AIRFLOW_HOME.mkdir(parents=True, exist_ok=True)
TEST_AIRFLOW_LOGS.mkdir(parents=True, exist_ok=True)
os.environ.setdefault("AIRFLOW_HOME", str(TEST_AIRFLOW_HOME))
os.environ.setdefault("AIRFLOW__LOGGING__BASE_LOG_FOLDER", str(TEST_AIRFLOW_LOGS))
os.environ.setdefault("AIRFLOW__CORE__LOAD_EXAMPLES", "False")


@pytest.fixture(scope="session")
def project_root():
    """Get project root directory."""
    return PROJECT_ROOT


@pytest.fixture(scope="session")
def test_data_dir(project_root):
    """Get test data directory."""
    return project_root / "tests" / "fixtures"


@pytest.fixture(autouse=True)
def setup_test_env():
    """Setup test environment variables."""
    os.environ['ENVIRONMENT'] = 'test'
    os.environ['POSTGRES_HOST'] = 'localhost'
    os.environ['POSTGRES_PORT'] = '5432'
    os.environ['POSTGRES_DB'] = 'crypto_db_test'
    os.environ['POSTGRES_USER'] = 'test_user'
    os.environ['POSTGRES_PASSWORD'] = 'test_password'
    yield
    # Cleanup after test


def pytest_configure(config):
    """Configure pytest with custom markers."""
    config.addinivalue_line(
        "markers", "integration: mark test as integration test"
    )
    config.addinivalue_line(
        "markers", "slow: mark test as slow running"
    )

SRC_PATH = PROJECT_ROOT / "src"
if str(SRC_PATH) not in sys.path:
    sys.path.insert(0, str(SRC_PATH))
