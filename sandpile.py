# Bak-Tang-Wiesenfeld sandpile model
import numpy as np
# import scipy as sp
# import random as random
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit
from math import ceil


class Table():
    def __init__(self, M, N, k):
        self.M = M  # number of rows
        self.N = N  # number of columns
        self.k = k  # critical parameter
        # Initialise M by N grid of zeroes:
        self.grid = np.zeros([M+2, N+2], dtype=int)  # extra rows and columns around edges for overflow

    def add_grain(self, *args):
        # Function to add a single grain of sand to the table in a random site (m,n)
        # optional args for position of grain
        # m = random.randint(1,self.M)
        # n = random.randint(1,self.N)
        # self.grid[m,n] += 1
        # OR dropping the grain in the centre of the grid:
        if len(args) == 0:  # add grain in random position
            self.grid[int(ceil((self.M + 1)/2)), int(ceil((self.N + 1)/2))] += 1
        else:
            self.grid[args[0], args[1]] += 1

    def check_site(self, m, n):
        # Checks if any avalanches will occur at (m,n)
        if self.grid[m, n] == self.k:  # avalanche
            # print("avalanche")
            self.m = m
            self.n = n
            return True
        else:  # No avalanche
            return False

    def execute_avalanche(self, m, n):
        # Function to execute the avalanche starting at the point (m,n)
        self.s = 0  # Avalanche size - number of grains displaced during avalanche
        self.t = 0  # Avalanche lifetime- nuber of timetsteps taken to relax to critical state
        self.a = 1  # Avalanche area- number of unique sitest toppled
        self.r = 0  # Avalanche radius- max number of sites away from the initial point that the avalanche reaches
        originPt = [m, n]  # Avalanche starts at m,n
        siteDistances = []  # A list of the distances of toppling sites from origin
        topplePts = [[m, n]]  # A list for storing surrounding pts which need to be toppled
        toppleSites = [[m,n]]  # Sites to be toppled
        while topplePts != []:
            for Pt in topplePts:
                i, j = Pt[0], Pt[1]
                self.topple(i, j)
                if Pt not in toppleSites:  # A list of unique pts toppled in the avalance
                    toppleSites.append([i, j])
                distance = abs(originPt[0]-i) + abs(originPt[1] -j) # x+y distance from origin to topple pt.
                siteDistances.append(distance)
                topplePts = topplePts[1:]  # remove point just toppled
                self.s += 4  # 2d=4 grains displaced per topple
                surroundingPts = [[i+1, j], [i-1, j], [i, j+1], [i, j-1]]
                for site in surroundingPts:  # Now check all cells surrounding, to see if avalanches will occur
                    r,c = site[0], site[1]
                    if r == 0 or r == self.M + 1 or c == 0 or c == self.N + 1:  # If sand fell off table
                        pass
                    elif self.check_site(r, c):
                        topplePts.append([r, c])
                # print(self.grid)
            self.t += 1     # Count a timestep
        # End of avalanche. Return statistics
        self.a = len(toppleSites)
        self.r = max(siteDistances)
        return([self.s, self.t, self.a, self.r])

    def topple(self, m, n):
        # Function to perform a toppling process at the grid point (m,n)
        self.surrounds = [[m+1, n], [m-1, n], [m, n+1], [m, n-1]]
        self.grid[m, n] -= 4  # 4 grains topple
        for pt in self.surrounds:
            self.grid[pt[0], pt[1]] += 1  # surroundings gain a grain


def get_freq_data(data):
    # Sorts data ( an array of statistics) into unique data points and the number of each data point
    d = np.array(data)
    freq = np.bincount(d)
    uniqueVal = np.nonzero(freq)[0]
    d1 = np.vstack((uniqueVal, freq[uniqueVal])).T
    return([d1[:, 0], d1[:, 1]])


def plot_histogram(data, observable, xunits):
    # plots a histogram of the data (array of stats) of an ["observable","units of observable"]
    plt.hist(data, max(data))
    plt.title("Avalanche %s for grid size = %d x %d" %(observable, gridSize[0], gridSize[1]))
    plt.xlabel("%s (%s)" %(observable, xunits))
    plt.ylabel("Number of avalanches")
    plt.show()


def loglog_plot_stats(data, observable, xunits):
    # Produces loglog plot of the distribution of an observables data
    # Data is an array of stats, observable and xunits are strings
    [x, freq] = get_freq_data(data)
    plt.loglog(x, freq, '.', basex=10)
    plt.title("Avalanche distribution for %s (Grid size: %dx%d )" %(observable, gridSize[0], gridSize[1]))
    plt.ylabel("Number of avalanches")
    plt.xlabel("%s (%s)"%(observable, xunits))
    plt.show()


def power_law_fit_plot(xdata, ydata, xylegend, unitsLegend):
    # Power law fits between xdata and ydata
    # xylegend = ["name of xdata","name of ydata"],#units legend=[units of xdata,units of ydata]
    xData = np.array(xdata)
    params, pcov = curve_fit(power_law_func, xData, ydata)
    plt.plot(xData, ydata, ".")
    plt.plot(np.sort(xData), power_law_func(np.sort(xData), *params), '-')
    plt.legend(["Avalanche data", "Power- law fit: x^%5.3f" %(params[1])])
    plt.title("Relationship between %s and %s" %(xylegend[0], xylegend[1]))
    plt.xlabel("%s (%s)" %(xylegend[0], unitsLegend[0]))
    plt.ylabel("%s (%s)" %(xylegend[1], unitsLegend[1]))
    plt.show()


def power_law_func(x, a, b):  # power law function to fit data
    return a * x**b


def exp_func(x, a, b, c):
    return a*np.exp(-b*x)


if __name__ == '__main__':
    legend = []
    allDensities = []  # array for collecting grid densities of sand
    plotOn = 1  # 0 for no plots, 1 for plots to be shown
    for gridSize in [[11, 11]]:
        legend.append("%d x %d grid" % (gridSize[0], gridSize[1]))
        sandpile = Table(gridSize[0], gridSize[1], 4)
        # print(sandpile.grid)
        totalGrains = 1000  # Number of grains to be dropped
        time = 0  # count timesteps
        size = []     # Statistics to be collected
        lifetime = []
        area = []
        radius = []
        density = []
        # Loop over number of grains to be dropped:
        for grain in range(totalGrains):
            sandpile.add_grain()
            time += 1  # add timestep for each grain dropped
            sandGrid = sandpile.grid[1:sandpile.M+1, 1:sandpile.N+1]  # grid without edges
            m, n = np.unravel_index(sandGrid.argmax(), sandGrid.shape)  # Find site with max grains:
            m = m + 1
            n = n + 1
            # Check if avalanche will occur:
            if sandpile.check_site(m, n):
                stats = sandpile.execute_avalanche(m, n)  # Avalanche occurs at (m,n)
                # store statistics for avalanche:
                size.append(stats[0])
                lifetime.append(stats[1])
                area.append(stats[2])
                radius.append(stats[3])
                density.append(np.average(sandpile.grid[1:sandpile.M+1, 1:sandpile.N+1]))
                totalSteps = time + sandpile.t
        allDensities.append(density)


        #####################
        #Plots:
        if plotOn:
            obsLegend = ["Size", "Lifetime", "Area", "Radius"]
            unitsLegend = ["number of sites", "time units", "number of sites", "number of sites"]  # units for each observable
            # Histogram plots and loglog plots for observables vs number avalanches:
            i = 0
            for stat in [size, lifetime, area, radius]:
                plot_histogram(stat, obsLegend[i], unitsLegend[i])
                loglog_plot_stats(stat, obsLegend[i], unitsLegend[i])
                i += 1

            # Power law fit of observables vs number of avalanches
            i = 0
            for stat in [size, lifetime, area]:
                [stats, freqs] = get_freq_data(stat)
                power_law_fit_plot(stats, freqs, [obsLegend[i], "Number of avalanches"], [unitsLegend[i],"Number"])
                i += 1

            # Consider radius separately:  remove zero term from radius in order to get power law fit
            [radii, freqs] = get_freq_data(radius)
            radii, freqs  = radii[1:], freqs[1:]
            power_law_fit_plot(radii,freqs, [obsLegend[3], "Number of avalanches"], [unitsLegend[i], "Number"])
            # try exponential fit for radius instead:
            params, pcov = curve_fit(exp_func, radii, freqs)
            plt.plot(radii, freqs, ".")
            plt.plot(np.sort(radii), exp_func(np.sort(radii), *params), '-')
            plt.legend(["Avalanche data", "Exponential fit: ~ exp(-%5.3fx)" %(params[1])])
            plt.title("Scaling law between %s and %s" %(obsLegend[3], "Number of avalanches"))
            plt.xlabel("%s (%s)" %(obsLegend[3], unitsLegend[3]))
            plt.ylabel("Number of avalanches")
            plt.show()

            # Power law fits of size vs other observables
            [sizes, freqs] = get_freq_data(size)
            i = 1
            for stat in [lifetime, area, radius]:
                [stats, statFreqs] = get_freq_data(stat)
                power_law_fit_plot(size, stat, [obsLegend[0], obsLegend[i]], [unitsLegend[0], unitsLegend[i]])  # correlations between  each variable and avalanche size :
                i += 1
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
    sandGrid = sandpile.grid[1:sandpile.M+1, 1:sandpile.N+1]  # grid without edges
    plt.imshow(sandGrid, interpolation='nearest', cmap='Blues')
    plt.title("Surface Density of Sandpile (Number of Grains: %d)" %(totalGrains))
    plt.colorbar()
    plt.show()
    #############################
