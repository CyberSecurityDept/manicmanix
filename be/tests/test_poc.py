import subprocess
import pytest


@pytest.fixture
def cli_output():
    result = subprocess.run(["./poc/linux/cli"], capture_output=True, text=True)
    return result.stdout


@pytest.fixture
def update_output():
    result = subprocess.run(["./poc/linux/update"], capture_output=True, text=True)
    return result.stdout


@pytest.fixture
def check_update_output():
    result = subprocess.run(
        ["./poc/linux/check-update"], capture_output=True, text=True
    )
    return result.stdout


def test_cli_output(cli_output):
    normalized_output = " ".join(cli_output.split())
    expected_string = (
        "CundamaniX - Comprehensive Uncovering and Network Data Analysis for "
        "Mobile Assessment and Network Investigation eXpert"
    )
    normalized_expected = " ".join(expected_string.split())

    assert (
        normalized_expected in normalized_output
    ), "The CLI output did not contain the expected string."


def test_update_output(update_output):
    normalized_output = " ".join(update_output.split())

    expected_string = (
        'Downloaded indicators "NSO Group Pegasus Indicators of Compromise"'
    )
    assert (
        expected_string in normalized_output
    ), f"Expected string '{expected_string}' not found in the update output."


def test_check_update_output(check_update_output):
    normalized_output = " ".join(check_update_output.split())
    expected_string = "Parsing STIX2 indicators file"

    assert (
        expected_string in normalized_output
    ), f"Expected string '{expected_string}' not found in the check-update output."
