"""File to generate retrieve the AWS Secret."""

import json
import os
import sys

import boto3
from botocore.exceptions import ClientError
from loguru import logger

# logger configuration
logger.remove()
logger.add(sys.stdout, level=os.getenv("LOG_LEVEL", "INFO"))

def get_secret_name(region_name, domain_name):
    """
    Retrieve the secret name from AWS Secrets Manager based on a domain name pattern.

    List all secrets in the specified region and search for a secret whose name 
    matches the domain name pattern.

    Args:
        region_name (str): The AWS region where the secrets are stored.
        domain_name (str): The pattern to match against secret names.

    Returns:
        str or None: The name of the secret if a match is found, otherwise None.
    
    Raises:
        ClientError: If there is an error with the AWS Secrets Manager client.

    """
    client = boto3.client('secretsmanager', region_name=region_name)
    try:
        logger.info(f"Attempting to list secrets in region {region_name}")
        response = client.list_secrets()
        secrets = response['SecretList']

        # The secret name pattern for OpenSearch domains
        secret_pattern = f"{domain_name}"

        for secret in secrets:
            if secret_pattern in secret['Name']:
                logger.info(f"Found matching secret: {secret['Name']}")
                return secret['Name']

        logger.warning(f"No secret found matching pattern: {secret_pattern}")
        return None
    except ClientError as e:
        logger.error(f"An error occurred while listing secrets: {e}")
        raise e

def get_secret():
    """
    Retrieve and display a secret from AWS Secrets Manager.

    Uses the domain name pattern to find the appropriate secret, retrieves it, 
    and logs the contents. Masks secret values in the output.

    Returns:
        str: The retrieved secret as a string.
    
    Raises:
        ClientError: If there is an error with the AWS Secrets Manager client.

    """
    region_name = "eu-central-1"
    domain_name = "rag"
    secret_name = get_secret_name(region_name, domain_name)

    # Create a Secrets Manager client
    session = boto3.session.Session()
    client = session.client(
        service_name='secretsmanager',
        region_name=region_name
    )

    try:
        logger.info(f"Attempting to retrieve secret: {secret_name}")
        get_secret_value_response = client.get_secret_value(
            SecretId=secret_name
        )
    except ClientError as e:
        logger.error(f"An error occurred: {e}")
        raise e
    else:
        # Decrypt the secret using the associated KMS key
        secret = get_secret_value_response['SecretString']

        logger.info("Secret retrieved successfully")

        try:
            # Attempt to parse the secret as JSON
            secret_dict = json.loads(secret)
            logger.info("Secret contents (key-value pairs):")
            for key, value in secret_dict.items():
                logger.info(f"  {key}: {'*' * len(value)}")  # Mask the actual values
        except json.JSONDecodeError:
            logger.info("Secret is not in JSON format. Raw secret (masked):")
            logger.info('*' * len(secret))

        return secret

if __name__ == "__main__":
    """
    Execute the script to retrieve and display a secret from AWS Secrets Manager.

    Calls the function to get the secret and handles exceptions that may occur during execution.
    """
    try:
        retrieved_secret = get_secret()
        logger.info("Script executed successfully")
    except Exception as e:
        logger.error(f"An error occurred during script execution: {e}")
