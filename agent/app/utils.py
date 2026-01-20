import random


def maybe_throw(probability: float, exception: Exception) -> None:
    if random.random() < probability:
        raise exception
