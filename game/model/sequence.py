"""Генерация последовательности цветов."""

import random

from game.model.field import color_count_for_grid


def generate_next_color(
    sequence: list[int],
    color_count: int,
    avoid_patterns: bool = True,
) -> int:
    candidates = list(range(color_count))
    if avoid_patterns and len(sequence) >= 3:
        a, b, c = sequence[-3], sequence[-2], sequence[-1]
        forbidden: set[int] = set()
        if a == c and a != b:
            forbidden.add(b)
        candidates = [x for x in candidates if x not in forbidden] or candidates
    return random.choice(candidates)


def append_color(sequence: list[int], color_count: int) -> None:
    sequence.append(generate_next_color(sequence, color_count))
