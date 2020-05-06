## Environment

The environment consists of multiple classes. Rendering the query environment requires a user to initialize the timer.
This is followed by initializing a cache with a particular size.
Here is an example: 

```python
from buffer_pool_baseline.environment import Query, Time, \
    Cache


t = Time()

c = Cache(10, t, equate_id_to_value=True)

# Here is how you create queries of different types
q1 = Query(query_type="sequential", time=t,
           parameters={"start": 0, "end": 50, "loop_size": 10})
q2 = Query(query_type="join", time=t, parameters={'start_table_1': 0, 'end_table_1': 20,
                                                  'start_table_2': 10, 'end_table_2': 30})
q3 = Query(query_type="select", time=t, parameters={"start": 10, "end": 20})

# Cache needs to be set up for each query independently!
# e.g. of q3 is shown below: 
q3.set_query_cache(c)

print(q1.actions) # Use this to print the set of possible actions in the environment. 
while not q3.is_done():
    # Pass action as part of step! it will return reward 
    hits, misses = q3.step(q3.actions[0])

# Final result!
print(q3.step())
```