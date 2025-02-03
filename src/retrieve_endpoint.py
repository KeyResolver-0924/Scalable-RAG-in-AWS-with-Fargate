"""File to generate retrieve the endpoint."""

import sys

import boto3
from botocore.exceptions import ClientError


def get_opensearch_endpoint(domain_name, region):
    """
    Retrieve the OpenSearch domain endpoint.

    Attempt to describe the OpenSearch domain and return the endpoint if available.

    Args:
        domain_name (str): The name of the OpenSearch domain.
        region (str): The AWS region where the OpenSearch domain is hosted.

    Returns:
        str or None: The endpoint of the OpenSearch domain if available, otherwise None.
    
    Prints:
        Status messages and errors to the standard output or standard error.

    """
    client = boto3.client('es', region_name=region)
    try:
        print(f"Attempting to describe OpenSearch domain: {domain_name}")
        response = client.describe_elasticsearch_domain(DomainName=domain_name)
        print("Domain description retrieved successfully")

        # Check if the Endpoint exists in the response
        endpoint = response['DomainStatus'].get('Endpoint', None)
        if endpoint:
            print(f"Endpoint: {endpoint}")
            return endpoint
        else:
            print("No endpoint found for the domain.", file=sys.stderr)
            return None

    except ClientError as e:
        print(f"ClientError: {e}", file=sys.stderr)
    except Exception as e:
        print(f"An error occurred during script execution: {e}", file=sys.stderr)

def main(domain_name, region_name):
    """
    Execute the script to retrieve and print the OpenSearch domain endpoint.

    Args:
        domain_name (str): The name of the OpenSearch domain.
        region_name (str): The AWS region where the OpenSearch domain is hosted.

    Returns:
        bool: True if the endpoint was successfully retrieved, False otherwise.

    """
    try:
        endpoint = get_opensearch_endpoint(domain_name, region_name)
        if endpoint:
            print("Script executed successfully")
            return True
        else:
            print("No endpoint returned.", file=sys.stderr)
            return False
    except Exception as e:
        print(f"An error occurred during script execution: {e}", file=sys.stderr)
        return False

if __name__ == "__main__":
    region_name = "eu-central-1"
    domain_name = "rag"
    main(domain_name, region_name)
