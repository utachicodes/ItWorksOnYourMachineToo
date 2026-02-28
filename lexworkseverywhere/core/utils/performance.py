# -*- coding: utf-8 -*-
import time
import functools
import logging
from typing import Callable

logger = logging.getLogger("lexworkseverywhere.perf")


def monitor_performance(name: str):
    """Décorateur pour mesurer le temps d'exécution d'une fonction."""
    def decorator(func: Callable):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.perf_counter()
            result = func(*args, **kwargs)
            end_time = time.perf_counter()
            duration = end_time - start_time
            logger.info(f"PERF: [{name}] took {duration:.4f} seconds")
            return result
        return wrapper
    return decorator


def measure_memory_peak(name: str):
    """Décorateur pour mesurer le pic de mémoire (très basique via psutil)."""
    import psutil
    import os

    def decorator(func: Callable):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            process = psutil.Process(os.getpid())
            mem_before = process.memory_info().rss
            result = func(*args, **kwargs)
            mem_after = process.memory_info().rss
            diff = (mem_after - mem_before) / (1024 * 1024)
            logger.info(f"PERF: [{name}] Memory delta: {diff:.2f} MB")
            return result
        return wrapper
    return decorator
