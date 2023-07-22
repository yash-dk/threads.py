import pytest
from threadspy import ThreadsApi
from dotenv import load_dotenv
import os
import time

@pytest.fixture(scope="session")
def threads_api():
    # Initialize the ThreadsApi instance with test-specific configurations
    load_dotenv()
    
    return ThreadsApi(username=os.getenv('IG_USERNAME'), password=os.getenv('IG_PASSWORD'))

@pytest.fixture(autouse=True)
def slow_down_tests():
    yield
    time.sleep(5)
