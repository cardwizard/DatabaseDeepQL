from timer import Time
from uuid import uuid4
from typing import Union


class CacheElement:
    """
    Base Cache Element
    """
    def __init__(self, id: str, value: int, time: Time) -> None:
        self.id = id
        self.value = value
        self.hit_count = 0
        self.time = time
        self.last_access = time.now()

    def get_value(self):
        self.last_access = self.time.now()
        self.hit_count += 1
        return self.value

    def get_hits(self):
        return self.hit_count


class Cache:
    """
    Base Cache Class
    """
    def __init__(self, max_cache_size: int, time: Time, equate_id_to_value: bool = False) -> None:
        self.max_cache_size = max_cache_size
        self.cache_map = {}
        self.time = time
        self.equate_id_to_value = equate_id_to_value

    def get_current_size(self):
        return len(self.cache_map)

    def add_element(self, value: int):
        if self.equate_id_to_value:
            id = value
        else:
            id = str(uuid4())

        assert self.get_current_size() < self.max_cache_size

        new_element = CacheElement(id, value, self.time)
        self.cache_map[id] = new_element
        return id

    def evict_element_by_id(self, id: str) -> None:
        del self.cache_map[id]

    def evict_element_by_value(self, value: int) -> None:
        self.cache_map = {key: value for key, cache_value in self.cache_map.items() if cache_value.value != value}

    def get_element_by_id(self, id: str) -> CacheElement:
        return self.cache_map.get(id)

    def get_element_by_value(self, value: int) -> Union[CacheElement, None]:
        for cache_element in self.cache_map.values():
            if cache_element.value == value:
                return cache_element

        return None
