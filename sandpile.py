"""Bak-Tang-Wiesenfeld sandpile model"""

import numpy as np
# import scipy as sp
# import random as random
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit
from math import ceil
from plotting_helper import get_freq_data, plot_histogram, loglog_plot_stats, \
    power_law_fit_plot, power_law_func, exp_func


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
        # add grain in random position:
        # self.grid[random.randint(1,self.M), random.randint(1,self.N)] += 1
        if len(args) == 0:  # Drop grain in the centre of the grid:
            self.grid[int(ceil((self.M + 1) / 2)), int(ceil((self.N + 1) / 2))] += 1
        else:
            self.grid[args[0], args[1]] += 1

    def check_site(self, i_check, j_check):
        """Checks if any avalanches will occur at (m,n)"""
        if self.grid[i_check, j_check] == self.k:  # avalanche
            return True
        else:  # No avalanche
            return False

    def topple(self, i_topple, j_topple):
        """Perform a toppling process at the grid point (m,n)"""
        surrounds = [[i_topple + 1, j_topple], [i_topple - 1, j_topple], [i_topple, j_topple + 1],
                     [i_topple, j_topple - 1]]
        self.grid[i_topple, j_topple] -= 4  # 4 grains topple
        for pt in surrounds:
            self.grid[pt[0], pt[1]] += 1  # surroundings gain a grain

    # TODO: Subclass for Avalanche; new instance can be made when new grain is added (by gui module)
    #       methods: execute_timestep.
    #       attributes:  is_toppling (bool) for monitoring whether avalanche is active?
    #                    critical_sites? (list/queue?) to be toppled in a single time step

    def execute_avalanche(self, i_0, j_0):
        """Execute the avalanche starting at the point (i_0,j_0)"""
        topple_pts = [[i_0, j_0]]  # A list for storing surrounding pts which need to be toppled
        topple_sites = [[i_0, j_0]]  # Sites to be toppled  # TODO: Would a list of tuples be more efficient?
        a_time = 0
        while topple_pts:  # TODO: manage topple pts by timestep... move this for loop to a method execute_timestep?
            for pt in topple_pts:
                i, j = pt
                self.topple(i, j)
                if pt not in topple_sites:  # A list of unique pts toppled in the avalanche
                    topple_sites.append([i, j])
                topple_pts = topple_pts[1:]  # remove point just toppled  # TODO: use .pop(), .push() for a queue
                surrounding_pts = [[i + 1, j], [i - 1, j], [i, j + 1], [i, j - 1]]
                for site in surrounding_pts:  # Now check all cells surrounding, to see if avalanches will occur
                    r, c = site
                    # if r == 0 or r == self.M + 1 or c == 0 or c == self.N + 1:  # If sand fell off table
                    if (r in [0, self.M + 1]) or (c in [0, self.N + 1]):
                        pass
                    elif self.check_site(r, c):
                        topple_pts.append([r, c])
            a_time += 1  # Count a time-step
        return

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
                    elif self.check_site(r, c):
                        topple_pts.append([r, c])
            a_time += 1  # Count a time-step
        # End of avalanche. Return statistics
        a_area = len(topple_sites)  # Avalanche area- number of unique sites toppled
        a_radius = max(
            site_distances)  # Avalanche radius- max number of sites away from initial point that the avalanche reaches
        return {'size': a_size, 'lifetime': a_time, 'area': a_area, 'radius': a_radius}


def main():
    legend = []
    allDensities = []  # array for collecting grid densities of sand
    plotOn = 1  # 0 for no plots, 1 for plots to be shown
    for grid_config in [[11, 11]]:
        legend.append(f"{grid_config[0]} x {grid_config[1]} grid")
        sandpile = Table(grid_config[0], grid_config[1], 4)
        # print(sandpile.grid)
        totalGrains = 1000  # Number of  grains to be dropped
        size = []  # Statistics to be collected
        lifetime = []
        area = []
        radius = []
        density = []
        # Loop over number of grains to be dropped:
        for grain in range(totalGrains):
            sandpile.add_grain()
            sandGrid = sandpile.grid[1:sandpile.M + 1, 1:sandpile.N + 1]  # grid without edges
            m, n = np.unravel_index(sandGrid.argmax(), sandGrid.shape)  # Find site with max grains:
            m += 1
            n += 1
            # Check if avalanche will occur:
            if sandpile.check_site(m, n):
                stats = sandpile.execute_avalanche_with_stats(m, n)  # Avalanche occurs at (m,n)
                # store statistics for avalanche:
                size.append(stats['size'])
                lifetime.append(stats['lifetime'])
                area.append(stats['area'])
                radius.append(stats['radius'])
                density.append(np.average(sandpile.grid[1:sandpile.M + 1, 1:sandpile.N + 1]))
                totalSteps = grain + 1 + stats['lifetime']
        allDensities.append(density)

        #####################
        # Plots:
        if plotOn:
            obsLegend = ["Size", "Lifetime", "Area", "Radius"]
            units_legend = ["number of sites", "time units", "number of sites", "number of sites"]
            # Histogram plots and loglog plots for observables vs number avalanches:
            for i, stat in enumerate([size, lifetime, area, radius]):
                plot_histogram(grid_config, stat, obsLegend[i], units_legend[i])
                loglog_plot_stats(grid_config, stat, obsLegend[i], units_legend[i])

            # Power law fit of observables vs number of avalanches
            for i, stat in enumerate([size, lifetime, area]):
                [stats, freqs] = get_freq_data(stat)
                power_law_fit_plot(stats, freqs, [obsLegend[i], "Number of avalanches"], [units_legend[i], "Number"])

            # Consider radius separately:  remove zero term from radius in order to get power law fit
            [radii, freqs] = get_freq_data(radius)
            radii, freqs = radii[1:], freqs[1:]
            power_law_fit_plot(radii, freqs, [obsLegend[3], "Number of avalanches"], [units_legend[i], "Number"])
            # try exponential fit for radius instead:
            params, p_cov = curve_fit(exp_func, radii, freqs)
            plt.plot(radii, freqs, ".")
            plt.plot(np.sort(radii), exp_func(np.sort(radii), *params), '-')
            plt.legend(["Avalanche data", "Exponential fit: ~ exp(-%5.3fx)" % (params[1])])
            plt.title(f"Scaling law between {obsLegend[3]} and Number of avalanches")
            plt.xlabel(f"{obsLegend[3]} ({units_legend[3]})")
            plt.ylabel("Number of avalanches")
            plt.show()

            # Power law fits of size vs other observables
            [sizes, freqs] = get_freq_data(size)
            for i, stat in enumerate([lifetime, area, radius], 1):
                [stats, stat_freqs] = get_freq_data(stat)
                # correlations between  each variable and avalanche size :
                power_law_fit_plot(size, stat, [obsLegend[0], obsLegend[i]], [units_legend[0], units_legend[i]])
            ##############

    # Sand densities plots
    if plotOn:
        for d in allDensities:
            plt.plot(d)
        plt.title("Density of sand on board")
        plt.xlabel("Time")
        plt.ylabel("Sand Density")
        plt.legend(legend)
        plt.show()

        # Grid surface plot of final configuration
    sandGrid = sandpile.grid[1:sandpile.M + 1, 1:sandpile.N + 1]  # grid without edges
    plt.imshow(sandGrid, interpolation='nearest', cmap='Blues')
    plt.title(f"Surface Density of Sandpile (Number of Grains: {totalGrains})")
    plt.colorbar()
    plt.show()
    #############################


if __name__ == '__main__':
    main()
