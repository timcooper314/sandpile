"""Bak-Tang-Wiesenfeld sandpile model"""

import numpy as np
# import scipy as sp
# import random as random
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit
from math import ceil


class Table:
    def __init__(self, M, N, k):
        self.M = M  # number of rows
        self.N = N  # number of columns
        self.k = k  # critical parameter
        # Initialise M by N grid of zeroes:
        self.grid = np.zeros([M + 2, N + 2], dtype=int)  # extra rows and columns around edges for overflow

    def add_grain(self, *args):
        # Function to add a single grain of sand to the table in a random site (m,n)
        # optional args for position of grain
        # m = random.randint(1,self.M)
        # n = random.randint(1,self.N)
        # self.grid[m,n] += 1
        # OR dropping the grain in the centre of the grid:
        if len(args) == 0:  # add grain in random position
            self.grid[int(ceil((self.M + 1) / 2)), int(ceil((self.N + 1) / 2))] += 1
        else:
            self.grid[args[0], args[1]] += 1

    def check_site(self, i_check, j_check):
        """Checks if any avalanches will occur at (m,n)"""
        if self.grid[i_check, j_check] == self.k:  # avalanche
            return True
        else:  # No avalanche
            return False

    def execute_avalanche(self, i_0, j_0):
        """Execute the avalanche starting at the point (m,n)"""
        a_size = 0  # Avalanche size - number of grains displaced during avalanche
        a_time = 0  # Avalanche lifetime- number of time-steps taken to relax to critical state
        origin_pt = [i_0, j_0]  # Avalanche starts at (i_0, j_0)
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
            site_distances)  # Avalanche radius- max number of sites away from the initial point that the avalanche reaches
        return {'size': a_size, 'lifetime': a_time, 'area': a_area, 'radius': a_radius}

    def topple(self, i_topple, j_topple):
        """Perform a toppling process at the grid point (m,n)"""
        surrounds = [[i_topple + 1, j_topple], [i_topple - 1, j_topple], [i_topple, j_topple + 1],
                     [i_topple, j_topple - 1]]
        self.grid[i_topple, j_topple] -= 4  # 4 grains topple
        for pt in surrounds:
            self.grid[pt[0], pt[1]] += 1  # surroundings gain a grain


def get_freq_data(data):
    """Sorts data ( an array of statistics) into unique data points and the number of each data point"""
    freq = np.bincount(np.array(data))
    unique_val = np.nonzero(freq)[0]
    d1 = np.vstack((unique_val, freq[unique_val])).T
    return [d1[:, 0], d1[:, 1]]


def plot_histogram(data, observable, x_units):
    """Plots a histogram of data (array of stats) of an ["observable", "units of observable"]"""
    plt.hist(data, max(data))
    plt.title(f"Avalanche {observable} for grid size = {grid_config[0]} x {grid_config[1]}")
    plt.xlabel(f"{observable} ({x_units})")
    plt.ylabel("Number of avalanches")
    plt.show()


def loglog_plot_stats(data, observable, x_units):
    """Produces loglog plot of the distribution of an observables data
    Data is an array of stats, observable and x_units are strings"""
    [x, freq] = get_freq_data(data)
    plt.loglog(x, freq, '.', basex=10)
    plt.title(f"Avalanche distribution for {observable} (Grid size: {grid_config[0]}x{grid_config[1]} )")
    plt.ylabel("Number of avalanches")
    plt.xlabel(f"{observable} ({x_units})")
    plt.show()


def power_law_fit_plot(x_data, y_data, xy_legend, units_legend):
    """Power law fits between x_data and y_data
    xy_legend = ["name of x_data","name of y_data"], #units legend=[units of x_data,units of y_data]"""
    xData = np.array(x_data)
    params, p_cov = curve_fit(power_law_func, xData, y_data)
    plt.plot(xData, y_data, ".")
    plt.plot(np.sort(xData), power_law_func(np.sort(xData), *params), '-')
    plt.legend(["Avalanche data", "Power-law fit: x^%5.3f" % (params[1])])
    plt.title(f"Relationship between {xy_legend[0]} and {xy_legend[1]}")
    plt.xlabel(f"{xy_legend[0]} ({units_legend[0]})")
    plt.ylabel(f"{xy_legend[1]} ({units_legend[1]})")
    plt.show()


def power_law_func(x, a, b):
    return a * x ** b


def exp_func(x, a, b):
    return a * np.exp(-b * x)


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
                stats = sandpile.execute_avalanche(m, n)  # Avalanche occurs at (m,n)
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
                plot_histogram(stat, obsLegend[i], units_legend[i])
                loglog_plot_stats(stat, obsLegend[i], units_legend[i])

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
