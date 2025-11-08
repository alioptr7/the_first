from elasticsearch import AsyncElasticsearch
from datetime import datetime
import json
import logging

from response_network.api.core.config import settings

class ElasticsearchClient:
    def __init__(self, hosts=None):
        if hosts is None:
            hosts = [settings.ELASTICSEARCH_HOST]
        self.es = AsyncElasticsearch(hosts=hosts)

    async def close(self):
        await self.es.close()

    async def search(self, index, query, size=10):
        """Execute a search query on Elasticsearch."""
        try:
            response = await self.es.search(
                index=index,
                body=query,
                size=size
            )
            return response
        except Exception as e:
            logging.error(f"Elasticsearch search error: {e}")
            raise

    async def get_cluster_health(self):
        """Get cluster health information."""
        try:
            response = await self.es.cluster.health()
            return response
        except Exception as e:
            logging.error(f"Elasticsearch health check error: {e}")
            return {
                "status": "red",
                "error": str(e)
            }

    async def get_indices_stats(self):
        """Get statistics about indices."""
        try:
            response = await self.es.indices.stats()
            return response
        except Exception as e:
            logging.error(f"Elasticsearch indices stats error: {e}")
            return {
                "error": str(e)
            }