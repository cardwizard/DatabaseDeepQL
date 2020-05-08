from typing import Dict, List, Tuple
from buffer_pool_baseline.timer import Time
from buffer_pool_baseline.cache import Cache
from buffer_pool_baseline.strategy import EvictionStrategy


class Query:
    def __init__(self, query_type: str, parameters: Dict, cache: Cache = None, time: Time = None,
                 found_in_cache_optim=True):
        self.query_type = query_type
        self.parameters = parameters
        self.time = time

        self.cache = cache
        self.done = False

        self.found_in_cache_optim = found_in_cache_optim
        self.hits = 0
        self.misses = 0
        self.actions = ["lru", "mru"]

    def copy(self):
        q = Query(self.query_type, self.parameters, self.cache.copy(), self.time.copy())
        q.done = self.done
        q.found_in_cache_optim = self.found_in_cache_optim
        q.hits = self.hits
        q.misses = self.misses
        return q

    def set_query_cache(self, cache):
        self.cache = cache

    def set_time(self, time):
        self.time = time

    def is_done(self):
        return self.done

    def step(self, action=None):
        if self.is_done():
            return self.hits, self.misses

        self.time.increment()
        hits, misses, found_in_cache = None, None, None

        if self.query_type == "select":
            hits, misses, found_in_cache = self._step_select_query(action)

        if self.query_type == "join":
            hits, misses, found_in_cache = self._step_join_query(action)

        if self.query_type == "sequential":
            hits, misses, found_in_cache = self._step_sequential_query(action)

        # If the optimizer is on, continue steos
        if found_in_cache and self.found_in_cache_optim:
            self.step(action)

        return hits, misses

    def _get_element(self, value, action):
        next_element = self.cache.get_element_by_id(value)
        found_in_cache = False

        if next_element:
            # Increase the hit rate if element is found!
            self.hits += 1
            found_in_cache = True
        else:
            self.cache.add_element(value, action)
            self.misses += 1

        next_element = self.cache.get_element_by_id(value)
        return next_element, found_in_cache

    def _step_select_query(self, action=None):
        # parameter requirement: {"start": int, "end": int}
        if self.parameters.get("current_position") is None:
            self.parameters["current_position"] = self.parameters["start"]

        if self.parameters["current_position"] == self.parameters["end"]:
            self.done = True
            return self.hits, self.misses, False

        next_element, found_in_cache = self._get_element(self.parameters["current_position"], action)
        next_element.get_value()

        # Increment the current position
        self.parameters["current_position"] += 1

        return self.hits, self.misses, found_in_cache

    def _step_sequential_query(self, action = None):
        if self.parameters.get("current_position") is None:
            self.parameters["current_position"] = self.parameters["start"]

        if self.parameters.get("current_counter") is None:
            self.parameters["current_counter"] = 0

        if self.parameters["current_position"] == self.parameters["end"] and \
                self.parameters["current_counter"] == self.parameters["loop_size"]:
            self.done = True
            return self.hits, self.misses, False

        if self.parameters["current_position"] == self.parameters["end"]:
            current_element, found_in_cache = self._get_element(self.parameters["current_position"], action)
            current_element.get_value()

            self.parameters["current_counter"] += 1
            self.parameters["current_position"] = self.parameters["start"]

            return self.hits, self.misses, found_in_cache

        current_element, found_in_cache = self._get_element(self.parameters["current_position"], action)
        current_element.get_value()

        self.parameters["current_position"] += 1

        return self.hits, self.misses, found_in_cache

    def _step_join_query(self, action=None):
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
            return self.hits, self.misses, False

        if self.parameters["current_position_table_2"] == self.parameters["end_table_2"]:
            # Reset the values for the next iteration
            self.parameters["current_position_table_1"] += 1
            self.parameters["current_position_table_2"] = self.parameters["start_table_2"]

        # Get both the elements!
        element_1, found_in_cache_1 = self._get_element(self.parameters["current_position_table_1"], action)
        element_1.get_value()

        element_2, found_in_cache_2 = self._get_element(self.parameters["current_position_table_2"], action)
        element_2.get_value()
        self.parameters["current_position_table_2"] += 1

        return self.hits, self.misses, (found_in_cache_1 and found_in_cache_2)


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

    c2 = Cache(4, t, equate_id_to_value=True)

    q1 = Query(query_type="sequential", time=t,
               parameters={"start": 1, "end": 6, "loop_size": 3})

    q2 = Query(query_type="join", time=t, parameters={'start_table_1': 0, 'end_table_1': 20,
                                                      'start_table_2': 10, 'end_table_2': 30})
    q3 = Query(query_type="select", time=t, parameters={"start": 10, "end": 20})

    q1.set_query_cache(c2)

    old_observations = []

    while not q1.is_done():
        q1.step("mru")
        # old_observations.append(q1.copy())

    print(q1.step())
