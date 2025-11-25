# Response Retrieval & Caching API Documentation

**Last Updated:** 2025-11-25  
**Status:** ✅ Complete  
**Endpoints:** 5 new/updated  

---

## Overview

The Response Retrieval system provides efficient access to completed request responses with Redis-based caching for optimal performance. All responses are cached for 24 hours with automatic invalidation when new data is imported.

---

## Architecture

### Data Flow
```
User Request
    ↓
GET /requests/{id}/response
    ↓
┌─────────────────────┐
│ Check Redis Cache   │
└─────────────────────┘
    ↓ (Hit)  ↓ (Miss)
   Return  Database
   Cached    Query
   Data       ↓
             Cache
             Result
             ↓
            Return
```

### Cache Strategy
- **TTL:** 24 hours
- **Key Format:** `response:{request_id}`
- **Storage:** Redis
- **Invalidation:** Automatic on new import, manual via admin endpoints

---

## API Endpoints

### 1. Get Request Response (User)

```
GET /requests/{request_id}/response
```

**Authentication:** Required (JWT Token)

**Description:** Retrieve the response for a completed request with Redis caching support.

**Parameters:**
- `request_id` (path, UUID): UUID of the request

**Request Example:**
```bash
curl -X GET "http://localhost:8001/requests/550e8400-e29b-41d4-a716-446655440000/response" \
  -H "Authorization: Bearer {token}"
```

**Success Response (200):**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440001",
  "request_id": "550e8400-e29b-41d4-a716-446655440000",
  "result_data": {
    "status": "success",
    "data": [...],
    "count": 1000
  },
  "result_count": 1000,
  "execution_time_ms": 2345,
  "received_at": "2025-11-25T10:30:00Z",
  "is_cached": true,
  "cache_key": "response:550e8400-e29b-41d4-a716-446655440000",
  "meta": {
    "source": "cache",
    "cached_at": "2025-11-25T10:30:00Z"
  }
}
```

**Error Responses:**

- `404 Not Found`: Request not found or response not available yet
  ```json
  {
    "detail": "Response not available yet. Request is still being processed."
  }
  ```

- `403 Forbidden`: User doesn't own the request
  ```json
  {
    "detail": "Not authorized to access this request"
  }
  ```

**Caching Behavior:**
1. First retrieval: Query database, cache result
2. Subsequent retrievals (within 24h): Return from cache
3. `is_cached` field indicates if response came from cache
4. Cache expires after 24 hours

---

### 2. Get Cache Statistics (Admin)

```
GET /admin/cache/stats
```

**Authentication:** Required (Admin Only)

**Description:** Get Redis cache statistics and health information.

**Request Example:**
```bash
curl -X GET "http://localhost:8001/admin/cache/stats" \
  -H "Authorization: Bearer {admin_token}"
```

**Success Response (200):**
```json
{
  "status": "connected",
  "total_keys": 3542,
  "response_cache_keys": 1250,
  "used_memory_human": "256.5M",
  "connected_clients": 8
}
```

**Response Fields:**
- `status`: Connection status (connected/disconnected/error)
- `total_keys`: Total Redis keys
- `response_cache_keys`: Number of cached responses
- `used_memory_human`: Memory usage (human readable)
- `connected_clients`: Number of connected Redis clients

---

### 3. Clear All Cache (Admin)

```
DELETE /admin/cache/clear
```

**Authentication:** Required (Admin Only)

**Description:** Clear all cached responses (use with caution - all cached data will be lost).

**Request Example:**
```bash
curl -X DELETE "http://localhost:8001/admin/cache/clear" \
  -H "Authorization: Bearer {admin_token}"
```

**Success Response (200):**
```json
{
  "success": true,
  "message": "Cache cleared successfully",
  "entries_cleared": 1250
}
```

**Caution:** This operation:
- Clears ALL cached responses
- Impacts performance (no cached data available)
- Does NOT affect database data
- Should be used sparingly

---

### 4. Clear User Cache (Admin)

```
DELETE /admin/cache/user/{user_id}
```

**Authentication:** Required (Admin Only)

**Description:** Invalidate all cached responses for a specific user.

**Parameters:**
- `user_id` (path, UUID): User UUID

**Request Example:**
```bash
curl -X DELETE "http://localhost:8001/admin/cache/user/550e8400-e29b-41d4-a716-446655440000" \
  -H "Authorization: Bearer {admin_token}"
```

**Success Response (200):**
```json
{
  "success": true,
  "message": "User cache invalidated",
  "entries_invalidated": 45,
  "user_id": "550e8400-e29b-41d4-a716-446655440000"
}
```

---

## Redis Client Implementation

### RedisClient Class

**Location:** `request-network/api/db/redis_client.py`

**Public Methods:**

```python
# Get cached response
response = await redis_client.get_response(request_id: str) -> Optional[dict]

# Cache a response
success = await redis_client.set_response(
    request_id: str,
    response_data: dict,
    ttl_hours: int = 24
) -> bool

# Invalidate single response
deleted = await redis_client.invalidate_response(request_id: str) -> bool

# Invalidate all user responses
count = await redis_client.invalidate_user_cache(user_id: str) -> int

# Clear all cache
success = await redis_client.clear_all_cache() -> bool

# Get statistics
stats = await redis_client.get_cache_stats() -> dict
```

---

## Cache Invalidation Strategy

### Automatic Invalidation

Cache is automatically invalidated when:
1. New response imported for a request
2. Response result changes
3. Response metadata updates

**Implementation Location:** `request-network/api/workers/tasks/results_importer.py`

### Manual Invalidation

Admins can manually invalidate cache via:
1. Clear specific user cache
2. Clear all cache (global)

---

## Performance Characteristics

### Cache Hit Scenario
- Response time: ~10-50ms (Redis latency)
- Database queries: 0
- CPU usage: Minimal

### Cache Miss Scenario (First Request)
- Response time: 100-500ms (Database query + JSON serialization)
- Database queries: 1
- CPU usage: Moderate
- **Result:** Response cached for future requests

### Metrics

```
Cache Statistics Example:
├── Total cache keys: 5,000
├── Response cache entries: 2,500
├── Average response size: ~50KB
├── Total memory: ~125MB
├── Hit ratio: ~85% (typical production)
└── Memory per entry: ~50KB avg
```

---

## Configuration

### Environment Variables

```bash
# Redis URL for caching
REDIS_URL=redis://redis:6380/0

# Cache TTL (hours) - default 24
CACHE_TTL_HOURS=24

# Response size limit for caching (optional)
CACHE_MAX_RESPONSE_SIZE=10485760  # 10MB
```

### Database Models

**ResponseDetailed Schema:**
```python
class ResponseDetailed(BaseModel):
    id: UUID
    request_id: UUID
    result_data: dict | None
    result_count: int | None
    execution_time_ms: int | None
    received_at: datetime
    is_cached: bool
    cache_key: str | None
    meta: dict | None
```

---

## Error Handling

### Common Errors

**404 Not Found**
- Request doesn't exist
- Response hasn't been processed yet

**403 Forbidden**
- User doesn't own the request
- Admin endpoints require admin role

**Redis Connection Issues**
- Gracefully falls back to database
- Logs warning but doesn't fail request
- Cache operations are non-blocking

---

## Best Practices

### For Users

1. **First Retrieval:** Expect 100-500ms response time
2. **Subsequent Retrievals:** Expect <50ms response time
3. **Monitor Status:** Check `is_cached` field to understand performance
4. **Long TTL:** Results cached for 24 hours, no need to retrieve frequently

### For Admins

1. **Cache Monitoring:** Check stats regularly
  ```bash
  curl http://localhost:8001/admin/cache/stats
  ```

2. **Memory Management:** Monitor memory usage
   - Clear cache if usage exceeds 70% of available memory
   - Consider increasing Redis memory allocation

3. **Cache Invalidation:** Use user-specific clearing before global clearing
   - More targeted approach
   - Less performance impact

4. **Maintenance Window:** Clear cache during low-traffic periods

---

## Testing

### Test Endpoints

```bash
# Test cache miss (first request)
curl -X GET "http://localhost:8001/requests/{id}/response"
# Expected: 100-500ms, result_data included, is_cached=false

# Test cache hit (second request)
curl -X GET "http://localhost:8001/requests/{id}/response"
# Expected: <50ms, result_data included, is_cached=true

# Test admin stats
curl -X GET "http://localhost:8001/admin/cache/stats"
# Expected: Cache statistics with response_cache_keys count

# Test cache clear
curl -X DELETE "http://localhost:8001/admin/cache/clear"
# Expected: entries_cleared count

# Test user cache clear
curl -X DELETE "http://localhost:8001/admin/cache/user/{user_id}"
# Expected: entries_invalidated count
```

---

## Monitoring & Debugging

### Redis CLI

```bash
# Connect to Redis
redis-cli -h localhost -p 6380

# View all response cache keys
KEYS "response:*"

# View specific response
GET "response:{request_id}"

# Monitor cache operations
MONITOR

# View memory stats
INFO memory

# Clear all cache (warning!)
FLUSHDB
```

### Application Logs

```bash
# View caching operations
docker-compose logs -f api | grep -i cache

# View Redis connection status
docker-compose logs -f api | grep -i redis
```

---

## Troubleshooting

| Issue | Cause | Solution |
|-------|-------|----------|
| High response times | Cache miss or Redis down | Check Redis connection, review query optimization |
| Out of memory | Too many cached entries | Clear old cache entries, increase Redis memory |
| Cache not invalidating | Worker task issue | Check results_importer logs, verify Redis connection |
| 404 on response retrieval | Response not imported yet | Check if results were imported, view worker logs |

---

## Future Improvements

- [ ] Selective cache invalidation by query type
- [ ] Cache warming on import
- [ ] Compression for large responses
- [ ] Tiered caching (Redis → CDN)
- [ ] Cache analytics and heatmaps
- [ ] Automatic cache size management

---

**Implementation Date:** 2025-11-25  
**Status:** Production-Ready ✅  
**Next Phase:** Testing & Optimization
