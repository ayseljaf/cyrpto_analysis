import os

import pytest


@pytest.mark.integration
@pytest.mark.skipif(
    os.getenv("RUN_STREAMING_INTEGRATION") != "1",
    reason="Set RUN_STREAMING_INTEGRATION=1 to run Kafka->DB integration test",
)
def test_kafka_to_db_flow_placeholder():
    """Integration entry point for local Kafka+Timescale smoke runs."""
    assert True
