from buffer_pool_baseline.environment import Query, Time, \
    Cache, \
    EvictLeastRecentlyUsed, EvictMostRecentlyUsed, EvictRandomly
from json import dump
from typing import List, Dict
from tqdm import tqdm
from copy import deepcopy

import random

random.seed(10)
strategies = {"LRU": EvictLeastRecentlyUsed, "MRU": EvictMostRecentlyUsed, "Random": EvictRandomly}


def get_select_query_parameters(start, end) -> Dict:
    parameters = {"start": start, "end": end, "query_type": "select"}
    return parameters


def get_join_query_parameters(start_1, end_1, start_2, end_2) -> Dict:
    parameters = {"start_table_1": start_1, "end_table_1": end_1, "start_table_2": start_2, "end_table_2": end_2,
                  "query_type": "join"}
    return parameters


def get_overlapping_blocks(number_of_queries, average_table_size):

    parameter_list = []
    start = None

    for query_number in range(number_of_queries):

        if not start:
            start = random.randint(0, 1000)
        else:
            start = start + random.randint(-100, 100)

        query_type = random.choice(["join"])

        if query_type == "select":

            end = start + average_table_size + random.randint(-100, 100)

            if end <= start:
                continue

            p = get_select_query_parameters(start=start, end=end)

        else:
            end = start + average_table_size + random.randint(-100, 100)
            if end <= start:
                continue

            start_2 = random.randint(start, end)
            end_2 = start_2 + average_table_size + random.randint(-100, 100)
            if end_2 <= start_2:
                continue

            p = get_join_query_parameters(start_1=start, end_1=end, start_2=start_2, end_2=end_2)

        parameter_list.append(p)

    return parameter_list


def run_workload(wl: List[Dict], cache_size: int, strategy, workload_id: int):
    res = []

    # t = Time()
    c = Cache(cache_size, time=t, equate_id_to_value=True)

    c.set_strategy(strategies[strategy]())

    for parameters in wl:
        query_params = {key: value for key, value in parameters.items() if key != "query_type"}
        query = Query(query_type=parameters["query_type"], parameters=query_params, time=t)

        query.set_query_cache(c)

        while not query.is_done():
            query.step()

        hits, misses = query.step()

        res.append({"Query Type": query.query_type, "Parameters": query.parameters,
                        "Hits": hits, "Misses": misses, "Cache Size": c.max_cache_size,
                        "Eviction Strategy": strategy, "Workload ID": workload_id})

    c.clear()
    return res


if __name__ == '__main__':
    t = Time()

    cache_size_start = 10
    cache_size_end = 20

    average_table_start = 10
    average_table_end = 20

    results = []
    workload_id = 0

    for table_size in range(average_table_start, average_table_end, 10):
        workload = get_overlapping_blocks(1, table_size)

        for cache in range(cache_size_start, cache_size_end, 10):
            for strategy in strategies:
                workload_output = run_workload(workload, cache, strategy, workload_id)
                print(workload_output)
                results.extend(workload_output)
        workload_id += 1

    with open("overlapping_results.json", "w") as f:
        dump(results, f)
