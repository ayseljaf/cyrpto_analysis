"""Test project structure and configuration."""
import os
import pytest
from pathlib import Path


class TestProjectStructure:
    """Test that all required directories and files exist."""
    
    def test_dags_directory_exists(self):
        """Test dags directory exists."""
        assert os.path.isdir('dags'), "dags/ directory should exist"
    
    def test_dags_tasks_directory_exists(self):
        """Test dags/tasks directory exists."""
        assert os.path.isdir('dags/tasks'), "dags/tasks/ directory should exist"
    
    def test_plugins_directory_exists(self):
        """Test plugins directory exists."""
        assert os.path.isdir('plugins'), "plugins/ directory should exist"
    
    def test_sql_directory_exists(self):
        """Test sql directory exists."""
        assert os.path.isdir('sql'), "sql/ directory should exist"
    
    def test_logs_directory_exists(self):
        """Test logs directory exists."""
        assert os.path.isdir('logs'), "logs/ directory should exist"
    
    def test_init_files_exist(self):
        """Test __init__.py files exist in Python packages."""
        init_files = [
            'dags/__init__.py',
            'dags/tasks/__init__.py',
            'plugins/__init__.py'
        ]
        for init_file in init_files:
            assert os.path.isfile(init_file), f"{init_file} should exist"
    
    def test_sql_migration_file_exists(self):
        """Test SQL migration file exists."""
        assert os.path.isfile('sql/create_analysis_tables.sql'), \
            "sql/create_analysis_tables.sql should exist"

    def test_streaming_sql_migration_file_exists(self):
        """Test streaming SQL migration file exists."""
        assert os.path.isfile('sql/create_streaming_tables.sql'), \
            "sql/create_streaming_tables.sql should exist"

    def test_pipeline_module_files_exist(self):
        """Test refactored pipeline modules exist."""
        expected_files = [
            'src/pipeline/__init__.py',
            'src/pipeline/config.py',
            'src/pipeline/sql_queries.py',
            'src/pipeline/task_logic.py',
        ]
        for file_path in expected_files:
            assert os.path.isfile(file_path), f"{file_path} should exist"
    
    def test_requirements_airflow_exists(self):
        """Test requirements-airflow.txt exists."""
        assert os.path.isfile('requirements-airflow.txt'), \
            "requirements-airflow.txt should exist"
    
    def test_env_example_exists(self):
        """Test .env.example exists."""
        assert os.path.isfile('include/.env.example'), \
            "include/.env.example should exist"
    
    def test_env_example_has_fernet_key(self):
        """Test .env.example has Fernet key configured."""
        with open('include/.env.example', 'r') as f:
            content = f.read()
            assert 'AIRFLOW_FERNET_KEY=' in content, \
                "AIRFLOW_FERNET_KEY should be in .env.example"
            assert 'REPLACE_WITH_GENERATED_KEY' not in content, \
                "Fernet key should be generated, not placeholder"
