from typing import List, Dict


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

