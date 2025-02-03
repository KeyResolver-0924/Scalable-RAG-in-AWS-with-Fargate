
"""File to generate embeddings from PDF."""

import json
import os
import sys

import boto3
import fitz
from langchain_aws import BedrockEmbeddings
from loguru import logger

# logger
logger.remove()
logger.add(sys.stdout, level=os.getenv("LOG_LEVEL", "INFO"))

def extract_text_from_pdf(pdf_path):
    """
    Extracts text from a PDF file and returns it as a list of dictionaries.

    Each dictionary contains the page number and the extracted text for that page.

    Args:
        pdf_path (str): The file path to the PDF document.

    Returns:
        list: A list of dictionaries where each dictionary contains 'page_number' and 'text'.
    
    Raises:
        Exception: If the PDF file cannot be opened or read.

    """
    logger.info(f"Opening PDF file: {pdf_path}")

    try:
        doc = fitz.open(pdf_path)
        logger.info("PDF file opened successfully.")
    except Exception as e:
        logger.error(f"Failed to open PDF: {e}")
        raise

    pages = []

    logger.info(f"Extracting text from {len(doc)} pages.")

    for page_num in range(len(doc)):
        page = doc.load_page(page_num)
        text = page.get_text()

        pages.append({
            "page_number": page_num + 1,
            "text": text.strip()
        })
        logger.debug(f"Extracted text from page {page_num + 1}: {text[:100]}...")

    doc.close()
    logger.info(f"Text extraction completed for {len(pages)} pages.")

    return pages

def create_embeddings(pages, bedrock_client, model_id):
    """
    Creates embeddings for each page of text using a Bedrock model.

    Args:
        pages (list): A list of dictionaries where each dictionary contains 'page_number' and 'text'.
        bedrock_client (boto3.client): A Bedrock client for creating embeddings.
        model_id (str): The ID of the Bedrock model to use for embeddings.

    Returns:
        list: The input list of dictionaries with an additional 'vector_field' key containing the embeddings.

    Raises:
        Exception: If an error occurs while generating embeddings.

    """
    logger.info(f"Creating embeddings using model: {model_id}")

    bedrock_embeddings = BedrockEmbeddings(
        client=bedrock_client,
        model_id=model_id
    )

    for idx, page in enumerate(pages):
        logger.debug(f"Generating embedding for page {page['page_number']}")

        try:
            embedding = bedrock_embeddings.embed_query(page['text'])
            page['vector_field'] = embedding
            logger.debug(f"Embedding created for page {page['page_number']}: {embedding[:5]}...")
        except Exception as e:
            logger.error(f"Error creating embedding for page {page['page_number']}: {e}")

    logger.info("Embeddings creation completed.")

    return pages

def main():
    """
    Run the main process to extract text from a PDF, create embeddings, 
    and save the results to a JSON file.
    """
    pdf_path = "../data/document.pdf"
    region_name = "eu-central-1"
    bedrock_embedding_model_id = "amazon.titan-embed-text-v1"

    logger.info("Starting the main process.")

    # Create Bedrock client
    try:
        bedrock_client = boto3.client("bedrock-runtime", region_name=region_name)
        logger.info(f"Created Bedrock client in region {region_name}.")
    except Exception as e:
        logger.error(f"Failed to create Bedrock client: {e}")
        raise

    # Extract text from PDF
    extracted_pages = extract_text_from_pdf(pdf_path)

    # Create embeddings for each page
    pages_with_embeddings = create_embeddings(extracted_pages, bedrock_client, bedrock_embedding_model_id)

    # Save the extracted text and embeddings to a JSON file
    output_file = "../data/text_with_embeddings.json"
    logger.info(f"Saving extracted text and embeddings to {output_file}.")

    try:
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(pages_with_embeddings, f, ensure_ascii=False, indent=2)
        logger.info(f"Data successfully saved to {output_file}.")
    except Exception as e:
        logger.error(f"Failed to save data to {output_file}: {e}")
        raise

    # Print a sample of the first page
    if pages_with_embeddings:
        first_page = pages_with_embeddings[0]
        logger.info("Displaying sample of the first page.")
        logger.info(f"Page Number: {first_page['page_number']}")
        logger.info(f"Content (first 200 characters): {first_page['text'][:200]}...")
        logger.info(f"Embedding (first 5 values): {first_page['vector_field'][:5]}...")

    logger.info("Main process completed.")

if __name__ == "__main__":
    logger.info("Starting the script.")
    main()
    logger.info("Script execution finished.")
