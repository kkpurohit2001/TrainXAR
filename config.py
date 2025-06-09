# config.py
import os
from dotenv import load_dotenv

load_dotenv()

# Pinecone configuration
PINECONE_API_KEY       = os.getenv("PINECONE_API_KEY")
PINECONE_ENVIRONMENT   = os.getenv("PINECONE_ENVIRONMENT")
PINECONE_INDEX_NAME = os.getenv("PINECONE_INDEX_NAME", "train-xar-knowledge-base")
EMBEDDING_DIMENSION    = int(os.getenv("EMBEDDING_DIMENSION", 1536))

# OpenAI configuration
OPENAI_API_KEY         = os.getenv("OPENAI_API_KEY")


# MySQL
MYSQL_HOST = os.getenv("MYSQL_HOST")
MYSQL_PORT = int(os.getenv("MYSQL_PORT", 3306))
MYSQL_USER = os.getenv("MYSQL_USER")
MYSQL_PASSWORD = os.getenv("MYSQL_PASSWORD")
MYSQL_DATABASE = os.getenv("MYSQL_DATABASE")