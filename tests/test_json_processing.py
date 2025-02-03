"""Unit tests for the JSON document."""

import json
import os
from unittest.mock import MagicMock, patch

import boto3
import pytest
from botocore.exceptions import NoCredentialsError

from generate_embeddings import create_embeddings

# Path to the document
DOCUMENT_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'text_with_embeddings.json')

@pytest.fixture
def sample_json_data():
    """
    Create a sample JSON data for testing.

    Returns:
        list: A list of dictionaries representing pages with text

    """
    return [
        {"page_number": 1, "text": "This is a test JSON document."},
        {"page_number": 2, "text": "It has multiple pages."}
    ]

@pytest.fixture
def mock_bedrock_client():
    """
    Create a mock Bedrock client for testing.

    Returns:
        MagicMock: A mock object representing the Bedrock client

    """
    with patch('boto3.client') as mock_client:
        mock_bedrock = MagicMock()
        mock_response = {
            'body': MagicMock(),
            'contentType': 'application/json',
        }
        mock_response['body'].read.return_value = b'{"embedding": [0.1, 0.2, 0.3]}'
        mock_bedrock.invoke_model.return_value = mock_response
        mock_client.return_value = mock_bedrock
        yield mock_bedrock

def test_create_embeddings(sample_json_data, mock_bedrock_client):
    """
    Test the create_embeddings function with sample JSON data.

    Args:
        sample_json_data (list): Sample JSON data
        mock_bedrock_client (MagicMock): Mock Bedrock client

    Raises:
        AssertionError: If any of the assertions fail

    """
    model_id = "amazon.titan-embed-text-v1"
    pages_with_embeddings = create_embeddings(sample_json_data, mock_bedrock_client, model_id)

    assert len(pages_with_embeddings) == len(sample_json_data)
    for page in pages_with_embeddings:
        assert "vector_field" in page, "vector_field is missing from page with embeddings"
        assert isinstance(page["vector_field"], list), "vector_field should be a list"
        assert page["vector_field"] == [0.1, 0.2, 0.3], "Unexpected embedding values"

    assert mock_bedrock_client.invoke_model.call_count == len(sample_json_data), "Bedrock client not called for each page"
    
    for call_args in mock_bedrock_client.invoke_model.call_args_list:
        kwargs = call_args[1]
        assert kwargs['modelId'] == model_id
        assert 'body' in kwargs
        assert kwargs['contentType'] == 'application/json'

def test_process_real_json_document():
    """
    Test processing the real JSON document.

    Raises:
        AssertionError: If any of the assertions fail

    """
    assert os.path.exists(DOCUMENT_PATH), f"The file {DOCUMENT_PATH} does not exist"

    with open(DOCUMENT_PATH, 'r') as file:
        data = json.load(file)

    assert isinstance(data, list), "JSON data should be a list"
    assert len(data) > 0, "JSON data is empty"
    
    for item in data:
        assert "page_number" in item, "page_number is missing from JSON item"
        assert "text" in item, "text is missing from JSON item"
        assert isinstance(item["page_number"], int), "page_number should be an integer"
        assert isinstance(item["text"], str), "text should be a string"
        assert len(item["text"]) > 0, f"Text is empty for page {item['page_number']}"

    # Add specific content checks based on your document
    assert any("react" in item["text"].lower() for item in data), "Expected phrase not found in document"

@pytest.mark.integration
def test_create_embeddings_with_real_document(mock_bedrock_client):
    """
    Integration test for create_embeddings function with the real JSON document.

    Args:
        mock_bedrock_client (MagicMock): Mock Bedrock client

    Raises:
        AssertionError: If any of the assertions fail

    """
    assert os.path.exists(DOCUMENT_PATH), f"The file {DOCUMENT_PATH} does not exist"

    with open(DOCUMENT_PATH, 'r') as file:
        data = json.load(file)

    model_id = "amazon.titan-embed-text-v1"
    pages_with_embeddings = create_embeddings(data, mock_bedrock_client, model_id)

    assert len(pages_with_embeddings) == len(data), "Number of pages with embeddings doesn't match original data count"
    
    for page in pages_with_embeddings:
        assert "vector_field" in page, "vector_field is missing from page with embeddings"
        assert isinstance(page["vector_field"], list), "vector_field should be a list"
        assert page["vector_field"] == [0.1, 0.2, 0.3], "Unexpected embedding values"

    assert mock_bedrock_client.invoke_model.call_count == len(data), "Bedrock client not called for each page"
    
    for call_args in mock_bedrock_client.invoke_model.call_args_list:
        kwargs = call_args[1]
        assert kwargs['modelId'] == model_id
        assert 'body' in kwargs
        assert kwargs['contentType'] == 'application/json'

@pytest.mark.integration
def test_create_embeddings_with_real_document_and_aws():
    """
    Full integration test for create_embeddings function with the real JSON document and AWS.

    Raises:
        pytest.skip: If no AWS credentials are found
        AssertionError: If any of the assertions fail

    """
    try:
        client = boto3.client("bedrock-runtime", region_name="eu-central-1")
    except NoCredentialsError:
        pytest.skip("No AWS credentials found for Bedrock client")

    assert os.path.exists(DOCUMENT_PATH), f"The file {DOCUMENT_PATH} does not exist"

    with open(DOCUMENT_PATH, 'r') as file:
        data = json.load(file)

    model_id = "amazon.titan-embed-text-v1"
    pages_with_embeddings = create_embeddings(data, client, model_id)

    assert len(pages_with_embeddings) == len(data), "Number of pages with embeddings doesn't match original data count"
    
    for page in pages_with_embeddings:
        assert "vector_field" in page, "vector_field is missing from page with embeddings"
        assert isinstance(page["vector_field"], list), "vector_field should be a list"
        assert len(page["vector_field"]) > 0, "vector_field is empty"
        assert all(isinstance(value, float) for value in page["vector_field"]), "Embedding values should be floats"

    print(f"Successfully created embeddings for {len(data)} pages from the real document.")
