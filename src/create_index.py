"""File to create the Opensearch Index."""

import os
import sys

import boto3
from loguru import logger
from opensearchpy import OpenSearch, RequestsHttpConnection

from retrieve_secret import get_secret, get_secret_name

# logger
logger.remove()
logger.add(sys.stdout, level=os.getenv("LOG_LEVEL", "INFO"))

def get_opensearch_endpoint(domain_name, region_name):
    """
    Retrieve the endpoint for an OpenSearch domain.

    Args:
        domain_name (str): The name of the OpenSearch domain.
        region_name (str): The AWS region where the domain is located.

    Returns:
        str: The endpoint URL for the OpenSearch domain.

    Raises:
        Exception: If there's an error retrieving the OpenSearch endpoint.

    """
    client = boto3.client('es', region_name=region_name)
    try:
        response = client.describe_elasticsearch_domain(DomainName=domain_name)
        return response['DomainStatus']['Endpoint']
    except Exception as e:
        logger.error(f"Error retrieving OpenSearch endpoint: {e}")
        raise

def create_index(host, index_name, username, password):
    """
    Create an index in OpenSearch with specified settings and mappings.

    This function creates an OpenSearch client and uses it to create an index
    with predefined settings for shards, replicas, and KNN, as well as 
    mappings for text and vector fields.

    Args:
        host (str): The OpenSearch host URL.
        index_name (str): The name of the index to create.
        username (str): The username for OpenSearch authentication.
        password (str): The password for OpenSearch authentication.

    Raises:
        Exception: If there's an error creating the index.

    """
    # Create the OpenSearch client
    client = OpenSearch(
        hosts = [{'host': host, 'port': 443}],
        http_auth = (username, password),
        use_ssl = True,
        verify_certs = True,
        connection_class = RequestsHttpConnection,
        timeout=30
    )

    # Define the index settings and mappings
    index_body = {
        "settings": {
            "index": {
                "number_of_shards": 3,
                "number_of_replicas": 2,
                "knn": True,
                "knn.space_type": "cosinesimil"
            }
        },
        "mappings": {
            "properties": {
                "text": {
                    "type": "text",
                    "analyzer": "standard"
                },
                "vector_field": {
                    "type": "knn_vector",
                    "dimension": 1536,
                }
            }
        }
    }

    # Create the index
    try:
        response = client.indices.create(index_name, body=index_body)
        logger.info(f"Index '{index_name}' created successfully: {response}")
    except Exception as e:
        logger.error(f"Error creating index: {e}")
        raise

if __name__ == "__main__":
    """
    Main execution block of the script.

    This block retrieves necessary configuration information, gets the OpenSearch
    endpoint and password, and creates an index in OpenSearch. It handles exceptions
    and logs relevant information during the process.
    """

    region_name = "eu-central-1"  
    domain_name = "rag"      
    secret_name = get_secret_name(region_name, domain_name)  
    index_name = "rag"  
    username = "rag"  
    
    try:
        host = get_opensearch_endpoint(domain_name, region_name)
        logger.info(f"OpenSearch endpoint: {host}")

        password = get_secret()
        logger.info("Retrieved secret successfully")

        # Create the index
        create_index(host, index_name, username, password)

        logger.info("Script executed successfully")
    except Exception as e:
        logger.error(f"An error occurred during script execution: {e}")
