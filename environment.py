from typing import Dict, List
from timer import Time
from cache import Cache, CacheElement
from strategy import EvictLeastRecentlyUsed


class Query:
    def __init__(self, query_type: str, parameters: Dict, cache: Cache):
        self.query_type = query_type
        self.parameters = parameters
        self.cache = cache

    def _select_query(self):
        pass

    def _join_query(self):
        pass


# class Env:
#     def __init__(self, cache_size: int) -> None:
#         self.cache_size = cache_size


if __name__ == '__main__':
    t = Time()
    c = Cache(10, t, equate_id_to_value=True)
    strategy = EvictLeastRecentlyUsed()

    for x in range(15):
        c.add_element(x, strategy)
        t.increment()

    print(c.cache_map)