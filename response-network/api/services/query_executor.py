from typing import Any, Dict
from workers.elasticsearch_client import ElasticsearchClient


class QueryExecutor:
    """Thin shim that adapts the workers' ElasticsearchClient to the API service interface.

    This provides an async `execute` method that the tasks expect.
    """

    def __init__(self):
        self.client = ElasticsearchClient()

    async def execute(self, query: str, parameters: Dict[str, Any]):
        # Assume `query` is the query_type and `parameters` is the query params dict
        return await self.client.execute_query(query_type=query, query_params=parameters)
