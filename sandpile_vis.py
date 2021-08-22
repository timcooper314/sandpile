import time
import random as random
import numpy as np
from tkinter import Tk, Entry

import sandpile


class Window:
    def __init__(self):
        self.root = Tk()
        self.M = 15
        self.N = 15
        self.k = 4
        self.sandPile = sandpile.Table(self.M, self.N, self.k)
        self.init_ui()
        self.start_click()
        self.root.mainloop()

    def init_ui(self):
        self.root.title("Abelian Sandpile")
        self.create_grid_layout()
        self.set_colours()

    def create_grid_layout(self):
        self.entries = []
        for r in range(self.M):
            for c in range(self.N):
                self.entries.append(Entry(self.root, text="", width=2))
                self.entries[r*self.N + c].grid(row=r, column=c, padx=0, pady=0, ipadx=0, ipady=0)

    def set_colours(self):
        if self.k == 4:
            self.colours = {0: "white", 1: "lightblue", 2: "#619bcc", 3: "#316a9a", 4: "#255075", 5: "#4169E1",
                            6: "#0F52BA", 7: "#0818A8"}
        elif self.k == 8:
            self.colours = {0: "white", 1: "lightblue", 2: "#89CFF0", 3: "#0096FF",
                            4: "#1F51FF", 5: "#4169E1", 6: "#0F52BA", 7: "#0818A8",
                            8: "#1F51FF", 9: "#4169E1", 10: "#0F52BA", 11: "#0818A8"}
        else:
            self.colours = {0: "white"}
            for c in range(1, self.k + 4):
                self.colours[c] = "#" + ''.join([random.choice('0123456789ABCDEF') for _ in range(6)])

    def update_grid(self, i, j):
        self.sandPile.add_grain(i + 1, j + 1)
        if self.sandPile.is_critical_site(i + 1, j + 1):
            self.execute_avalanche(i + 1, j + 1)
        else:  # no avalanche
            self.entries[i * self.N + j].configure(background=self.colours[self.sandPile.grid[i + 1][j + 1]])
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
                self.entries[i * self.N + j].configure(bg=self.colours[self.sandPile.grid[i + 1][j + 1]])
        self.root.update()

    def start_click(self):
        total_grains = 500
        print("Simulating grains dropped in center")
        pos_i = self.M // 2 * np.ones(total_grains, dtype=int)
        pos_j = self.N // 2 * np.ones(total_grains, dtype=int)
        for grain in range(total_grains):
            self.update_grid(pos_i[grain], pos_j[grain])
            self.update_button_colours()


def main():
    app = Window()


if __name__ == '__main__':
    main()
