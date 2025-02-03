"""Unit tests for checking the endpoint and secret."""

from unittest.mock import MagicMock, patch

import pytest
from botocore.exceptions import ClientError

from retrieve_endpoint import get_opensearch_endpoint, main


@pytest.fixture
def mock_boto3_client():
    """
    Fixture to mock the boto3 client.
    
    Returns:
        MagicMock: A mock object representing the boto3 client.

    Raises:
        None

    """
    with patch('boto3.client') as mock_client:
        yield mock_client

def test_get_opensearch_endpoint_success(mock_boto3_client, capsys):
    """
    Test successful retrieval of OpenSearch endpoint for the 'rag' domain.
    
    Args:
        mock_boto3_client (MagicMock): A pytest fixture that mocks the boto3 client.
        capsys (pytest.CaptureFixture): A pytest fixture for capturing stdout and stderr.

    Returns:
        None

    Raises:
        AssertionError: If any of the assertions fail.

    """
    # Arrange
    domain_name = 'rag'
    region = 'eu-central-1'
    expected_endpoint = f'search-{domain_name}-abcdef123456.{region}.es.amazonaws.com'
    mock_es_client = MagicMock()
    mock_boto3_client.return_value = mock_es_client
    mock_es_client.describe_elasticsearch_domain.return_value = {
        'DomainStatus': {'Endpoint': expected_endpoint}
    }

    # Act
    result = get_opensearch_endpoint(domain_name, region)

    # Assert
    assert result == expected_endpoint
    assert result.startswith(f'search-{domain_name}')
    assert result.endswith(f'{region}.es.amazonaws.com')
    captured = capsys.readouterr()
    assert f"Attempting to describe OpenSearch domain: {domain_name}" in captured.out
    assert "Domain description retrieved successfully" in captured.out
    assert f"Endpoint: {expected_endpoint}" in captured.out

def test_get_opensearch_endpoint_no_endpoint(mock_boto3_client, capsys):
    """
    Test behavior when no endpoint is found for the 'rag' domain.
    
    Args:
        mock_boto3_client (MagicMock): A pytest fixture that mocks the boto3 client.
        capsys (pytest.CaptureFixture): A pytest fixture for capturing stdout and stderr.

    Returns:
        None

    Raises:
        AssertionError: If any of the assertions fail.

    """
    # Arrange
    domain_name = 'rag'
    region = 'eu-central-1'
    mock_es_client = MagicMock()
    mock_boto3_client.return_value = mock_es_client
    mock_es_client.describe_elasticsearch_domain.return_value = {
        'DomainStatus': {}  # No endpoint in response
    }

    # Act
    result = get_opensearch_endpoint(domain_name, region)

    # Assert
    assert result is None
    captured = capsys.readouterr()
    assert "No endpoint found for the domain." in captured.err

def test_get_opensearch_endpoint_client_error(mock_boto3_client, capsys):
    """
    Test handling of ClientError exception for the 'rag' domain.
    
    Args:
        mock_boto3_client (MagicMock): A pytest fixture that mocks the boto3 client.
        capsys (pytest.CaptureFixture): A pytest fixture for capturing stdout and stderr.

    Returns:
        None

    Raises:
        AssertionError: If any of the assertions fail.

    """
    # Arrange
    domain_name = 'rag'
    region = 'eu-central-1'
    mock_es_client = MagicMock()
    mock_boto3_client.return_value = mock_es_client
    mock_es_client.describe_elasticsearch_domain.side_effect = ClientError(
        {'Error': {'Code': 'ResourceNotFoundException', 'Message': 'Domain not found'}},
        'DescribeElasticsearchDomain'
    )

    # Act
    result = get_opensearch_endpoint(domain_name, region)

    # Assert
    assert result is None
    captured = capsys.readouterr()
    assert "ClientError:" in captured.err

def test_get_opensearch_endpoint_general_exception(mock_boto3_client, capsys):
    """
    Test handling of general exceptions for the 'rag' domain.
    
    Args:
        mock_boto3_client (MagicMock): A pytest fixture that mocks the boto3 client.
        capsys (pytest.CaptureFixture): A pytest fixture for capturing stdout and stderr.

    Returns:
        None

    Raises:
        AssertionError: If any of the assertions fail.

    """
    # Arrange
    domain_name = 'rag'
    region = 'eu-central-1'
    mock_es_client = MagicMock()
    mock_boto3_client.return_value = mock_es_client
    mock_es_client.describe_elasticsearch_domain.side_effect = Exception("Unexpected error")

    # Act
    result = get_opensearch_endpoint(domain_name, region)

    # Assert
    assert result is None
    captured = capsys.readouterr()
    assert "An error occurred during script execution:" in captured.err

@pytest.mark.parametrize("secret_name,region,endpoint,expected", [
    ("rag-test", "eu-central-1", "search-rag-abcdef123456.eu-central-1.es.amazonaws.com", True),
    ("rag-non-existent", "eu-central-1", None, False),
])
def test_main_function(mock_boto3_client, capsys, secret_name, region, endpoint, expected):
    """
    Test the main function with various scenarios for the 'rag' domain.
    
    This parameterized test verifies the behavior of the main function
    under different conditions:
    1. Successful endpoint retrieval for different secret names
    2. Failed endpoint retrieval for a non-existent secret
    
    It checks that the function returns the expected boolean result,
    prints appropriate messages to stdout or stderr, and ensures the
    endpoint format is correct when successful.
    
    Args:
        mock_boto3_client (MagicMock): A pytest fixture that mocks the boto3 client.
        capsys (pytest.CaptureFixture): A pytest fixture for capturing stdout and stderr.
        secret_name (str): Name of the secret being tested (starts with 'rag').
        region (str): AWS region being tested.
        endpoint (str or None): Mocked endpoint (or None for failure case).
        expected (bool): Expected boolean return value of the main function.

    Returns:
        None

    Raises:
        AssertionError: If any of the assertions fail.

    """
    # Arrange
    domain_name = 'rag'
    mock_es_client = MagicMock()
    mock_boto3_client.return_value = mock_es_client
    if endpoint:
        mock_es_client.describe_elasticsearch_domain.return_value = {
            'DomainStatus': {'Endpoint': endpoint}
        }
    else:
        mock_es_client.describe_elasticsearch_domain.side_effect = ClientError(
            {'Error': {'Code': 'ResourceNotFoundException', 'Message': 'Domain not found'}},
            'DescribeElasticsearchDomain'
        )

    # Act
    result = main(domain_name, region)

    # Assert
    assert result == expected
    captured = capsys.readouterr()
    if expected:
        assert endpoint.startswith(f'search-{domain_name}')
        assert endpoint.endswith(f'{region}.es.amazonaws.com')
        assert f"Attempting to describe OpenSearch domain: {domain_name}" in captured.out
        assert "Domain description retrieved successfully" in captured.out
        assert f"Endpoint: {endpoint}" in captured.out
        assert "Script executed successfully" in captured.out
    else:
        if endpoint is None:
            assert "ClientError:" in captured.err
        assert "No endpoint returned." in captured.err or "An error occurred during script execution:" in captured.err

    # Additional check for secret name
    assert secret_name.startswith('rag')
