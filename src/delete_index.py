"""File to delete the Opensearch Index."""

import os
import sys

from loguru import logger
from opensearchpy import OpenSearch, RequestsHttpConnection

from retrieve_endpoint import get_opensearch_endpoint
from retrieve_secret import get_secret

# logger configuration
logger.remove()
logger.add(sys.stdout, level=os.getenv("LOG_LEVEL", "INFO"))

def get_opensearch_cluster_client(domain_name, host, username, password):
    """
    Create and return an OpenSearch client for the specified cluster.

    Args:
        domain_name (str): The name of the OpenSearch domain.
        host (str): The host URL of the OpenSearch cluster.
        username (str): The username for authentication.
        password (str, optional): The password for authentication. Defaults to a preset value.

    Returns:
        OpenSearch: An instance of the OpenSearch client.

    """
    opensearch_client = OpenSearch(
        hosts = [{'host': host, 'port': 443}],
        http_auth = (username, password),
        use_ssl = True,
        verify_certs = True,
        connection_class = RequestsHttpConnection,
        timeout=30
    )
    return opensearch_client

def delete_opensearch_index(opensearch_client, index_name):
    """
    Delete a specific index from the OpenSearch cluster.

    Args:
        opensearch_client (OpenSearch): The OpenSearch client instance.
        index_name (str): The name of the index to delete.

    Returns:
        bool: True if the index was successfully deleted, False otherwise.

    """
    logger.info(f"Trying to delete index {index_name}")
    try:
        response = opensearch_client.indices.delete(index=index_name)
        logger.info(f"Index {index_name} deleted")
        return response['acknowledged']
    except Exception as e:
        logger.error(f"Error deleting index {index_name}: {str(e)}")
        return False

def list_all_indices(opensearch_client):
    """
    List all indices in the OpenSearch cluster.

    Args:
        opensearch_client (OpenSearch): The OpenSearch client instance.

    Returns:
        list: A list of all index names in the cluster.

    """
    try:
        indices = opensearch_client.indices.get_alias("*")
        return list(indices.keys())
    except Exception as e:
        logger.error(f"Error listing indices: {str(e)}")
        return []

def delete_all_indices(opensearch_client):
    """
    Delete all non-system indices in the OpenSearch cluster.

    This function lists all indices, skips system indices (those starting with '.'),
    and attempts to delete each non-system index.

    Args:
        opensearch_client (OpenSearch): The OpenSearch client instance.

    """
    indices = list_all_indices(opensearch_client)
    logger.info(f"Found {len(indices)} indices")

    for index in indices:
        if index.startswith('.'):
            logger.info(f"Skipping system index: {index}")
            continue
        success = delete_opensearch_index(opensearch_client, index)
        if not success:
            logger.warning(f"Failed to delete index: {index}")

    remaining_indices = list_all_indices(opensearch_client)
    logger.info(f"Remaining indices after deletion: {remaining_indices}")

if __name__ == "__main__":
    """
    Main execution block of the script.

    This block sets up the OpenSearch client using environment variables and
    configuration from imported modules, then proceeds to delete all non-system
    indices in the specified OpenSearch cluster.
    """
    domain_name = "rag"
    region = "eu-central-1"  
    username = "rag"    
    password = get_secret()
    host = get_opensearch_endpoint(domain_name, region)
    
    client = get_opensearch_cluster_client(domain_name, host, username, password)
    
    delete_all_indices(client)

    logger.info("Script execution completed")
