import sys
import time
import random as random
import numpy as np
import matplotlib.pyplot as plt
from functools import partial

from PyQt5.QtWidgets import QApplication, QHBoxLayout, QVBoxLayout, QGroupBox, QGridLayout, \
    QPushButton, QRadioButton, QLineEdit, QDialog, QMainWindow

import sandpile


class Window(QDialog):  # ):#QMainWindow):
    def __init__(self):
        super().__init__()
        self.M = 25
        self.N = 25
        self.k = 4
        self.sandPile = sandpile.Table(self.M, self.N, self.k)
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Abelian Sandpile")
        self.setGeometry(100, 100, 300, 300)  # x,y pos, width,height
        self.window_layout = QVBoxLayout()
        self.create_grid_layout()
        self.create_horizontal_layout()

        self.window_layout.addWidget(self.grid_group_box)
        self.window_layout.addWidget(self.horizontal_group_box)
        self.setLayout(self.window_layout)
        self.show()

    def set_colours(self):
        if self.k == 4:
            self.colours = {0: "white", 1: "lightblue", 2: "#619bcc", 3: "#316a9a", 4: "#255075", 5: "#4169E1",
                            6: "#0F52BA", 7: "#0818A8"}
        elif self.k == 8:
            self.colours = {0: "white", 1: "lightblue", 2: "#89CFF0", 3: "#0096FF",
                            4: "#1F51FF", 5: "#4169E1", 6: "#0F52BA", 7: "#0818A8"}
        else:
            self.colours = {0: "white"}
            for c in range(1, self.k):
                self.colours[c] = "#" + ''.join([random.choice('0123456789ABCDEF') for _ in range(6)])

    def create_grid_layout(self):
        self.grid_group_box = QGroupBox("Grid")
        layout = QGridLayout()
        layout.setSpacing(0)
        self.set_colours()
        self.buttons = []
        ind = 0
        for i in range(self.M):
            for j in range(self.N):
                button = QPushButton()
                button.clicked.connect(partial(self.update_grid, i, j))
                button.setStyleSheet("background-color : white")
                self.buttons.append(button)
                layout.addWidget(button, i, j)
                ind += 1
        self.grid_group_box.setLayout(layout)

    def create_horizontal_layout(self):
        self.horizontal_group_box = QGroupBox("horizontal")
        layout = QHBoxLayout()

        self.number_grains_text = QLineEdit("Number of grains", self)
        layout.addWidget(self.number_grains_text)

        self.random_radio_button = QRadioButton("Random", self)
        layout.addWidget(self.random_radio_button)

        start_button = QPushButton("Start", self)
        start_button.clicked.connect(partial(self.start_click))
        layout.addWidget(start_button)

        reset_button = QPushButton("Clear", self)
        reset_button.clicked.connect(self.clear_grid)
        layout.addWidget(reset_button)

        self.horizontal_group_box.setLayout(layout)

    def update_grid(self, i, j):
        self.sandPile.add_grain(i + 1, j + 1)
        if self.sandPile.is_critical_site(i + 1, j + 1):
            self.execute_avalanche(i + 1, j + 1)
        else:  # no avalanche
            self.buttons[i * self.N + j].setStyleSheet(
                "background-color : " + self.colours[self.sandPile.grid[i + 1][j + 1]])  # + ";border :5px solid red;")
            # self.buttons[i * self.N + j].repaint()

    def execute_avalanche(self, i_c, j_c):
        """Initiates avalanche at (i_c, j_c).
        Loops over the toppling of piles until grid hits a 'steady' state"""
        toppling_sites = set()
        toppling_sites.add((i_c, j_c))
        while len(toppling_sites) != 0:
            new_critical_sites = self.sandPile.execute_timestep(toppling_sites)
            toppling_sites = new_critical_sites
        # TODO: Extract repainting logic to another method
        self.update_button_colours()

    def update_button_colours(self):
        for x in range(self.M):  # TODO: this is time expensive...
            for y in range(self.N):  # This is quite time expensive... hopefully can optimise
                # self.buttons[x*self.N+y].setText(f'{self.sandPile.grid[x+1][y+1]}')
                self.buttons[x * self.N + y].setStyleSheet(
                    "background-color : " + self.colours[
                        self.sandPile.grid[x + 1][y + 1]])  # TODO: what colour for supercritical (>4) cells?

    def start_click(self):
        total_grains = self.number_grains_text.text()
        random_pos = self.random_radio_button.isChecked()
        if total_grains == "Number of grains":
            total_grains = 100  # default
            print(f"Default number of grains: {total_grains}")
        else:
            total_grains = int(total_grains)

        if random_pos:
            pos_i = np.random.randint(self.M, size=total_grains)
            pos_j = np.random.randint(self.N, size=total_grains)
        elif np.sum(self.sandPile.grid) == 1:  # start on initial point
            print("Starting on initial seed")
            [i_index, j_index] = np.where(self.sandPile.grid == 1)
            pos_i = (i_index - 1) * np.ones(total_grains, dtype=int)
            pos_j = (j_index - 1) * np.ones(total_grains, dtype=int)
        else:  # np.sum(self.sandPile.grid) == 0:
            print("Simulating grains dropped in center")
            pos_i = self.M // 2 * np.ones(total_grains, dtype=int)
            pos_j = self.N // 2 * np.ones(total_grains, dtype=int)

        for grain in range(total_grains):
            self.update_grid(pos_i[grain], pos_j[grain])

    def clear_grid(self):
        plt.imshow(self.sandPile.grid[1:self.M + 1, 1:self.N + 1], cmap='Blues',
                   interpolation='nearest')  # ,shading='gouraud')
        plt.show()
        self.sandPile.grid = np.zeros([self.M + 2, self.N + 2], dtype=int)
        for i in range(self.M):
            for j in range(self.N):
                # self.buttons[i*self.N+j].setText(f'{self.sandPile.grid[i+1][j+1]}')
                self.buttons[i * self.N + j].setStyleSheet("background-color : white")


def main():
    app = QApplication(sys.argv)
    ex = Window()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
