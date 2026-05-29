"""Размер игрового поля (2×2 или 3×3)."""

GRID_SIZE_MIN = 2
GRID_SIZE_MAX = 3


def color_count_for_grid(grid_size: int) -> int:
    if grid_size not in (GRID_SIZE_MIN, GRID_SIZE_MAX):
        raise ValueError(f"Unsupported grid size: {grid_size}")
    return grid_size * grid_size
