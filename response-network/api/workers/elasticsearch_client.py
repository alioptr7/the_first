from elasticsearch import AsyncElasticsearch
from datetime import datetime
import json
import logging

from core.config import settings

class ElasticsearchClient:
    def __init__(self, hosts=None):
        if hosts is None:
            # Use ELASTICSEARCH_URL from settings
            # Parse the URL to get hosts
            es_url = str(settings.ELASTICSEARCH_URL)
            hosts = [es_url]
        
        try:
            self.es = AsyncElasticsearch(hosts=hosts)
        except Exception as e:
            logging.error(f"Failed to initialize Elasticsearch client: {e}")
            self.es = None

    async def close(self):
        if self.es:
            await self.es.close()
    
    async def close_connection(self):
        """Alias for close() for compatibility."""
        await self.close()
    
    async def check_health(self):
        """Check if Elasticsearch is healthy."""
        if not self.es:
            return False
        
        try:
            response = await self.es.cluster.health()
            return response.get("status") in ["yellow", "green"]
        except Exception as e:
            logging.error(f"Elasticsearch health check failed: {e}")
            return False

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