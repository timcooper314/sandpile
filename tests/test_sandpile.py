import numpy as np
from pytest import fixture
from sandpile import Table


@fixture
def sand_pile_parameters():
    m = 5
    n = 5
    k = 4
    return m, n, k


@fixture
def sand_pile_table(sand_pile_parameters):
    m, n, k = sand_pile_parameters
    return Table(m, n, k)


@fixture
def expected_table_grain_added():
    table_one_grain = np.zeros([7, 7], dtype=int)
    table_one_grain[3, 3] = 1
    return table_one_grain


def test_should_add_grain_to_center(sand_pile_table, expected_table_grain_added):
    sand_pile_table.add_grain()
    assert sand_pile_table.grid[3, 3] == expected_table_grain_added[3, 3]
