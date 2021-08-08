import numpy as np
from pytest import fixture
from sandpile import Table


@fixture
def sand_pile_parameters():
    m = 5  # Small enough to be manageable in testing,
    n = 5  # and large enough to cover nontrivial tests
    k = 4
    return m, n, k


@fixture
def empty_sand_pile(sand_pile_parameters):
    m, n, k = sand_pile_parameters
    return Table(m, n, k)


@fixture
def sand_pile_with_critical_site(sand_pile_parameters):
    m, n, k = sand_pile_parameters
    table = Table(m, n, k)
    table.grid[3, 3] = k
    return table


@fixture
def sand_pile_before_avalanche_with_supercritical_site(sand_pile_parameters):
    m, n, k = sand_pile_parameters
    table = Table(m, n, k)
    table.grid = np.array([[0, 0, 0, 0, 0, 0, 0],
                           [0, 0, 0, 0, 0, 0, 0],
                           [0, 0, 0, 4, 0, 0, 0],
                           [0, 0, 4, 3, 4, 0, 0],
                           [0, 0, 0, 4, 0, 0, 0],
                           [0, 0, 0, 0, 0, 0, 0],
                           [0, 0, 0, 0, 0, 0, 0]])
    return table


@fixture
def expected_table_grain_added():
    table_one_grain = np.zeros([7, 7], dtype=int)
    table_one_grain[3, 3] = 1
    return table_one_grain


@fixture
def expected_table_after_single_topple():
    return np.array([[0, 0, 0, 0, 0, 0, 0],
                     [0, 0, 0, 0, 0, 0, 0],
                     [0, 0, 0, 1, 0, 0, 0],
                     [0, 0, 1, 0, 1, 0, 0],
                     [0, 0, 0, 1, 0, 0, 0],
                     [0, 0, 0, 0, 0, 0, 0],
                     [0, 0, 0, 0, 0, 0, 0]])


@fixture
def expected_table_after_topple_timestep_into_supercritical_site():
    return np.array([[0, 0, 0, 0, 0, 0, 0],
                     [0, 0, 0, 1, 0, 0, 0],
                     [0, 0, 2, 0, 2, 0, 0],
                     [0, 1, 0, 7, 0, 1, 0],
                     [0, 0, 2, 0, 2, 0, 0],
                     [0, 0, 0, 1, 0, 0, 0],
                     [0, 0, 0, 0, 0, 0, 0]])


@fixture
def expected_table_after_avalanche_with_supercritical_site():
    return np.array([[0, 0, 0, 0, 0, 0, 0],
                     [0, 0, 0, 1, 0, 0, 0],
                     [0, 0, 2, 1, 2, 0, 0],
                     [0, 1, 1, 3, 1, 1, 0],
                     [0, 0, 2, 1, 2, 0, 0],
                     [0, 0, 0, 1, 0, 0, 0],
                     [0, 0, 0, 0, 0, 0, 0]])


def test_should_add_grain_to_center(empty_sand_pile, expected_table_grain_added):
    empty_sand_pile.add_grain()
    assert empty_sand_pile.grid.all() == expected_table_grain_added.all()


def test_should_check_critical_site(sand_pile_with_critical_site):
    assert sand_pile_with_critical_site.is_critical_site(3, 3)


def test_should_topple_site(sand_pile_with_critical_site, expected_table_after_single_topple):
    sand_pile_with_critical_site.topple(3, 3)
    assert sand_pile_with_critical_site.grid.all() == expected_table_after_single_topple.all()


# def test_should_topple_into_supercritical_site(sand_pile_before_avalanche_with_supercritical_site,
#                                                expected_table_after_topple_timestep_into_supercritical_site):
#     total_mass_i = np.sum(sand_pile_before_avalanche_with_supercritical_site.grid)
#     sand_pile_before_avalanche_with_supercritical_site.execute_timestep()
#     assert sand_pile_before_avalanche_with_supercritical_site.grid == \
#            expected_table_after_topple_timestep_into_supercritical_site
#     total_mass_f = np.sum(sand_pile_before_avalanche_with_supercritical_site.grid)
#     # Check conservation of mass:
#     assert total_mass_i == total_mass_f
#
#
# def test_should_avalanche_with_supercritical_site(sand_pile_before_avalanche_with_supercritical_site,
#                                                   expected_table_after_avalanche_with_supercritical_site):
#     total_mass_i = np.sum(sand_pile_before_avalanche_with_supercritical_site.grid)
#     sand_pile_before_avalanche_with_supercritical_site.execute_avalanche()
#     assert sand_pile_before_avalanche_with_supercritical_site.grid == \
#            expected_table_after_avalanche_with_supercritical_site
#     total_mass_f = np.sum(sand_pile_before_avalanche_with_supercritical_site.grid)
#     # Check conservation of mass:
#     assert total_mass_i == total_mass_f
