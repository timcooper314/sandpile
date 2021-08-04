import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit
from math import ceil


def get_freq_data(data):
    """Sorts data ( an array of statistics) into unique data points and the number of each data point"""
    freq = np.bincount(np.array(data))
    unique_val = np.nonzero(freq)[0]
    d1 = np.vstack((unique_val, freq[unique_val])).T
    return [d1[:, 0], d1[:, 1]]


def plot_histogram(grid_config, data, observable, x_units):
    """Plots a histogram of data (array of stats) of an ["observable", "units of observable"]"""
    plt.hist(data, max(data))
    plt.title(f"Avalanche {observable} for grid size = {grid_config[0]} x {grid_config[1]}")
    plt.xlabel(f"{observable} ({x_units})")
    plt.ylabel("Number of avalanches")
    plt.show()


def loglog_plot_stats(grid_config, data, observable, x_units):
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
