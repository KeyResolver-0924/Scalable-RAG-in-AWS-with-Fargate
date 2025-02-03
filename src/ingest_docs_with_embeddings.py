"""File to ingest documents in the Opensearch Index."""

import json
import os
import sys

import boto3
from loguru import logger
from opensearchpy import OpenSearch, RequestsHttpConnection

from retrieve_secret import get_secret

# logger configuration
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

def ingest_data(client, index_name, data):
    """
    Ingest data into the specified OpenSearch index.

    Args:
        client (OpenSearch): The OpenSearch client instance.
        index_name (str): The name of the index to ingest data into.
        data (list): A list of dictionaries containing the data to be ingested.

    Raises:
        ValueError: If the input data is not in the expected format.

    """
    if not isinstance(data, list):
        logger.error(f"Error: Expected a list of dictionaries, but got {type(data)}")
        logger.error(f"Data sample: {str(data)[:200]}...")  # Log first 200 characters of data
        raise ValueError("Invalid data format")

    for page in data:
        try:
            document = {
                "text": page.get('text'),  
                "vector_field": page.get('vector_field')
            }

            response = client.index(
                index=index_name,
                body=document,
            )
            logger.info(f"Indexed page {page.get('page_number')}: {response['result']}")
        except Exception as e:
            logger.error(f"Error indexing page {page.get('page_number')}: {e}")
            logger.error(f"Problematic page data: {page}")

def main():
    """
    Main function to orchestrate the data ingestion process.

    This function retrieves necessary configuration, sets up the OpenSearch client,
    loads data from a JSON file, and ingests it into the specified OpenSearch index.
    """
    region_name = "eu-central-1"  
    domain_name = "rag"      
    index_name = "rag"  
    username = "rag"  
    
    try:
        # Get the OpenSearch endpoint
        host = get_opensearch_endpoint(domain_name, region_name)
        logger.info(f"OpenSearch endpoint: {host}")

        # Get the master password from Secrets Manager
        password = get_secret()

        client = OpenSearch(
            hosts = [{'host': host, 'port': 443}],
            http_auth = (username, password),
            use_ssl = True,
            verify_certs = True,
            connection_class = RequestsHttpConnection,
            timeout=30
        )

        # Load the data from the JSON file
        with open('../data/text_with_embeddings.json', 'r') as f:
            data = json.load(f)

        logger.info(f"Loaded data type: {type(data)}")
        if isinstance(data, list) and len(data) > 0:
            logger.info(f"First item keys: {', '.join(data[0].keys())}")
            logger.info(f"Number of pages: {len(data)}")
        else:
            logger.warning("Data is empty or not in the expected format")

        # Ingest the data into OpenSearch
        ingest_data(client, index_name, data)

        logger.info("Data ingestion completed successfully")
    except Exception as e:
        logger.error(f"An error occurred during script execution: {e}")

if __name__ == "__main__":
    main()
