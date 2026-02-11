"""
Setup configuration for RAG Chatbot API
"""

from setuptools import setup, find_packages

setup(
    name="rag-chatbot-api",
    version="1.0.0",
    description="RAG-Powered Textbook Chatbot API",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    package_data={
        "": ["*.sql"],
        "db": ["migrations/*.sql"],
    },
    python_requires=">=3.11",
    install_requires=[
        "fastapi>=0.109.0",
        "uvicorn[standard]>=0.27.0",
        "qdrant-client>=1.7.3",
        "psycopg[binary]>=3.1.17",
        "openai>=1.10.0",
        "cohere>=4.47",
        "sentence-transformers>=2.3.1",
        "langchain>=0.1.4",
        "pydantic>=2.5.3",
        "python-dotenv>=1.0.1",
        "sentry-sdk[fastapi]>=1.39.2",
        "httpx>=0.26.0",
        "pyjwt>=2.8.0",
    ],
)
