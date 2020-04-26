from typing import List, Dict

import random


class EvictionStrategy:
    @staticmethod
    def suggest_evictions(cache_map):
        pass


class EvictLeastRecentlyUsed(EvictionStrategy):
    @staticmethod
    def suggest_evictions(cache_map) -> List:
        min_time = min([x.get_last_access() for x in cache_map.values()])

        return [cache_element for id, cache_element in cache_map.items()
                if cache_element.get_last_access() == min_time]


class EvictMostRecentlyUsed(EvictionStrategy):
    @staticmethod
    def suggest_evictions(cache_map) -> List:
        max_time = max([x.get_last_access() for x in cache_map.values()])

        return [cache_element for id, cache_element in cache_map.items()
                if cache_element.get_last_access() == max_time]


class EvictRandomly(EvictionStrategy):
    @staticmethod
    def suggest_evictions(cache_map) -> List:
        random_key = random.choice(list(cache_map.keys()))
        return [cache_map[random_key]]
