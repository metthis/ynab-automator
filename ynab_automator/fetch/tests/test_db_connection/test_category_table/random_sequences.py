from __future__ import annotations
import random


def random_sample(start: int, end: int, size: int) -> list:
    return random.sample(range(start, end), k=size)


def get_complementary_randomised_seqs_of_ints(
    start: int, end: int
) -> tuple[list, list]:
    length = end - start
    if length % 2:
        raise ValueError("Difference of end and start has to be even.")

    seq_1 = random_sample(start=start, end=end, size=length // 2)
    seq_2 = set(range(start, end)) - set(seq_1)
    seq_2 = list(seq_2)
    random.shuffle(seq_2)

    if not len(seq_1) == len(seq_2):
        message = f"The two sequences are supposed to be the same length but are {len(seq_1)} and {len(seq_2)} long."
        raise ValueError(message)

    return tuple(seq_1), tuple(seq_2)
