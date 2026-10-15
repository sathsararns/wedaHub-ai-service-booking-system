import unittest
from unittest.mock import Mock, patch

import numpy as np

from app.rag import provider_index


class ProviderRetrievalTests(unittest.TestCase):
    def test_disabled_rag_uses_fallback_without_loading_or_fetching_providers(self):
        embedder = Mock()
        with (
            patch.object(provider_index, "RAG_ENABLED", False),
            patch.object(provider_index, "_embedder", embedder),
            patch.object(provider_index.backend_client, "search_providers") as fetch,
        ):
            self.assertIsNone(provider_index.semantic_search("Electrician in Galle"))
            self.assertFalse(provider_index.is_available())
        embedder.embed.assert_not_called()
        fetch.assert_not_called()

    def test_service_filter_is_applied_before_the_result_limit(self):
        electrician = {"_id": "electrician-1", "category": "Electrician"}
        carpenter = {"_id": "carpenter-1", "category": "Carpenter"}
        embedder = Mock()
        embedder.embed.return_value = [[1.0, 0.0]]
        with (
            patch.object(provider_index, "_ensure_index", return_value=True),
            patch.object(provider_index, "_get_embedder", return_value=embedder),
            patch.object(provider_index, "_index_providers", [electrician, carpenter]),
            patch.object(provider_index, "_index_embeddings", np.array([[1.0, 0.0], [0.8, 0.6]])),
        ):
            results = provider_index.semantic_search("repair my door", service="Carpentry", top_k=1)
        self.assertEqual([provider["_id"] for provider, score in results], ["carpenter-1"])
