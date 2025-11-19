import logging
from typing import Any, Dict

from elasticsearch import Elasticsearch, ConnectionError, NotFoundError, TransportError

from .config import settings

logger = logging.getLogger(__name__)


class ElasticsearchClient:
    """
    A synchronous client to interact with Elasticsearch, tailored for the Response Network.
    It handles connection, query building, validation, and execution.
    """

    def __init__(self, es_url: str = str(settings.ELASTICSEARCH_URL)):
        logger.info(f"Initializing Elasticsearch client for URL: {es_url}")
        self.client = Elasticsearch(
            hosts=[es_url],
            # TODO: Add authentication in production
            # http_auth=(settings.ELASTICSEARCH_USER, settings.ELASTICSEARCH_PASSWORD),
            retry_on_timeout=True,
            max_retries=3,
            request_timeout=settings.ELASTICSEARCH_QUERY_TIMEOUT,
        )

    def close_connection(self):
        """Closes the Elasticsearch client connection."""
        logger.info("Closing Elasticsearch client connection.")
        self.client.close()

    def check_health(self) -> bool:
        """Checks the health of the Elasticsearch cluster."""
        try:
            is_healthy = self.client.ping()
            if is_healthy:
                logger.info("Elasticsearch cluster is healthy.")
            else:
                logger.warning("Elasticsearch cluster is not healthy.")
            return is_healthy
        except ConnectionError:
            logger.error("Failed to connect to Elasticsearch cluster.")
            return False

    def build_es_query(self, query_type: str, query_params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Builds a basic Elasticsearch query dictionary from the given type and params.
        This is a simplified builder and will be expanded.
        """
        # The 'index' is part of query_params but used at the search level, not in the query body.
        # We remove it to avoid it being part of the query DSL.
        params_for_dsl = query_params.copy()
        params_for_dsl.pop("index", None)

        # Construct the query body based on the query type
        query_body = {
            "query": {
                query_type: params_for_dsl
            }
        }
        return query_body

    def validate_query(self, index: str, query_body: Dict[str, Any]):
        """
        Performs pre-execution validation on the query.
        Raises ValueError for invalid queries.
        
        TODO: Implement index whitelisting based on user profile.
        """
        if not index:
            raise ValueError("Index name cannot be empty.")
        
        # For now, we assume all indices are allowed, but this is where
        # a check against a user's allowed indices would go.
        logger.debug(f"Query validation passed for index '{index}'.")

    async def execute_query(
        self,
        query_type: str,
        query_params: Dict[str, Any],
        size: int = 100,
        offset: int = 0,
    ) -> Dict[str, Any]:
        """
        Validates and executes a search query against Elasticsearch.
        """
        index = query_params.get("index")
        if not index:
            raise ValueError("Missing 'index' in query_params.")

        final_size = min(size, settings.ELASTICSEARCH_MAX_RESULT_SIZE)
        query_body = self.build_es_query(query_type, query_params)
        self.validate_query(index, query_body)

        logger.info(f"Executing query on index '{index}' with size {final_size}.")
        logger.debug(f"Elasticsearch query body: {query_body}")

        try:
            response = await self.client.search(
                index=index,
                body=query_body,
                size=final_size,
                from_=offset,
                request_timeout=settings.ELASTICSEARCH_QUERY_TIMEOUT,
            )
            return response
        except NotFoundError:
            logger.warning(f"Index '{index}' not found.")
            raise
        except TransportError as e:
            logger.error(f"Elasticsearch transport error on index '{index}': {e.error} - {e.info}")
            raise
        except Exception as e:
            logger.critical(f"An unexpected error occurred during Elasticsearch query: {e}", exc_info=True)
            raise