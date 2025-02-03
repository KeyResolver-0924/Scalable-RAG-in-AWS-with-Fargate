"""LancgChain and Bedrock Q&A App."""

import os
import sys

import boto3
from langchain.chains import create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_aws import BedrockEmbeddings, ChatBedrock
from langchain_community.vectorstores import OpenSearchVectorSearch
from langchain_core.prompts import ChatPromptTemplate
from loguru import logger

from retrieve_endpoint import get_opensearch_endpoint
from retrieve_secret import get_secret

# logger configuration
logger.remove()
logger.add(sys.stdout, level=os.getenv("LOG_LEVEL", "INFO"))


def bedrock_embeddings(bedrock_client, bedrock_embedding_model_id):
    """
    Create a LangChain vector embedding using Bedrock.

    Args:
        bedrock_client (boto3.client): The Bedrock client.
        bedrock_embedding_model_id (str): The ID of the Bedrock embedding model.

    Returns:
        BedrockEmbeddings: A LangChain Bedrock embeddings client.

    """
    logger.info(f"Creating LangChain vector embedding using Bedrock model: {bedrock_embedding_model_id}")
    return BedrockEmbeddings(
        client=bedrock_client,
        model_id=bedrock_embedding_model_id)

def opensearch_vectorstore(index_name, opensearch_password, bedrock_embeddings_client, opensearch_endpoint, _is_aoss=False):
    """
    Create an OpenSearch vector search client.

    Args:
        index_name (str): The name of the OpenSearch index.
        opensearch_password (str): The password for OpenSearch authentication.
        bedrock_embeddings_client (BedrockEmbeddings): The Bedrock embeddings client.
        opensearch_endpoint (str): The OpenSearch endpoint URL.
        _is_aoss (bool, optional): Whether it's Amazon OpenSearch Serverless. Defaults to False.

    Returns:
        OpenSearchVectorSearch: An OpenSearch vector search client.

    """
    logger.info(f"Creating OpenSearch vector search client for index: {index_name}")
    return OpenSearchVectorSearch(
        index_name=index_name,
        embedding_function=bedrock_embeddings_client,
        opensearch_url=f"https://{opensearch_endpoint}",
        http_auth=(index_name, opensearch_password),
        is_aoss=_is_aoss,
        timeout=30,  
        retry_on_timeout=True,
        max_retries=3,
    )

def bedrock_llm(bedrock_client, bedrock_model_id):
    """
    Create a Bedrock language model client.

    Args:
        bedrock_client (boto3.client): The Bedrock client.
        bedrock_model_id (str): The ID of the Bedrock model.

    Returns:
        ChatBedrock: A LangChain Bedrock chat model.

    """
    logger.info(f"Creating Bedrock LLM with model: {bedrock_model_id}")
    
    model_kwargs = {
        # "maxTokenCount": 4096,
        "temperature": 0,
        "topP": 0.3,
        }
    
    return ChatBedrock(
        model_id=bedrock_model_id,
        client=bedrock_client,
        model_kwargs=model_kwargs
    )

def main():
    """
    Main function to run the LangChain with Bedrock and OpenSearch workflow.

    This function sets up the necessary clients, creates the LangChain components,
    and executes a query using the retrieval chain.
    """
    logger.info("Starting the LangChain with Bedrock and OpenSearch workflow...")
    
    bedrock_model_id = "amazon.titan-text-lite-v1"
    bedrock_embedding_model_id = "amazon.titan-embed-text-v1"
    region = "eu-central-1"  
    index_name = "rag"  
    domain_name = "rag"
    question = " Can you describe the React approach?"
 

    logger.info(f"Creating Bedrock client with model {bedrock_model_id}, and embeddings with {bedrock_embedding_model_id}")

    # Creating all clients for chain
    bedrock_client = boto3.client("bedrock-runtime", region_name=region)
    llm = bedrock_llm(bedrock_client, bedrock_model_id)
    
    embeddings = bedrock_embeddings(bedrock_client, bedrock_embedding_model_id)
    host = get_opensearch_endpoint(domain_name, region)
    password = get_secret()
    
    vectorstore = opensearch_vectorstore(index_name, password, embeddings, host)
    
    
    prompt = ChatPromptTemplate.from_template("""You are an assistant for question-answering tasks. 
    Use the following pieces of retrieved context to answer the question. 
    If you don't know the answer, just say that you don't know. 
    Use five sentences maximum.
    
    {context}

    Question: {input}
    Answer:""")
    
    chain = create_stuff_documents_chain(llm, prompt)
    
    retrieval_chain = create_retrieval_chain(
        retriever=vectorstore.as_retriever(),
        combine_docs_chain = chain
    )

    response = retrieval_chain.invoke({"input": question})

    logger.info(f"The answer from Bedrock {bedrock_model_id} is: {response.get('answer')}")

if __name__ == "__main__":
    main()
