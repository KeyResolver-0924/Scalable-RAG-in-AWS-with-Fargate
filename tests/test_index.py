"""Unit tests for the Index Creation."""

from unittest.mock import MagicMock, patch

import pytest
from opensearchpy import OpenSearch, RequestsHttpConnection

from create_index import create_index
from retrieve_endpoint import get_opensearch_endpoint
from retrieve_secret import get_secret


@pytest.fixture
def mock_opensearch_client():
    """
    Create a mock Opensearch client for testing.

    Returns:
        MagicMock: A mock object representing the Opensearch client

    """
    with patch('create_index.OpenSearch') as mock_opensearch:
        mock_client = MagicMock()
        mock_opensearch.return_value = mock_client
        yield mock_client

def test_create_index(mock_opensearch_client):
    """
    Test the create_index function to ensure it creates an index successfully.

    This test mocks the OpenSearch client and verifies that the index creation
    method is called with the correct parameters.

    Args:
        mock_opensearch_client (MagicMock): A mock object for the OpenSearch client.

    Raises:
        AssertionError: If any of the assertions fail.

    """
    # Arrange
    host = 'test-host'
    index_name = 'test-index'
    username = 'test-user'
    password = 'test-password'

    # Set up the mock response
    mock_response = {'acknowledged': True, 'shards_acknowledged': True, 'index': index_name}
    mock_opensearch_client.indices.create.return_value = mock_response

    # Act
    create_index(host, index_name, username, password)

    # Assert
    mock_opensearch_client.indices.create.assert_called_once()
    
    # Check if the index creation method was called with the correct parameters
    call_args = mock_opensearch_client.indices.create.call_args
    assert call_args[0][0] == index_name
    assert 'body' in call_args[1]
    
    # Check if the index body contains the expected settings and mappings
    index_body = call_args[1]['body']
    assert 'settings' in index_body
    assert 'mappings' in index_body
    assert index_body['settings']['index']['number_of_shards'] == 3
    assert index_body['settings']['index']['number_of_replicas'] == 2
    assert index_body['settings']['index']['knn'] is True
    assert index_body['mappings']['properties']['vector_field']['type'] == 'knn_vector'
    assert index_body['mappings']['properties']['vector_field']['dimension'] == 1536

@pytest.mark.integration
def test_index_exists_after_creation():
    """
    Integration test to verify that the index exists after creation.

    This test creates an actual connection to OpenSearch and verifies
    that the index exists after calling the create_index function.

    Note: This test requires actual OpenSearch credentials and will make
    a real connection. Use with caution.

    Raises:
        AssertionError: If the index does not exist after creation.

    """
    # Arrange
    domain_name="rag"
    region = "eu-central-1"  
    host = get_opensearch_endpoint(domain_name, region)
    index_name = "rag-test"
    username = "rag"
    password = get_secret()


    # Act
    create_index(host, index_name, username, password)

    # Assert
    client = OpenSearch(
        hosts = [{'host': host, 'port': 443}],
        http_auth = (username, password),
        use_ssl = True,
        verify_certs = True,
        connection_class = RequestsHttpConnection
    )

    assert client.indices.exists(index=index_name), f"Index '{index_name}' does not exist after creation"

    # Clean up - delete the test index
    client.indices.delete(index=index_name)
