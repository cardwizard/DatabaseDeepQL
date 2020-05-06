from buffer_pool_baseline.environment import Query, Time, \
    Cache, \
    EvictLeastRecentlyUsed, EvictMostRecentlyUsed, EvictRandomly
from json import dumps, loads
from typing import List, Dict
from tqdm import tqdm
from numpy.random import choice
from sys import argv

import random

random.seed(10)
strategies = {"LRU": EvictLeastRecentlyUsed, "MRU": EvictMostRecentlyUsed, "Random": EvictRandomly}


def get_select_query_parameters(start, end) -> Dict:
    parameters = {"start": start, "end": end, "query_type": "select"}
    return parameters


def get_join_query_parameters(start_1, end_1, start_2, end_2) -> Dict:
    parameters = {"start_table_1": start_1, "end_table_1": end_1,
                  "start_table_2": start_2, "end_table_2": end_2,
                  "query_type": "join"}
    return parameters


def get_seq_query_parameters(start, end, loop_size) -> Dict:
    parameters = {"start": start, "end": end, "loop_size": loop_size, "query_type": "sequential"}
    return parameters


def get_overlapping_blocks(number_of_queries, average_table_size, probability):

    parameter_list = []
    start = None

    for query_number in range(number_of_queries):

        if not start:
            start = random.randint(0, 100)
        else:
            start = start + random.randint(-5, 5)

        query_type = choice(["join", "select", "sequential"], p=probability)
        print(query_type)
        if query_type == "select":

            end = start + average_table_size + random.randint(-5, 5)

            if end <= start:
                continue

            p = get_select_query_parameters(start=start, end=end)

        elif query_type == "join":
            end = start + average_table_size + random.randint(-5, 5)
            if end <= start:
                continue

            start_2 = random.randint(start, end)
            end_2 = start_2 + average_table_size + random.randint(-5, 5)
            if end_2 <= start_2:
                continue

            p = get_join_query_parameters(start_1=start, end_1=end, start_2=start_2, end_2=end_2)

        else:
            end = start + average_table_size + random.randint(-5, 5)
            if end <= start:
                continue
            p = get_seq_query_parameters(start, end, random.randint(40, 50))

        parameter_list.append(p)

    return parameter_list


def run_workload(wl: List[Dict], cache_size: int, strategy, workload_id: int, avg_table_size: int):
    res = []

    # t = Time()
    c = Cache(cache_size, time=t, equate_id_to_value=True)

    # c.set_strategy(strategies[strategy]())

    for parameters in wl:
        query_params = {key: value for key, value in parameters.items() if key != "query_type"}
        query = Query(query_type=parameters["query_type"], parameters=query_params, time=t)

        query.set_query_cache(c)

        while not query.is_done():
            query.step("lru")

        hits, misses = query.step()

        res.append({"Query Type": query.query_type, "Parameters": query.parameters,
                        "Hits": hits, "Misses": misses, "Cache Size": c.max_cache_size,
                        "Eviction Strategy": strategy, "Workload ID": workload_id,
                        "Table Size": avg_table_size})

    c.clear()
    return res


if __name__ == '__main__':

    t = Time()

    cache_size_start = 10
    cache_size_end = 100

    average_table_start = 100
    average_table_end = 500

    results = []
    workload_id = 0

    for table_size in tqdm(range(average_table_start, average_table_end, 100)):
        workload = get_overlapping_blocks(50, table_size, probability=loads(argv[1]))

        for cache in range(cache_size_start, cache_size_end, 20):
            for strategy in strategies:
                workload_output = run_workload(workload, cache, strategy, workload_id, table_size)
                output = dumps(workload_output)

                with open(argv[2], "a+") as f:
                    f.write(output)
                    f.write("\n")

            workload_id += 1
    # workload = get_overlapping_blocks(50, 100)
    #
    # for strategy in tqdm(strategies):
    #     workload_output = run_workload(workload, 150, strategy, 150, 100)
    #     output = dumps(workload_output)
    #     with open("overlapping_results_tuned.json", "a+") as f:
    #         f.write(output)
    #         f.write("\n")

