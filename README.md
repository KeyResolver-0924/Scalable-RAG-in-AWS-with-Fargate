# RAG Application with LangChain, AWS Opensearch and AWS Bedrock

<p align="center">
<img width="737" alt="cover_gke_medium" src="https://github.com/user-attachments/assets/bed9591e-23f0-4219-86e8-9764f51da0a2">
</p>

This repository contains a full RAG application using Terraform as IaC, LangChain as framework, AWS Bedrock as LLM and Embedding Models, AWS OpenSearch as a vector database, and deployment on AWS OpenSearch endpoint. 

Main Steps

- **Data Ingestion**: Load data to an Opensearch Index
- **Embedding and Model**: Bedrock Titan
- **Vector Store and Endpoint**: Opensearch
- **IaC**: Terraform
- **data**: original pdf document and generated json file with embeddings

Feel free to ⭐ and clone this repo 😉

## Tech Stack

![Visual Studio Code](https://img.shields.io/badge/Visual%20Studio%20Code-0078d7.svg?style=for-the-badge&logo=visual-studio-code&logoColor=white)
![Python](https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54)
![Anaconda](https://img.shields.io/badge/Anaconda-%2344A833.svg?style=for-the-badge&logo=anaconda&logoColor=white)
![Linux](https://img.shields.io/badge/Linux-FCC624?style=for-the-badge&logo=linux&logoColor=white)
![Ubuntu](https://img.shields.io/badge/Ubuntu-E95420?style=for-the-badge&logo=ubuntu&logoColor=white)
![Git](https://img.shields.io/badge/git-%23F05033.svg?style=for-the-badge&logo=git&logoColor=white)
![AWS](https://img.shields.io/badge/AWS-%23FF9900.svg?style=for-the-badge&logo=amazon-aws&logoColor=white)


## Project Structure

The project has been structured with the following files:

- `terraform:` IaC
- `tests`: unittest and mock tests
- `src:` scripts with the app logic
- `requirements.txt:` project requirements
- `Makefile:` command for testing, linting and formating
- `pyproject.toml:` linting/formatting requirements



## Project Set Up

The Python version used for this project is Python 3.11.

1. Clone the repo (or download it as a zip file):

   ```bash
   git clone https://github.com/benitomartin/aws-bedrock-opensearch-langchain.git
   ```

2. Create the virtual environment named `main-env` using Conda with Python version 3.10:

   ```bash
   conda create -n main-env python=3.11
   conda activate main-env
   ```
 
3. Install the requirements.txt:

    ```bash
    pip install -r requirements.txt

    or
 
    make req
    ```

4. Create infrastructure from the terraform folder. This can take up to 30 minutes

   ```bash
   conda install conda-forge::terraform
   terraform init
   terraform plan
   terraform apply
   ```

5. Generate embeddings from documents:

   ```bash
   python src/generate_embeddings.py
   ```

6. Create Index:
   
   ```bash
   python src/create_index.py
    ```

7. Ingest documents into index:
   
    ```bash
    python src/ingest_docs_with_embeddings.py
    ```

8. Test the app to get a reply:
 
    ```bash
    python src/app.py
    ```

The app contains a question. You can change it accordingly to test other scenarios.
