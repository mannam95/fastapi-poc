# Benchmarking

## Locust

Locust is a powerful tool for benchmarking FastAPI applications.

# Benchmarking Report

## Test Configuration

### Load Test Parameters

#### Locust

- **Ramp-up Strategy**: 100 users at 10 users/second
- **Test Duration**: 3 minutes
- **Wait Time**: Between 0.1-2 seconds between tasks
- **Host**: http://localhost:8000

#### FastAPI Application

- **pool_size**: 5
- **max_overflow**: 5
- **pool_timeout**: 30
- **pool_pre_ping**: True
- **Note**: A single worker can open max 10 connections to the database. If new requests come in while the pool is full, it will wait for a connection to be returned to the pool. If no connection is available within 30 seconds, it will raise a TimeoutError.

### Infrastructure Resources

#### FastAPI Application

| Case | CPU Limits | CPU Reservations | Memory Limits | Memory Reservations |
| ---- | ---------- | ---------------- | ------------- | ------------------- |
| 1    | 10         | 3                | 4GB           | 2GB                 |
| 2    | 5          | 3                | 4GB           | 2GB                 |
| 3    | 10         | 3                | 4GB           | 2GB                 |

#### PostgreSQL Database

**Note:** In all cases, the db container had only 1 case, more than enough.

| Case | CPU Limits | CPU Reservations | Memory Limits | Memory Reservations |
| ---- | ---------- | ---------------- | ------------- | ------------------- |
| 1    | 2          | 1                | 4GB           | 2GB                 |

## Performance Results

### Case1 Statistics

| Endpoint                 | Requests | Failures | Median (ms) | 95%ile (ms) | 99%ile (ms) | Average (ms) | Min (ms) | Max (ms)  | RPS(Last 2s) | Failures/s(Last 2s) |
| ------------------------ | -------- | -------- | ----------- | ----------- | ----------- | ------------ | -------- | --------- | ------------ | ------------------- |
| GET /api/v1/processes    | 966      | 4        | 2300        | 5100        | 7400        | 2469.06      | 43       | 9185      | 3.4          | 0                   |
| POST /api/v1/processes   | 232      | 1        | 15000       | 31000       | 38000       | 15774.84     | 39       | 40662     | 1.5          | 0                   |
| GET /api/v1/processes/1  | 789      | 1        | 1900        | 4700        | 6700        | 2117.8       | 61       | 10244     | 2.5          | 0                   |
| PUT /api/v1/processes/\* | 427      | 89       | 13000       | 30000       | 36000       | 14454.87     | 49       | 43350     | 1.5          | 0.4                 |
| **Aggregated**           | **2414** | **95**   | **2700**    | **23000**   | **33000**   | **5728.82**  | **39**   | **43350** | **8.9**      | **0.4**             |

## Analysis

### Performance Characteristics

1. **Read Operations (GET)**

   - Fastest operations with median response times under 600ms
   - GET /api/v1/processes/1 shows best performance (430ms median)
   - List endpoint (/api/v1/processes) slightly slower due to larger payload

2. **Write Operations (POST/PUT)**

   - Significantly slower due to many-to-many relationships
   - POST operations show highest latency (4,500ms median)
   - PUT operations affected by race conditions

3. **Error Analysis**
   - High failure rate in PUT operations (76% failure rate)
   - Failures primarily due to concurrent updates on same resources
   - Read operations show minimal failures

### Bottlenecks and Recommendations

1. **Database Concurrency**

   - Implement optimistic locking for PUT operations
   - Consider using database-level row locking
   - Add retry mechanisms for failed updates

2. **Many-to-Many Relationships**

   - Consider denormalizing frequently accessed data
   - Implement caching for relationship lookups
   - Optimize SQLAlchemy queries with selectinload or joinedload

3. **Resource Utilization**
   - Current CPU allocation seems sufficient
   - Memory usage appears well-balanced
   - Consider increasing PostgreSQL CPU allocation if write-heavy

### Success Metrics

- Overall RPS: 18.6 requests per second
- Read operations show good performance
- System handles concurrent users effectively for read operations

### Areas for Improvement

1. Resolve PUT operation race conditions
2. Optimize many-to-many relationship handling
3. Implement better concurrency control
4. Consider adding caching layer for frequently accessed data

## Conclusion

The system demonstrates good performance for read operations but faces challenges with concurrent write operations. The primary bottleneck appears to be the handling of many-to-many relationships and race conditions in update operations. Implementing proper concurrency control and optimizing relationship handling should significantly improve write operation performance.

**Note-1:** The test was run on a single machine with 10 logical CPUs and 4GB of RAM. The results are not representative of a production environment.

**Note-2:** The test assumed we have continuosly from 100 users at any given time. I am not sure in a production environment we will have such a high number of users at any given time. Maybe sometime but not always.
