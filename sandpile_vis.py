import time
import random as random
import numpy as np
from tkinter import Tk, Entry
import palettable.cmocean.sequential as pcolours

import sandpile


class Window:
    def __init__(self):
        self.root = Tk()
        self.M = 25
        self.N = 25
        self.k = 4
        self.colours = ['white'] + pcolours.Deep_5.hex_colors
        self.total_grains = 1000
        self.sandPile = sandpile.Table(self.M, self.N, self.k)
        self.init_ui()
        self.start_click()
        self.root.mainloop()

    def init_ui(self):
        self.root.title("Abelian Sandpile")
        self.create_grid_layout()

    def create_grid_layout(self):
        self.entries = []
        for r in range(self.M):
            for c in range(self.N):
                self.entries.append(Entry(self.root, text="", width=2, bd=0))
                self.entries[r*self.N + c].grid(row=r, column=c, padx=0, pady=0, ipadx=0, ipady=0),

    def update_grid(self, i, j):
        self.sandPile.add_grain(i + 1, j + 1)
        if self.sandPile.is_critical_site(i + 1, j + 1):
            self.execute_avalanche(i + 1, j + 1)
        else:  # no avalanche
            self.entries[i * self.N + j].configure(background=self.colours[min(self.k, self.sandPile.grid[i + 1][j + 1])])
        self.update_button_colours()
        self.root.update()

    def execute_avalanche(self, i_c, j_c):
        """Initiates avalanche at (i_c, j_c).
        Loops over the toppling of piles until grid hits a 'steady' state"""
        toppling_sites = {(i_c, j_c)}
        while toppling_sites:
            new_critical_sites = self.sandPile.execute_timestep(toppling_sites)
            toppling_sites = new_critical_sites
            self.update_button_colours()

    def update_button_colours(self):
        for i in range(self.M):
            for j in range(self.N):
                self.entries[i * self.N + j].configure(bg=self.colours[min(self.k, self.sandPile.grid[i + 1][j + 1])])
        self.root.update()

    def start_click(self):
        print("Simulating grains dropped in center")
        for _ in range(self.total_grains):
            self.update_grid(self.M // 2, self.N // 2)


def main():
    app = Window()


if __name__ == '__main__':
    main()
