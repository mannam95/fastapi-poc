# Benchmarking

## Locust

Locust is a powerful tool for benchmarking FastAPI applications.

# Benchmarking Report

## Test Configuration

### Load Test Parameters

#### Locust

- **Ramp-up Strategy**: 100 users at 10 users/second (after 10 seconds we essentially have 100 concurrent users)
- **Test Duration**: 3 minutes
- **Wait Time**: Between 0.1-2 seconds between tasks
- **Host**: http://localhost:8000

#### FastAPI Application

- **pool_size**: 5
- **max_overflow**: 5
- **pool_timeout**: 30
- **pool_pre_ping**: True
- **Note**: A single worker can open max 10 connections to the database. If new requests come in while the pool is full, it will wait for a connection to be returned to the pool. If no connection is available within 30 seconds, it will raise a TimeoutError.

#### Laptop Configuration

- **CPU**: Intel(R) Core(TM) i9-11900H CPU @ 4.9GHz 2.50 GHz
- **RAM**: 32GB (16GB x 2 - 3200 MHz DDR4)
- **Cache**: 24MB L3 Cache
- **Cores**: 8 cores (16 thread or 16 logical CPUs)
- **OS**: Ubuntu 22.04 LTS

#### API request configuration

- **Process Create**, **Process Update**, **Get Process By Id**, **Get All Processes**:
- All the above end points had complete many to many relationships in the request post body and response.

### Infrastructure Resources

#### FastAPI Application

| Case | CPU Limits | CPU Reservations | Memory Limits | Memory Reservations | Workers |
| ---- | ---------- | ---------------- | ------------- | ------------------- | ------- |
| 1    | 10         | 3                | 4GB           | 2GB                 | 10      |
| 2    | 10         | 3                | 4GB           | 2GB                 | 10      |
| 3    | 5          | 3                | 4GB           | 2GB                 | 5       |
| 4    | 10         | 3                | 4GB           | 2GB                 | 10      |

- All cases contain GET, POST, PUT requests.
- Difference between {case1 vs case2, case3, case4} is the api request body.
- In case1:
  - Get list of processes do not have any many to many relationships.
  - Get process by id have many to many relationships in the response.
  - Create process do not have many to many relationships in the request.
  - Update process do not have many to many relationships in the request.
- In case2, case3, case4:
  - Get list of processes have complex many to many relationships in the response.
  - Get process by id have complex many to many relationships in the response.
  - Create process have complex many to many relationships in the request.
  - Update process have complex many to many relationships in the request.

#### PostgreSQL Database

**Note:** In all cases, the db container had only 1 case, more than enough.

| Case | CPU Limits | CPU Reservations | Memory Limits | Memory Reservations |
| ---- | ---------- | ---------------- | ------------- | ------------------- |
| 1    | 2          | 1                | 4GB           | 2GB                 |

## Performance Results

### Case1 Statistics

| Endpoint                 | Requests   | Failures | Median (ms) | 95%ile (ms) | 99%ile (ms) | Average (ms) | Min (ms) | Max (ms) | RPS(Last 2s) | Failures/s(Last 2s) |
| ------------------------ | ---------- | -------- | ----------- | ----------- | ----------- | ------------ | -------- | -------- | ------------ | ------------------- |
| GET /api/v1/processes    | 6,513      | 1        | 12          | 40          | 58          | 15.55        | 2        | 160      | 33.6         | 0                   |
| POST /api/v1/processes   | 1,669      | 0        | 28          | 61          | 89          | 31.38        | 17       | 202      | 8.0          | 0                   |
| GET /api/v1/processes/1  | 4,984      | 2        | 18          | 48          | 70          | 21.84        | 1        | 167      | 31.6         | 0.1                 |
| PUT /api/v1/processes/\* | 3,270      | 1        | 29          | 85          | 140         | 36.89        | 3        | 279      | 19.3         | 0                   |
| **Aggregated**           | **16,436** | **4**    | **18**      | **55**      | **85**      | **23.34**    | **1**    | **279**  | **92.5**     | **0.1**             |

### Case2 Statistics

| Endpoint                 | Requests | Failures | Median (ms) | 95%ile (ms) | 99%ile (ms) | Average (ms) | Min (ms) | Max (ms)  | RPS(Last 2s) | Failures/s(Last 2s) |
| ------------------------ | -------- | -------- | ----------- | ----------- | ----------- | ------------ | -------- | --------- | ------------ | ------------------- |
| GET /api/v1/processes    | 966      | 4        | 2300        | 5100        | 7400        | 2469.06      | 43       | 9185      | 3.4          | 0                   |
| POST /api/v1/processes   | 232      | 1        | 15000       | 31000       | 38000       | 15774.84     | 39       | 40662     | 1.5          | 0                   |
| GET /api/v1/processes/1  | 789      | 1        | 1900        | 4700        | 6700        | 2117.8       | 61       | 10244     | 2.5          | 0                   |
| PUT /api/v1/processes/\* | 427      | 89       | 13000       | 30000       | 36000       | 14454.87     | 49       | 43350     | 1.5          | 0.4                 |
| **Aggregated**           | **2414** | **95**   | **2700**    | **23000**   | **33000**   | **5728.82**  | **39**   | **43350** | **8.9**      | **0.4**             |

### Case3 Statistics

| Endpoint                 | Requests  | Failures | Median (ms) | 95%ile (ms) | 99%ile (ms) | Average (ms) | Min (ms) | Max (ms) | RPS(Last 2s) | Failures/s(Last 2s) |
| ------------------------ | --------- | -------- | ----------- | ----------- | ----------- | ------------ | -------- | -------- | ------------ | ------------------- |
| GET /api/v1/processes    | 5048      | 5        | 270         | 680         | 830         | 308.13       | 2        | 1447     | 29.3         | 0                   |
| POST /api/v1/processes   | 1295      | 3        | 400         | 1100        | 1500        | 468.75       | 1        | 2051     | 6.7          | 0                   |
| GET /api/v1/processes/1  | 3773      | 2        | 200         | 610         | 780         | 250.44       | 1        | 1497     | 23.2         | 0                   |
| PUT /api/v1/processes/\* | 2602      | 0        | 380         | 1100        | 1400        | 456.38       | 58       | 2350     | 15.2         | 0                   |
| **Aggregated**           | **12718** | **10**   | **280**     | **820**     | **1200**    | **337.86**   | **1**    | **2350** | **74.4**     | **0**               |

### Case4 Statistics

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

   - Case 1 showed excellent performance (12-18ms median) but with simplified data relationships
   - Case 2 showed significant latency with median response times of 1900-2300ms with complex relationships
   - Cases 3 and 4 demonstrated dramatic improvements over Case 2:
     - Case 3: 200-270ms median response times
     - Case 4: 86-150ms median response times
   - While Case 1's performance was impressive, it didn't handle the complex many-to-many relationships needed in production

2. **Write Operations (POST/PUT)**

   - Case 1 showed good performance (28-29ms median) but with simplified data
   - Case 2 showed extremely high latency (13000-15000ms median) with complex relationships
   - Cases 3 and 4 demonstrated significant improvements over Case 2:
     - Case 3: 380-400ms median for write operations
     - Case 4: 160ms median for write operations
   - Performance improved by approximately 40x for POST operations and 80x for PUT operations between Case 2 and Case 4

3. **Error Analysis**
   - Case 1 had minimal errors (4 failures total) but with simplified data
   - Case 2 showed high failure rate (89 failures in PUT operations, 20.8%) with complex data
   - Cases 3 and 4 showed significant improvement:
     - Case 4 processed 2918 PUT requests with only 2 failures (0.07%)

### Error Analysis Details

The nature of errors differed significantly between cases:

1. **Case 1**

   - Minimal errors due to simplified data relationships
   - Not representative of production scenarios with complex many-to-many relationships

2. **Case 2**

   - Primarily IntegrityError exceptions due to race conditions
   - Scenario: Multiple users attempting to update the same process simultaneously
   - Higher likelihood of failures with increasing concurrent users
   - First attempt at handling complex relationships

3. **Cases 3 and 4**
   - Minimal errors (0.07% in Case 4 vs 20.8% in Case 2)
   - Errors primarily related to connection timeouts or remote disconnects
   - No data integrity violations due to atomic transaction handling at database level
   - Database functions handled concurrency properly with proper locking mechanisms

This progression demonstrates how the system evolved from a simplified implementation (Case 1) through initial complex data handling (Case 2) to optimized implementations (Cases 3 and 4) that properly handle complex relationships while maintaining good performance.

### Bottlenecks and Recommendations

1. **Performance Optimization**

   - Case 4 configuration shows optimal performance for complex data operations
   - While Case 1 showed excellent performance, it didn't handle the complex relationships needed in production
   - Use direct SQL functions for complex write operations with many-to-many relationships
   - Implement stored procedures for performance-critical operations

2. **Architecture Optimization**

   - Leverage PostgreSQL's native capabilities for complex data manipulations
   - Use a hybrid approach: ORM for CRUD operations, SQL functions for complex queries
   - Implement connection pooling optimizations to handle higher throughput

3. **Resource Utilization**
   - Case 4 configuration (10 workers, 10 CPU limit) shows optimal performance
   - Consider increasing PostgreSQL resources if write operations become more frequent
   - Current memory allocation seems adequate across all test cases

### Success Metrics

- Case 1 achieved 92.5 RPS with simplified data
- Case 4 achieved 81.8 RPS (vs 8.9 RPS in Case 2) with complex data - a 9x improvement in throughput
- Average response time decreased from 5728.82ms to 173.07ms (33x improvement)
- Failure rate dropped from 3.9% to 0.06%

### Areas for Improvement

1. Further optimize PostgreSQL functions for specific query patterns
2. Implement intelligent caching for frequently accessed data
3. Consider read replicas for scaling read operations if needed
4. Monitor and tune database indices based on query patterns

## Conclusion

The benchmarking results demonstrate an important evolution in the system's implementation:

1. Case 1 showed excellent performance but with simplified data relationships, making it unsuitable for production use
2. Case 2 represented the first attempt at handling complex relationships, showing significant performance challenges
3. Cases 3 and 4 demonstrated progressive improvements in handling complex data while maintaining good performance

The final implementation in Case 4 yielded dramatic performance improvements across all metrics while properly handling complex data relationships:

1. Response times decreased by 40-80x for write operations compared to Case 2
2. System throughput increased by 9x
3. Error rates dropped from nearly 4% to negligible levels

This optimized approach provides an excellent balance between system performance and reliability, especially for endpoints handling complex data relationships or high write volumes. For production deployments, the Case 4 configuration should be adopted as the standard pattern.

**Note-1:** The test was run on a single machine with 10 logical CPUs and 4GB of RAM. The results are not representative of a production environment.

**Note-2:** The test assumed we have continuously from 100 users at any given time. I am not sure in a production environment we will have such a high number of users at any given time. Maybe sometime but not always.
