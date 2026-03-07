#!/usr/bin/env python3
"""
Qdrant Cloud Collection Provisioning Script
"""

import argparse
import os
import sys
from typing import Dict, Any

try:
    from qdrant_client import QdrantClient
    from qdrant_client.models import (
        VectorParams,
        Distance,
        HnswConfigDiff,
        OptimizersConfigDiff,
        CollectionInfo,
    )
except ImportError:
    print("ERROR: qdrant-client not installed. Run: pip install qdrant-client")
    sys.exit(1)

COLLECTION_NAME = "textbook_chunks"
VECTOR_SIZE = 3072
DISTANCE_METRIC = Distance.COSINE
HNSW_M = 16
HNSW_EF_CONSTRUCT = 100
ON_DISK = False


def get_qdrant_client() -> QdrantClient:
    qdrant_url = os.getenv("QDRANT_URL")
    qdrant_api_key = os.getenv("QDRANT_API_KEY")
    if not qdrant_url:
        print("ERROR: QDRANT_URL environment variable not set")
        sys.exit(1)
    if not qdrant_api_key:
        print("ERROR: QDRANT_API_KEY environment variable not set")
        sys.exit(1)
    try:
        client = QdrantClient(url=qdrant_url, api_key=qdrant_api_key, timeout=30)
        return client
    except Exception as e:
        print(f"ERROR: Failed to connect to Qdrant: {e}")
        sys.exit(1)


def check_collection_exists(client: QdrantClient) -> bool:
    try:
        collections = client.get_collections()
        return any(col.name == COLLECTION_NAME for col in collections.collections)
    except Exception as e:
        print(f"ERROR: Failed to check collections: {e}")
        return False


def create_collection(client: QdrantClient) -> bool:
    try:
        print(f"\n📦 Creating collection '{COLLECTION_NAME}'...")
        client.create_collection(
            collection_name=COLLECTION_NAME,
            vectors_config=VectorParams(size=VECTOR_SIZE, distance=DISTANCE_METRIC, on_disk=ON_DISK),
            hnsw_config=HnswConfigDiff(m=HNSW_M, ef_construct=HNSW_EF_CONSTRUCT),
            optimizers_config=OptimizersConfigDiff(indexing_threshold=10000),
        )
        print(f"✅ Collection '{COLLECTION_NAME}' created successfully!")
        return True
    except Exception as e:
        print(f"❌ ERROR: Failed to create collection: {e}")
        return False


def delete_collection(client: QdrantClient) -> bool:
    try:
        if not check_collection_exists(client):
            print(f"⚠️  Collection '{COLLECTION_NAME}' does not exist")
            return False
        print(f"\n⚠️  WARNING: This will permanently delete collection '{COLLECTION_NAME}'")
        confirmation = input("Type 'DELETE' to confirm: ")
        if confirmation != "DELETE":
            print("❌ Deletion cancelled")
            return False
        client.delete_collection(collection_name=COLLECTION_NAME)
        print(f"✅ Collection '{COLLECTION_NAME}' deleted successfully")
        return True
    except Exception as e:
        print(f"❌ ERROR: Failed to delete collection: {e}")
        return False


def get_collection_info(client: QdrantClient) -> Dict[str, Any]:
    try:
        if not check_collection_exists(client):
            return {"exists": False}

        info: CollectionInfo = client.get_collection(collection_name=COLLECTION_NAME)

        vectors_config = info.config.params.vectors
        if isinstance(vectors_config, dict):
            vector_params = vectors_config.get("") or next(iter(vectors_config.values()), None)
        else:
            vector_params = vectors_config

        config_data = {}
        if vector_params:
            config_data["vector_size"] = vector_params.size
            config_data["distance"] = vector_params.distance

        if info.config.hnsw_config:
            config_data["hnsw_m"] = info.config.hnsw_config.m
            config_data["hnsw_ef_construct"] = info.config.hnsw_config.ef_construct

        return {
            "exists": True,
            "name": COLLECTION_NAME,
            "vectors_count": getattr(info, "vectors_count", None) or info.points_count,
            "points_count": info.points_count,
            "indexed_vectors_count": info.indexed_vectors_count,
            "status": info.status,
            "optimizer_status": info.optimizer_status,
            "config": config_data,
        }

    except Exception as e:
        print(f"❌ ERROR: Failed to get collection info: {e}")
        return {"exists": False, "error": str(e)}


def print_collection_info(info: Dict[str, Any]) -> None:
    if not info.get("exists"):
        print(f"\n⚠️  Collection '{COLLECTION_NAME}' does not exist")
        if "error" in info:
            print(f"   Error: {info['error']}")
        return

    print(f"\n📊 Collection Information: {info['name']}")
    print(f"   Status: {info['status']}")
    print(f"   Points count: {info['points_count']:,}")
    print(f"   Vectors count: {info['vectors_count']:,}")
    print(f"   Indexed vectors: {info['indexed_vectors_count']:,}")
    print(f"   Optimizer status: {info['optimizer_status']}")
    print("\n   Configuration:")
    print(f"     Vector size: {info['config']['vector_size']}")
    print(f"     Distance metric: {info['config']['distance']}")
    print(f"     HNSW M: {info['config']['hnsw_m']}")
    print(f"     HNSW ef_construct: {info['config']['hnsw_ef_construct']}")


def main():
    parser = argparse.ArgumentParser(description="Provision Qdrant Cloud collection for RAG chatbot")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--check", action="store_true", help="Check if collection exists")
    group.add_argument("--create", action="store_true", help="Create the collection")
    group.add_argument("--delete", action="store_true", help="Delete the collection (WARNING: destructive)")
    group.add_argument("--info", action="store_true", help="Show detailed collection information")

    args = parser.parse_args()
    client = get_qdrant_client()

    if args.check:
        exists = check_collection_exists(client)
        if exists:
            print(f"✅ Collection '{COLLECTION_NAME}' exists")
            sys.exit(0)
        else:
            print(f"❌ Collection '{COLLECTION_NAME}' does not exist")
            sys.exit(1)
    elif args.create:
        if check_collection_exists(client):
            print(f"⚠️  Collection '{COLLECTION_NAME}' already exists")
            sys.exit(1)
        success = create_collection(client)
        sys.exit(0 if success else 1)
    elif args.delete:
        success = delete_collection(client)
        sys.exit(0 if success else 1)
    elif args.info:
        info = get_collection_info(client)
        print_collection_info(info)
        sys.exit(0 if info.get("exists") else 1)


if __name__ == "__main__":
    main()