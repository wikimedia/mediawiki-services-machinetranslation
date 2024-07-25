import gzip
import hashlib
import os
from functools import lru_cache

from diskcache import Cache


class TranslationCache:
    def get_cache_key(
        self, source_lang: str, target_lang: str, translator: str, source_content: str
    ) -> str:
        """
        Get the cache key.

        Args:
        - source_lang: The source language.
        - target_lang: The target language.
        - translator: The translator name - model name
        - source_content: The input text.

        Returns:
        - The cache key.
        """
        translation_hash = hashlib.sha256(source_content.encode()).hexdigest()
        return "/".join([source_lang, target_lang, translator, translation_hash])

    def get(self, source_lang: str, target_lang: str, translator: str, source_content: str) -> str:
        """
        Get the cached translation if it exists.

        Args:
        - source_lang: The source language.
        - target_lang: The target language.
        - translator: The translator name - model name
        - source_content: The input text.

        Returns:
        - The cached translation if it exists, otherwise None.
        """
        cache_key = self.get_cache_key(source_lang, target_lang, translator, source_content)
        compressed_translation = self.cache.get(cache_key)
        return gzip.decompress(compressed_translation).decode() if compressed_translation else None

    def set(
        self,
        source_lang: str,
        target_lang: str,
        translator: str,
        source_content: str,
        translation: str,
    ):
        """
        Cache the translation

        Args:
        - translator: The translator object.
        - source_lang: The source language.
        - target_lang: The target language.
        - translator: The translator name - model name
        - source_content: The input text.
        - translation: The translated text.
        """
        cache_key = self.get_cache_key(source_lang, target_lang, translator, source_content)
        compressed_translation = gzip.compress(translation.encode())
        self.cache.set(cache_key, compressed_translation)

    def clear(self):
        self.cache.clear()

    def close(self):
        self.cache.close()


class DiskCache(TranslationCache):
    """
    diskcache based cache provider.
    * Cache is persisted on disk. Persists across restarts.
      Does not persist across deployments unless cache dir is kept.
    * Max 1GB of cache size, sqlite based storage. Stored in cache directory of the project.
    * Has cache eviction policy based on LRU.

    """

    def __init__(self):
        CACHE_DIRECTORY = ".cache"
        self.cache = Cache(directory=CACHE_DIRECTORY, size_limit=1e9)


@lru_cache()
def get_cache():
    """
    Get the cache provider based on the environment variable 'MACHINE_TRANSLATION_CACHE_PROVIDER'.

    Returns:
        Cache provider object based on the value of 'MACHINE_TRANSLATION_CACHE_PROVIDER'.

    Raises:
        ValueError: If the value of 'MACHINE_TRANSLATION_CACHE_PROVIDER' is unknown.
    """
    cache_provider = os.getenv("MACHINE_TRANSLATION_CACHE_PROVIDER", "disk")
    if cache_provider == "disk":
        return DiskCache()
    else:
        raise ValueError(f"Unknown cache provider: {cache_provider}")


__all__ = ["get_cache"]
