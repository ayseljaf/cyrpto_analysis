"""Test DAG structure and configuration."""
import pytest
from airflow.models import DagBag


class TestCryptoPipelineDAG:
    """Test crypto_analysis_pipeline DAG."""
    
    @pytest.fixture(scope="class")
    def dagbag(self):
        """Load DAG bag."""
        return DagBag(dag_folder='dags/', include_examples=False)

    @staticmethod
    def _get_dag(dagbag):
        return dagbag.dags["crypto_analysis_pipeline"]
    
    def test_dag_loaded(self, dagbag):
        """Test DAG is loaded without errors."""
        assert dagbag.import_errors == {}, \
            f"DAG import errors: {dagbag.import_errors}"
        assert 'crypto_analysis_pipeline' in dagbag.dags, \
            "crypto_analysis_pipeline DAG should be loaded"
    
    def test_dag_configuration(self, dagbag):
        """Test DAG configuration."""
        dag = self._get_dag(dagbag)

        schedule = str(getattr(dag, "schedule", "") or getattr(dag, "schedule_interval", ""))
        assert "0 18 * * *" in schedule, "Schedule should be daily at 18:00 UTC"
        assert dag.catchup is False, "Catchup should be disabled"
        assert dag.max_active_runs == 1, "Max active runs should be 1"
        assert 'crypto' in dag.tags, "Should have 'crypto' tag"
        assert 'etl' in dag.tags, "Should have 'etl' tag"
        assert 'production' in dag.tags, "Should have 'production' tag"
    
    def test_dag_has_required_tasks(self, dagbag):
        """Test DAG has all required tasks."""
        dag = self._get_dag(dagbag)
        task_ids = [task.task_id for task in dag.tasks]
        
        required_tasks = [
            'get_crypto_pairs',
            'extract_crypto_data',
            'check_extracted_data',
            'verify_data_loaded',
            'calculate_monthly_statistics',
            'calculate_weekly_price_changes',
            'calculate_overall_statistics',
            'validate_monthly_stats',
            'update_pipeline_metadata'
        ]
        
        for task_id in required_tasks:
            assert task_id in task_ids, f"Task '{task_id}' should exist"
    
    def test_task_dependencies(self, dagbag):
        """Test task dependencies are correct."""
        dag = self._get_dag(dagbag)
        
        # Test get_crypto_pairs has no upstream
        get_pairs = dag.get_task('get_crypto_pairs')
        assert len(get_pairs.upstream_task_ids) == 0, \
            "get_crypto_pairs should have no upstream tasks"
        
        # Test extract depends on get_crypto_pairs
        extract = dag.get_task('extract_crypto_data')
        assert 'get_crypto_pairs' in extract.upstream_task_ids, \
            "extract_crypto_data should depend on get_crypto_pairs"
        
        # Test check_extracted_data depends on extract
        check_data = dag.get_task('check_extracted_data')
        assert 'extract_crypto_data' in check_data.upstream_task_ids, \
            "check_extracted_data should depend on extract_crypto_data"
        
        # Test verify_data_loaded depends on check_extracted_data
        verify = dag.get_task('verify_data_loaded')
        assert 'check_extracted_data' in verify.upstream_task_ids, \
            "verify_data_loaded should depend on check_extracted_data"
    
    def test_dag_default_args(self, dagbag):
        """Test DAG default args."""
        dag = self._get_dag(dagbag)
        
        assert dag.default_args.get('retries') == 3, \
            "Should have 3 retries"
        assert 'retry_delay' in dag.default_args, \
            "Should have retry_delay configured"
        assert dag.default_args.get('retry_exponential_backoff') is True, \
            "Should have exponential backoff enabled"
        assert dag.default_args.get('owner') == 'airflow', \
            "Owner should be 'airflow'"
    
    def test_dag_uses_taskflow_api(self, dagbag):
        """Test DAG uses TaskFlow API decorators."""
        dag = self._get_dag(dagbag)
        
        # Check for decorated tasks
        taskflow_tasks = [
            'get_crypto_pairs',
            'extract_crypto_data',
            'calculate_monthly_statistics',
            'calculate_weekly_price_changes',
            'calculate_overall_statistics',
            'update_pipeline_metadata'
        ]
        
        for task_id in taskflow_tasks:
            task = dag.get_task(task_id)
            # TaskFlow tasks are PythonOperator instances
            assert task is not None, f"Task {task_id} should exist"
    
    def test_dag_has_data_quality_checks(self, dagbag):
        """Test DAG includes data quality checks."""
        dag = self._get_dag(dagbag)
        task_ids = [task.task_id for task in dag.tasks]
        
        quality_check_tasks = [
            'check_extracted_data',
            'validate_monthly_stats'
        ]
        
        for task_id in quality_check_tasks:
            assert task_id in task_ids, \
                f"Data quality check '{task_id}' should exist"
    
    def test_dag_has_sensor(self, dagbag):
        """Test DAG includes sensor for data verification."""
        dag = self._get_dag(dagbag)
        
        sensor_task = dag.get_task('verify_data_loaded')
        assert sensor_task is not None, "Sensor task should exist"
        
        # Check sensor mode is 'reschedule' for optimization
        assert sensor_task.mode == 'reschedule', \
            "Sensor should use 'reschedule' mode for optimization"
    
    def test_dag_start_date(self, dagbag):
        """Test DAG has correct start date."""
        dag = self._get_dag(dagbag)

        assert dag.start_date.year == 2024, "Start date year should be 2024"
        assert dag.start_date.month == 1, "Start date month should be January"
        assert dag.start_date.day == 1, "Start date day should be 1st"
        assert dag.timezone is not None, "DAG should have timezone configured"
        assert str(dag.timezone) == "UTC", "DAG timezone should be UTC"

    def test_dag_uses_refactored_pipeline_modules(self):
        """Test DAG imports pipeline logic from src package modules."""
        with open("dags/crypto_pipeline_dag.py", "r", encoding="utf-8") as dag_file:
            content = dag_file.read()
        assert "from pipeline.config import" in content
        assert "from pipeline import task_logic" in content
    
    def test_dag_has_documentation(self, dagbag):
        """Test DAG has documentation."""
        dag = self._get_dag(dagbag)
        
        assert dag.description is not None, "DAG should have description"
        assert len(dag.description) > 0, "Description should not be empty"
        assert dag.doc_md is not None, "DAG should have doc_md"
