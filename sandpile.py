"""Bak-Tang-Wiesenfeld sandpile model"""

import numpy as np
from math import ceil


def surrounding_pts(i, j):
    return [(i + 1, j), (i - 1, j), (i, j + 1), (i, j - 1)]


class Table:
    def __init__(self, M, N, k):
        self.M = M  # number of rows
        self.N = N  # number of columns
        self.k = k  # critical parameter
        # Initialise M by N grid of zeroes:  # TODO: Get rid of the zero padding?
        self.grid = np.zeros([M + 2, N + 2], dtype=int)  # extra rows and columns around edges for overflow

    def add_grain(self, *args):
        """Function to add a single grain of sand to the table.
        Optional args for position of grain"""
        if len(args) == 0:  # Drop grain in the centre of the grid:
            self.grid[int(ceil((self.M + 1) / 2)), int(ceil((self.N + 1) / 2))] += 1
        else:
            self.grid[args[0], args[1]] += 1

    def is_critical_site(self, i_check, j_check):
        """Checks if any avalanches will occur at (m,n)"""
        return self.grid[i_check, j_check] >= self.k  # avalanche

    def topple(self, i_topple, j_topple):
        """Perform a toppling process at the grid point (m,n)"""
        self.grid[i_topple, j_topple] -= 4  # 4 grains topple
        for pt in surrounding_pts(i_topple, j_topple):
            self.grid[pt[0], pt[1]] += 1  # surroundings gain a grain

    # TODO: Subclass for Avalanche; new instance can be made when new grain is added (by gui module)
    #       methods: execute_timestep.
    #       attributes:  is_toppling (bool) for monitoring whether avalanche is active?
    #                    critical_sites? (list/queue?) to be toppled in a single time step

    def execute_topple(self, i, j):
        """Called once initial toppling point has been added, this will topple the next point in the queue and
        Will add to the toppling queue any points that have hit the toppling point"""
        new_critical_sites = set()
        if self.is_critical_site(i, j):  # if the point is in the critical point, topple it and check surrounds
            self.topple(i, j)

            for site in surrounding_pts(i, j):  # Now check all cells surrounding, to see if avalanches will occur
                r, c = site
                if not (r == 0 or r == self.M + 1 or c == 0 or c == self.N + 1):
                    if self.is_critical_site(r, c):
                        new_critical_sites.add((r, c))  # Re-Adding a point shouldn't cause issue, as it is checked
        return new_critical_sites

    def execute_timestep(self, sites_to_be_toppled):
        """Topples sites within a single timestep, and returns new critical sites
        which will be need to be toppled in the next timestep."""
        next_timestep_critical_sites = set()
        for site in sites_to_be_toppled:  # order doesn't matter
            new_critical_sites = self.execute_topple(site[0], site[1])
            next_timestep_critical_sites = next_timestep_critical_sites.union(new_critical_sites)
        return next_timestep_critical_sites

    def execute_avalanche_with_stats(self, i_0, j_0):
        """Execute the avalanche starting at the point (m,n)"""
        a_size = 0  # Avalanche size - number of grains displaced during avalanche
        a_time = 0  # Avalanche lifetime- number of time-steps taken to relax to critical state
        origin_pt = [i_0, j_0]  # Avalanche starts a t (i_0, j_0)
        site_distances = []  # A list of the distances of toppling sites from origin
        topple_pts = [[i_0, j_0]]  # A list for storing surrounding pts which need to be toppled
        topple_sites = [[i_0, j_0]]  # Sites to be toppled
        while topple_pts:
            for pt in topple_pts:
                i, j = pt
                self.topple(i, j)
                if pt not in topple_sites:  # A list of unique pts toppled in the avalanche
                    topple_sites.append([i, j])
                distance = abs(origin_pt[0] - i) + abs(origin_pt[1] - j)  # x+y distance from origin to topple pt.
                site_distances.append(distance)
                topple_pts = topple_pts[1:]  # remove point just toppled
                a_size += 4  # 2d=4 grains displaced per topple
                surrounding_pts = [[i + 1, j], [i - 1, j], [i, j + 1], [i, j - 1]]
                for site in surrounding_pts:  # Now check all cells surrounding, to see if avalanches will occur
                    r, c = site
                    if r == 0 or r == self.M + 1 or c == 0 or c == self.N + 1:  # If sand fell off table
                        pass
                    elif self.is_critical_site(r, c):
                        topple_pts.append([r, c])
            a_time += 1  # Count a time-step
        # End of avalanche. Return statistics
        a_area = len(topple_sites)  # Avalanche area- number of unique sites toppled
        a_radius = max(
            site_distances)  # Avalanche radius- max number of sites away from initial point that the avalanche reaches
        return {'size': a_size, 'lifetime': a_time, 'area': a_area, 'radius': a_radius}
