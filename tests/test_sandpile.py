import numpy as np
from pytest import fixture
from unittest.mock import MagicMock, Mock
from sandpile import Table
from sandpile_gui import Window


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
def expected_table_grain_added():
    table_one_grain = np.zeros([7, 7], dtype=int)
    table_one_grain[3, 3] = 1
    return table_one_grain


@fixture
def sand_pile_with_critical_site(sand_pile_parameters):
    m, n, k = sand_pile_parameters
    table = Table(m, n, k)
    table.grid[3, 3] = k
    return table


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
def sand_pile_before_avalanche_timestep(sand_pile_parameters):
    m, n, k = sand_pile_parameters
    table = Table(m, n, k)
    table.grid = np.array([[0, 0, 0, 0, 0, 0, 0],
                           [0, 0, 0, 0, 0, 0, 0],
                           [0, 0, 0, 0, 0, 0, 0],
                           [0, 0, 3, 4, 0, 0, 0],
                           [0, 0, 0, 0, 0, 0, 0],
                           [0, 0, 0, 0, 0, 0, 0],
                           [0, 0, 0, 0, 0, 0, 0]])
    return table


@fixture
def expected_table_after_avalanche_timestep():
    return np.array([[0, 0, 0, 0, 0, 0, 0],
                     [0, 0, 0, 0, 0, 0, 0],
                     [0, 0, 0, 1, 0, 0, 0],
                     [0, 0, 4, 0, 1, 0, 0],
                     [0, 0, 0, 1, 0, 0, 0],
                     [0, 0, 0, 0, 0, 0, 0],
                     [0, 0, 0, 0, 0, 0, 0]])


@fixture
def expected_table_after_avalanche():
    return np.array([[0, 0, 0, 0, 0, 0, 0],
                     [0, 0, 0, 0, 0, 0, 0],
                     [0, 0, 1, 1, 0, 0, 0],
                     [0, 1, 0, 1, 1, 0, 0],
                     [0, 0, 1, 1, 0, 0, 0],
                     [0, 0, 0, 0, 0, 0, 0],
                     [0, 0, 0, 0, 0, 0, 0]])

# @fixture
# def gui_window(sand_pile_parameters, empty_sand_pile):
#     m, n, k = sand_pile_parameters
#     gui_window = Window.__new__(Window)
#     gui_window.M = m
#     gui_window.N = n
#     gui_window.k = k
#     gui_window.sandPile = empty_sand_pile
#     gui_window.init_ui = MagicMock()
#     gui_window.buttons = MagicMock()
#     return gui_window

# @fixture
# def sand_pile_before_avalanche_with_supercritical_site(sand_pile_parameters):
#     m, n, k = sand_pile_parameters
#     table = Table(m, n, k)
#     table.grid = np.array([[0, 0, 0, 0, 0, 0, 0],
#                            [0, 0, 0, 0, 0, 0, 0],
#                            [0, 0, 0, 4, 0, 0, 0],
#                            [0, 0, 4, 3, 4, 0, 0],
#                            [0, 0, 0, 4, 0, 0, 0],
#                            [0, 0, 0, 0, 0, 0, 0],
#                            [0, 0, 0, 0, 0, 0, 0]])
#     return table


# @fixture
# def expected_table_after_topple_timestep_into_supercritical_site():
#     return np.array([[0, 0, 0, 0, 0, 0, 0],
#                      [0, 0, 0, 1, 0, 0, 0],
#                      [0, 0, 2, 0, 2, 0, 0],
#                      [0, 1, 0, 7, 0, 1, 0],
#                      [0, 0, 2, 0, 2, 0, 0],
#                      [0, 0, 0, 1, 0, 0, 0],
#                      [0, 0, 0, 0, 0, 0, 0]])
#
#
# @fixture
# def expected_table_after_avalanche_with_supercritical_site():
#     return np.array([[0, 0, 0, 0, 0, 0, 0],
#                      [0, 0, 0, 1, 0, 0, 0],
#                      [0, 0, 2, 1, 2, 0, 0],
#                      [0, 1, 1, 3, 1, 1, 0],
#                      [0, 0, 2, 1, 2, 0, 0],
#                      [0, 0, 0, 1, 0, 0, 0],
#                      [0, 0, 0, 0, 0, 0, 0]])


def test_should_add_grain_to_center(empty_sand_pile, expected_table_grain_added):
    empty_sand_pile.add_grain()
    assert empty_sand_pile.grid.all() == expected_table_grain_added.all()


def test_should_check_critical_site(sand_pile_with_critical_site):
    assert sand_pile_with_critical_site.is_critical_site(3, 3) == True


def test_should_topple_site(sand_pile_with_critical_site, expected_table_after_single_topple):
    assert sand_pile_with_critical_site.grid.all() == expected_table_after_single_topple.all()


def test_should_execute_topple(sand_pile_before_avalanche_timestep, expected_table_after_avalanche_timestep):
    new_critical = sand_pile_before_avalanche_timestep.execute_topple(3, 3)
    output_set = set()
    output_set.add((3, 2))
    assert new_critical == output_set
    assert sand_pile_before_avalanche_timestep.grid.all() == expected_table_after_avalanche_timestep.all()


def test_should_execute_timestep(sand_pile_before_avalanche_timestep, expected_table_after_avalanche_timestep):
    input_set = set()
    input_set.add((3, 3))
    new_critical = sand_pile_before_avalanche_timestep.execute_timestep(input_set)
    output_set = set()
    output_set.add((3, 2))
    assert new_critical == output_set
    assert sand_pile_before_avalanche_timestep.grid.all() == expected_table_after_avalanche_timestep.all()


# def test_should_execute_avalanche(gui_window, sand_pile_before_avalanche_timestep, expected_table_after_avalanche):
#     gui_window.execute_avalanche(3, 3)
#     print(gui_window.sandPile.grid)
#     assert gui_window.sandPile.grid.all() == expected_table_after_avalanche


# def test_should_topple_into_supercritical_site(sand_pile_before_avalanche_with_supercritical_site,
#                                                expected_table_after_topple_timestep_into_supercritical_site):
#     total_mass_i = np.sum(sand_pile_before_avalanche_with_supercritical_site.grid)
#     sand_pile_before_avalanche_with_supercritical_site.execute_timestep()
#     assert sand_pile_before_avalanche_with_supercritical_site.grid == \
#            expected_table_after_topple_timestep_into_supercritical_site
#     total_mass_f = np.sum(sand_pile_before_avalanche_with_supercritical_site.grid)
#     # Check conservation of mass:
#     assert total_mass_i == total_mass_f


# def test_should_avalanche_with_supercritical_site(sand_pile_before_avalanche_with_supercritical_site,
#                                                   expected_table_after_avalanche_with_supercritical_site):
#     total_mass_i = np.sum(sand_pile_before_avalanche_with_supercritical_site.grid)
#     sand_pile_before_avalanche_with_supercritical_site.execute_avalanche()
#     assert sand_pile_before_avalanche_with_supercritical_site.grid == \
#            expected_table_after_avalanche_with_supercritical_site
#     total_mass_f = np.sum(sand_pile_before_avalanche_with_supercritical_site.grid)
#     # Check conservation of mass:
#     assert total_mass_i == total_mass_f
