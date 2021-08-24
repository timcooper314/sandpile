import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit
from plotting_helper import get_freq_data, plot_histogram, loglog_plot_stats, \
    power_law_fit_plot, power_law_func, exp_func
import sandpile


def main():
    legend = []
    allDensities = []  # array for collecting grid densities of sand
    plotOn = 1  # 0 for no plots, 1 for plots to be shown
    for grid_config in [[11, 11]]:
        legend.append(f"{grid_config[0]} x {grid_config[1]} grid")
        sand_pile = sandpile.Table(grid_config[0], grid_config[1], 4)
        # print(sand_pile.grid)
        totalGrains = 1000  # Number of  grains to be dropped
        size = []  # Statistics to be collected
        lifetime = []
        area = []
        radius = []
        density = []
        # Loop over number of grains to be dropped:
        for grain in range(totalGrains):
            sand_pile.add_grain()
            sandGrid = sand_pile.grid[1:sand_pile.M + 1, 1:sand_pile.N + 1]  # grid without edges
            m, n = np.unravel_index(sandGrid.argmax(), sandGrid.shape)  # Find site with max grains:
            m += 1
            n += 1
            # Check if avalanche will occur:
            if sand_pile.is_critical_site(m, n):
                stats = sand_pile.execute_avalanche_with_stats(m, n)  # Avalanche occurs at (m,n)
                # store statistics for avalanche:
                size.append(stats['size'])
                lifetime.append(stats['lifetime'])
                area.append(stats['area'])
                radius.append(stats['radius'])
                density.append(np.average(sand_pile.grid[1:sand_pile.M + 1, 1:sand_pile.N + 1]))
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
    sandGrid = sand_pile.grid[1:sand_pile.M + 1, 1:sand_pile.N + 1]  # grid without edges
    plt.imshow(sandGrid, interpolation='nearest', cmap='Blues')
    plt.title(f"Surface Density of Sandpile (Number of Grains: {totalGrains})")
    plt.colorbar()
    plt.show()
    #############################


if __name__ == '__main__':
    main()
