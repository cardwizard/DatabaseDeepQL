from buffer_pool_baseline.environment import Query, Time, \
    Cache, \
    EvictLeastRecentlyUsed, EvictMostRecentlyUsed, EvictRandomly
from json import dump
from typing import List
from tqdm import tqdm

import random

random.seed(10)
strategies = {"LRU": EvictLeastRecentlyUsed(), "MRU": EvictMostRecentlyUsed(), "Random": EvictRandomly()}


def get_select_query(start, end) -> Query:
    q = Query(query_type="select", parameters={"start": start, "end": end})
    return q


def get_join_query(start_1, end_1, start_2, end_2) -> Query:
    q = Query(query_type="join", parameters={"start_table_1": start_1, "end_table_1": end_1,
                                             "start_table_2": start_2, "end_table_2": end_2})
    return q


def get_overlapping_blocks(number_of_queries, average_table_size):

    query_list = []
    start = None

    for query_number in range(number_of_queries):

        if not start:
            start = random.randint(0, 10000)
        else:
            start = start + random.randint(-1000, 1000)

        query_type = random.choice(["select", "join"])

        if query_type == "select":

            end = start + average_table_size + random.randint(-1000, 1000)

            if end <= start:
                continue

            q = get_select_query(start=start, end=end)

        else:
            end = start + average_table_size + random.randint(-1000, 1000)
            if end <= start:
                continue

            start_2 = random.randint(start, end)
            end_2 = start_2 + average_table_size + random.randint(-1000, 1000)
            if end_2 <= start_2:
                continue

            q = get_join_query(start_1=start, end_1=end, start_2=start_2, end_2=end_2)

        q.set_time(t)
        query_list.append(q)

    return query_list


def run_workload(wl: List[Query], cache_size: int, strategy):
    results = []

    # t = Time()
    c = Cache(cache_size, time=t, equate_id_to_value=True)

    c.set_strategy(strategies[strategy])

    for query in wl:
        query.set_query_cache(c)
        while not query.is_done():
            query.step()

        hits, misses = query.step()

        results.append({"Query Type": query.query_type, "Parameters": query.parameters,
                        "Hits": hits, "Misses": misses, "Cache Size": c.max_cache_size,
                        "Eviction Strategy": strategy})
    c.clear()
    return results


if __name__ == '__main__':
    t = Time()

    cache_size_start = 10
    cache_size_end = 100

    average_table_start = 100
    average_table_end = 1000

    results = []
    for table_size in tqdm(range(average_table_start, average_table_end)):
        workload = get_overlapping_blocks(20, table_size)

        for cache in range(cache_size_start, cache_size_end):
            for strategy in strategies:
                results.extend(run_workload(workload, cache, strategy))

    with open("overlapping_results.json", "w") as f:
        dump(results, f)
