from typing import Dict, List, Tuple
from timer import Time
from cache import Cache, CacheElement
from strategy import EvictLeastRecentlyUsed, EvictMostRecentlyUsed, EvictRandomly, EvictionStrategy


class Query:
    def __init__(self, query_type: str, parameters: Dict, cache: Cache = None, time: Time = None):
        self.query_type = query_type
        self.parameters = parameters
        self.time = time

        self.cache = cache
        self.done = False

        self.hits = 0
        self.misses = 0

    def set_query_cache(self, cache):
        self.cache = cache

    def set_time(self, time):
        self.time = time

    def is_done(self):
        return self.done

    def step(self):
        if self.is_done():
            return self.hits, self.misses

        self.time.increment()

        if self.query_type == "select":
            return self._step_select_query()

        if self.query_type == "join":
            return self._step_join_query()

    def _get_element(self, value):
        next_element = self.cache.get_element_by_id(value)

        if next_element:
            # Increase the hit rate if element is found!
            self.hits += 1
        else:
            self.cache.add_element(value)
            self.misses += 1

        next_element = self.cache.get_element_by_id(value)
        return next_element

    def _step_select_query(self):
        # parameter requirement: {"start": int, "end": int}
        if self.parameters.get("current_position") is None:
            self.parameters["current_position"] = self.parameters["start"]

        if self.parameters["current_position"] == self.parameters["end"]:
            self.done = True
            return self.hits, self.misses

        next_element = self._get_element(self.parameters["current_position"])
        next_element.get_value()

        # Increment the current position
        self.parameters["current_position"] += 1

        return self.hits, self.misses

    def _step_join_query(self):
        # parameter requirement: {"start_table_1": int, "end_table_1": int,
        # start_table_2": int, "end_table_2": int}
        if self.parameters.get("current_position_table_1") is None:
            self.parameters["current_position_table_1"] = self.parameters["start_table_1"]

        if self.parameters.get("current_position_table_2") is None:
            self.parameters["current_position_table_2"] = self.parameters["start_table_2"]

        if (self.parameters["current_position_table_1"] == self.parameters["end_table_1"]) and \
                (self.parameters["current_position_table_2"] == self.parameters["end_table_2"]):
            # Query is complete
            self.done = True
            return self.hits, self.misses

        if self.parameters["current_position_table_2"] == self.parameters["end_table_2"]:
            # Reset the values for the next iteration
            self.parameters["current_position_table_1"] += 1
            self.parameters["current_position_table_2"] = self.parameters["start_table_2"]

        # Get both the elements!
        self._get_element(self.parameters["current_position_table_1"]).get_value()
        self._get_element(self.parameters["current_position_table_2"]).get_value()

        self.parameters["current_position_table_2"] += 1

        return self.hits, self.misses


class QueryWorkload:
    def __init__(self, query_list: List[Query]) -> None:

        self.query_list = query_list
        self.caches = []

    def assign_caches(self, cache_list) -> None:
        for id, cache in enumerate(cache_list):
            self.query_list[id].set_query_cache(cache)

    def assign_strategies(self, strategies: List[EvictionStrategy]) -> None:
        assert len(self.query_list) == len(strategies)

        for id, strategy in enumerate(strategies):
            self.query_list[id].cache.set_strategy(strategy)

    def is_done(self):
        return all([query.is_done() for query in self.query_list])

    def step(self) -> Tuple:
        workload_hits = 0
        workload_misses = 0

        for query in self.query_list:
            hit, miss = query.step()
            workload_hits += hit
            workload_misses += miss

        return workload_hits, workload_misses


if __name__ == '__main__':

    t = Time()
    # c1 = Cache(50, t, equate_id_to_value=True)
    c2 = Cache(10, t, equate_id_to_value=True)

    lru_strategy = EvictLeastRecentlyUsed()
    mru_strategy = EvictMostRecentlyUsed()
    random_strategy = EvictRandomly()
    c2.set_strategy(random_strategy)

    q1 = Query(query_type="join", time=t, parameters={"start_table_1": 0, "end_table_1": 15,
                                                      "start_table_2": 20, "end_table_2": 30})
    q1.set_query_cache(c2)

    while not q1.is_done():
        print(q1.step())

    # q2 = Query(query_type="select", time=t, parameters={"start": 10, "end": 20})
    # q3 = Query(query_type="select", time=t, parameters={"start": 10, "end": 20})
    # q4 = Query(query_type="select", time=t, parameters={"start": 10, "end": 20})

