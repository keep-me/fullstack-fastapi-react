# Benchmark - Final Score: 92.2/100

## Test Results

| Test                                               | Average Time (ms)      | Score              |
| :------------------------------------------------- | :--------------------- | :----------------- |
| test_user_creation_performance                     | 66.06                  | goat               |
| test_user_creation_performance_optimized           | 6.08                   | goat               |
| test_user_creation_batch_performance               | 11.88                  | goat               |
| test_user_retrieval_performance                    | 1.60                   | goat               |
| test_user_update_performance                       | 9.90                   | goat               |
| test_users_list_performance                        | 7.00                   | goat               |
| test_user_search_performance                       | 5.83                   | goat               |
| test_role_operations_performance                   | 3.39                   | goat               |
| test_session_operations_performance                | 7.40                   | goat               |

**Legend:**
- goat: < 100ms (API) / < 10ms (DB)
- not good: 100-500ms (API) / 10-100ms (DB)
- poor: > 500ms (API) / > 100ms (DB)
