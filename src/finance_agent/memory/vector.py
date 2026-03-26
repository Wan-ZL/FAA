"""ChromaDB vector store for semantic search.

Handles semantic search over unstructured and semi-structured text:
news articles, SEC filings, earnings calls, analysis reports.
"""

from __future__ import annotations

import logging
from typing import Any

logger = logging.getLogger(__name__)


class VectorStore:
    """ChromaDB-based vector store for semantic search.

    Collections: news, sec_filings, earnings_calls, analyst_reports, system_reports
    """

    def __init__(self, persist_dir: str = "./data/chroma") -> None:
        self.persist_dir = persist_dir
        self._client = None
        self._collections: dict[str, Any] = {}

    def _get_client(self) -> Any:
        """Lazy-initialize ChromaDB client."""
        if self._client is None:
            import chromadb
            from chromadb.config import Settings
            self._client = chromadb.PersistentClient(
                path=self.persist_dir,
                settings=Settings(anonymized_telemetry=False),
            )
        return self._client

    def _get_collection(self, name: str) -> Any:
        """Get or create a collection."""
        if name not in self._collections:
            client = self._get_client()
            self._collections[name] = client.get_or_create_collection(
                name=name,
                metadata={"hnsw:space": "cosine"},
            )
        return self._collections[name]

    def add_documents(
        self,
        collection_name: str,
        documents: list[str],
        ids: list[str],
        metadatas: list[dict[str, Any]] | None = None,
    ) -> None:
        """Add documents to a collection."""
        collection = self._get_collection(collection_name)
        collection.upsert(
            documents=documents,
            ids=ids,
            metadatas=metadatas,
        )
        logger.info(f"Added {len(documents)} documents to '{collection_name}'")

    def search(
        self,
        collection_name: str,
        query: str,
        n_results: int = 5,
        where: dict[str, Any] | None = None,
    ) -> list[dict[str, Any]]:
        """Semantic search over a collection.

        Returns:
            List of dicts with 'document', 'metadata', 'distance' keys
        """
        collection = self._get_collection(collection_name)
        kwargs: dict[str, Any] = {
            "query_texts": [query],
            "n_results": n_results,
        }
        if where:
            kwargs["where"] = where

        results = collection.query(**kwargs)

        output = []
        docs = results.get("documents", [[]])[0]
        metas = results.get("metadatas", [[]])[0]
        dists = results.get("distances", [[]])[0]
        for i, doc in enumerate(docs):
            output.append({
                "document": doc,
                "metadata": metas[i] if i < len(metas) else {},
                "distance": dists[i] if i < len(dists) else 0,
            })
        return output

    def count(self, collection_name: str) -> int:
        """Get document count in a collection."""
        collection = self._get_collection(collection_name)
        return collection.count()

    def delete(self, collection_name: str, ids: list[str]) -> None:
        """Delete documents by ID."""
        collection = self._get_collection(collection_name)
        collection.delete(ids=ids)
