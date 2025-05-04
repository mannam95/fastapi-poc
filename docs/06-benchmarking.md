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

| Case | CPU Limits | CPU Reservations | Memory Limits | Memory Reservations | Workers |
| ---- | ---------- | ---------------- | ------------- | ------------------- | ------- |
| 1    | 10         | 3                | 4GB           | 2GB                 | 10      |
| 2    | 5          | 3                | 4GB           | 2GB                 | 5       |
| 3    | 10         | 3                | 4GB           | 2GB                 | 10      |

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

### Case2 Statistics

| Endpoint                 | Requests  | Failures | Median (ms) | 95%ile (ms) | 99%ile (ms) | Average (ms) | Min (ms) | Max (ms) | RPS(Last 2s) | Failures/s(Last 2s) |
| ------------------------ | --------- | -------- | ----------- | ----------- | ----------- | ------------ | -------- | -------- | ------------ | ------------------- |
| GET /api/v1/processes    | 5048      | 5        | 270         | 680         | 830         | 308.13       | 2        | 1447     | 29.3         | 0                   |
| POST /api/v1/processes   | 1295      | 3        | 400         | 1100        | 1500        | 468.75       | 1        | 2051     | 6.7          | 0                   |
| GET /api/v1/processes/1  | 3773      | 2        | 200         | 610         | 780         | 250.44       | 1        | 1497     | 23.2         | 0                   |
| PUT /api/v1/processes/\* | 2602      | 0        | 380         | 1100        | 1400        | 456.38       | 58       | 2350     | 15.2         | 0                   |
| **Aggregated**           | **12718** | **10**   | **280**     | **820**     | **1200**    | **337.86**   | **1**    | **2350** | **74.4**     | **0**               |

### Case3 Statistics

| Endpoint                 | Requests  | Failures | Median (ms) | 95%ile (ms) | 99%ile (ms) | Average (ms) | Min (ms) | Max (ms) | RPS(Last 2s) | Failures/s(Last 2s) |
| ------------------------ | --------- | -------- | ----------- | ----------- | ----------- | ------------ | -------- | -------- | ------------ | ------------------- |
| GET /api/v1/processes    | 5798      | 0        | 150         | 410         | 600         | 177.25       | 52       | 999      | 32.5         | 0                   |
| POST /api/v1/processes   | 1422      | 1        | 160         | 600         | 830         | 222.84       | 1        | 1182     | 8.5          | 0                   |
| GET /api/v1/processes/1  | 4358      | 6        | 86          | 320         | 500         | 120.93       | 2        | 914      | 24.6         | 0                   |
| PUT /api/v1/processes/\* | 2918      | 2        | 160         | 580         | 830         | 217.75       | 1        | 1181     | 16.2         | 0                   |
| **Aggregated**           | **14496** | **9**    | **130**     | **440**     | **690**     | **173.07**   | **1**    | **1182** | **81.8**     | **0**               |

## Analysis

### Performance Characteristics

1. **Read Operations (GET)**

   - Generally faster operations with median response times ranging from 86ms to 2300ms
   - GET /api/v1/processes/1 shows consistently good performance across cases
   - Case 3 shows dramatic improvement with median response time of 86ms (vs 1900ms in Case 1)

2. **Write Operations (POST/PUT)**

   - **ORM vs SQL Functions Impact**: Case 1 (SQLAlchemy ORM) showed extremely high latency (15000ms median for POST, 13000ms for PUT)
   - Cases 2-3 (PostgreSQL functions) demonstrated dramatic improvement with median times of 160-400ms
   - Performance improved by approximately 90x for POST operations and 80x for PUT operations when using native SQL functions

3. **Error Analysis**
   - High failure rate in PUT operations in Case 1 (89 failures, 20.8%)
   - Significant reduction in failures in Cases 2-3 despite handling more requests
   - Case 3 processed 2918 PUT requests with only 2 failures (0.07%)

### Error Analysis Details

The nature of errors differed significantly between case 1 and cases 2-3:

1. **Case 1 (SQLAlchemy ORM)**

   - Primarily IntegrityError exceptions due to race conditions
   - Scenario: Multiple users attempting to update the same process simultaneously
   - Time gap between ORM's check operation and actual update allowed conflicting changes
   - Higher likelihood of failures with increasing concurrent users

2. **Cases 2-3 (PostgreSQL Functions)**
   - Minimal errors (0.07% in Case 3 vs 20.8% in Case 1)
   - Errors primarily related to connection timeouts or remote disconnects
   - No data integrity violations due to atomic transaction handling at database level
   - Database functions handled concurrency properly with proper locking mechanisms

This difference demonstrates how direct SQL functions can provide atomic transaction guarantees that are more difficult to achieve through ORM layers, especially at high concurrency levels (100 users/second).

### Bottlenecks and Recommendations

1. **ORM Limitations for Complex Operations**

   - Use direct SQL functions for complex write operations with many-to-many relationships
   - Reserve SQLAlchemy ORM for simpler read operations where its convenience outweighs performance cost
   - Consider implementing stored procedures for performance-critical operations

2. **Architecture Optimization**

   - Leverage PostgreSQL's native capabilities for complex data manipulations
   - Use a hybrid approach: ORM for CRUD operations, SQL functions for complex queries
   - Implement connection pooling optimizations to handle higher throughput

3. **Resource Utilization**
   - Case 3 configuration (10 workers, 10 CPU limit) shows optimal performance
   - Consider increasing PostgreSQL resources if write operations become more frequent
   - Current memory allocation seems adequate across all test cases

### Success Metrics

- Case 3 achieved 81.8 RPS (vs 8.9 RPS in Case 1) - a 9x improvement in throughput
- Average response time decreased from 5728.82ms to 173.07ms (33x improvement)
- Failure rate dropped from 3.9% to 0.06%

### Areas for Improvement

1. Further optimize PostgreSQL functions for specific query patterns
2. Implement intelligent caching for frequently accessed data
3. Consider read replicas for scaling read operations if needed
4. Monitor and tune database indices based on query patterns

## Conclusion

The benchmarking results clearly demonstrate that while SQLAlchemy ORM provides convenience for simple CRUD operations, it becomes a significant bottleneck for complex data manipulations involving many-to-many relationships. The migration to PostgreSQL functions for these complex operations yielded dramatic performance improvements across all metrics:

1. Response times decreased by 30-90x for write operations
2. System throughput increased by 9x
3. Error rates dropped from nearly 4% to negligible levels

This hybrid approach - using ORM for simple operations and direct SQL functions for complex ones - provides an optimal balance between developer productivity and system performance. For production deployments, this approach should be adopted as a standard pattern, especially for endpoints handling complex data relationships or high write volumes.

**Note-1:** The test was run on a single machine with 10 logical CPUs and 4GB of RAM. The results are not representative of a production environment.

**Note-2:** The test assumed we have continuously from 100 users at any given time. I am not sure in a production environment we will have such a high number of users at any given time. Maybe sometime but not always.
