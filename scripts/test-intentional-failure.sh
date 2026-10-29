#!/usr/bin/env sh
set -eu
echo "Expected result: this command fails to demonstrate the CI gate."
DEMO_FORCE_TEST_FAILURE=1 pytest -q tests/test_api.py::test_ci_failure_gate_opt_in
