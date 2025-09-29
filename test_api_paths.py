# test_api_paths.py
import pytest
from collections import namedtuple

from graph_builder import build_dependency_graph
from path_generator import generate_valid_paths, generate_invalid_paths
from test_executor import TestExecutor

# --- Configuration ---
API_BASE_URL = "http://127.0.0.1:8000"
MAX_DEPTH = 3
NUM_VALID_PATHS = 3
NUM_INVALID_PATHS = 3

# A simple structure to hold test case information
TestCase = namedtuple("TestCase", ["path", "use_invalid_data", "expected_status", "description"])


def generate_test_cases():
    """Generates all test cases for parametrization."""
    graph, api_config = build_dependency_graph()
    all_cases = []

    # 1. Generate valid paths with valid data (should pass)
    valid_paths = generate_valid_paths(graph, MAX_DEPTH, NUM_VALID_PATHS)
    for path in valid_paths:
        description = f"VALID_PATH | {' -> '.join(path)} | valid_data"
        all_cases.append(TestCase(path, False, "PASSED", description))

    # 2. Generate valid paths but use invalid data (should fail)
    for path in valid_paths:
        description = f"VALID_PATH | {' -> '.join(path)} | invalid_data"
        all_cases.append(TestCase(path, True, "FAILED", description))

    # 3. Generate invalid paths (should fail)
    invalid_paths = generate_invalid_paths(graph, MAX_DEPTH, NUM_INVALID_PATHS)
    for path in invalid_paths:
        description = f"INVALID_PATH | {' -> '.join(path)}"
        all_cases.append(TestCase(path, False, "FAILED", description))

    return all_cases


# Use parametrize to create a test for each generated case
@pytest.mark.parametrize("test_case", generate_test_cases())
def test_api_path(api_server, test_case):
    """
    A single test function that is run for each generated TestCase.
    The `api_server` fixture ensures the mock API is running.
    """
    print(f"\n≈ {test_case.description}")

    _, api_config = build_dependency_graph()
    executor = TestExecutor(API_BASE_URL, api_config)

    result = executor.run_test_path(test_case.path, use_invalid_data=test_case.use_invalid_data)

    assert result["status"] == test_case.expected_status
