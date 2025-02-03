"""File to check the content of the Opensearch Index."""

import json
import os
import sys

from loguru import logger
from opensearchpy import OpenSearch, RequestsHttpConnection

from retrieve_endpoint import get_opensearch_endpoint
from retrieve_secret import get_secret

# Loguru logger
logger.remove()
logger.add(sys.stdout, level=os.getenv("LOG_LEVEL", "INFO"))

def get_opensearch_client(host, username, password):
    """
    Create and return an OpenSearch client.

    Args:
        host (str): The host URL of the OpenSearch cluster.
        username (str): The username for authentication.
        password (str): The password for authentication.

    Returns:
        OpenSearch: An instance of the OpenSearch client.

    """
    logger.info(f"Creating OpenSearch client for host: {host}")
    return OpenSearch(
        hosts = [{'host': host, 'port': 443}],
        http_auth = (username, password),
        use_ssl = True,
        verify_certs = True,
        connection_class = RequestsHttpConnection,
        timeout=30
    )

def check_index_content(client, index_name):
    """
    Check and display content of the specified index.

    This function retrieves and displays index statistics, mapping, and sample documents.

    Args:
        client (OpenSearch): The OpenSearch client instance.
        index_name (str): The name of the index to check.

    Raises:
        Exception: If there's an error retrieving index information.

    """
    try:
        # Get index stats
        stats = client.indices.stats(index=index_name)
        logger.info(f"Index stats for '{index_name}':")
        logger.info(f"  Total documents: {stats['indices'][index_name]['total']['docs']['count']}")
        logger.info(f"  Total size: {stats['indices'][index_name]['total']['store']['size_in_bytes']} bytes")

        # Get mapping
        mapping = client.indices.get_mapping(index=index_name)
        logger.info("\nIndex mapping:")
        logger.info(json.dumps(mapping, indent=2))

        # Sample documents
        search_results = client.search(index=index_name, body={"query": {"match_all": {}}, "size": 5})
        logger.info("\nSample documents (up to 5):")
        for hit in search_results['hits']['hits']:
            logger.info(json.dumps(hit['_source'], indent=2))
    except Exception as e:
        logger.error(f"Error checking index content: {str(e)}")
        raise

if __name__ == "__main__":
    """
    Main execution block of the script.

    This block sets up the OpenSearch client using configuration from imported modules,
    then proceeds to check and display the content of the specified index.
    """
    # Domain Values
    region = "eu-central-1"  
    index_name = "rag"  
    username = "rag"    
    domain_name = "rag" 
    
    try:
        host = get_opensearch_endpoint(domain_name, region)
        logger.info(f"Retrieved OpenSearch endpoint: {host}")

        password = get_secret()
        logger.info("Retrieved secret successfully")

        client = get_opensearch_client(host, username, password)
        check_index_content(client, index_name)

        logger.info("Script execution completed successfully")
    except Exception as e:
        logger.error(f"An error occurred during script execution: {str(e)}")
        sys.exit(1)
