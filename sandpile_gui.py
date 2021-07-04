# Abelian sandpile model GUI
import numpy as np
# import scipy as sp
import random as random
import matplotlib.pyplot as plt
# from scipy.optimize import curve_fit
# from math import ceil, floor
from functools import partial
# import time
import sys
from PyQt5.QtWidgets import QApplication, QHBoxLayout, QVBoxLayout, QGroupBox, QGridLayout, \
    QPushButton, QRadioButton, QLineEdit, QDialog
# from PyQt5.QtWidgets import QLabel, QWidget
# from PyQt5.QtGui import *
# from PyQt5.QtCore import *
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

    def create_grid_layout(self):
        self.grid_group_box = QGroupBox("Grid")
        layout = QGridLayout()
        layout.setSpacing(0)
        self.buttons = []
        if self.k == 4:
            self.colours = {0: "white", 1: "lightblue", 2: "#619bcc", 3: "#316a9a"}  # ,4:"#255075"}
        elif self.k == 8:
            self.colours = {0: "white", 1: "lightblue", 2: "#89CFF0", 3: "#0096FF",
                            4: "#1F51FF", 5: "#4169E1", 6: "#0F52BA", 7: "#0818A8"}
        else:
            self.colours = {0: "white"}
            for c in range(1, self.k):
                self.colours[c] = "#"+''.join([random.choice('0123456789ABCDEF') for _ in range(6)])
        ind = 0
        for i in range(self.M):
            for j in range(self.N):
                self.buttons.append(QPushButton())  # f'{0}'))
                self.buttons[ind].clicked.connect(partial(self.add_grain, i, j))
                self.buttons[ind].setStyleSheet("background-color : white")
                layout.addWidget(self.buttons[ind], i, j)  # , 2, 1)
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
        start_button.clicked.connect(partial(self.start_click))  # ,total_grains=self.number_grains_text.text(),random_pos = self.random_radio_button.isChecked()))
        layout.addWidget(start_button)

        reset_button = QPushButton("Clear", self)
        reset_button.clicked.connect(self.clear_grid)
        layout.addWidget(reset_button)

        self.horizontal_group_box.setLayout(layout)

    def add_grain(self, i, j):
        self.sandPile.grid[i+1][j+1] += 1
        sandgrid = self.sandPile.grid[1:self.M+1, 1:self.N+1]  # grid without edges
        m, n = np.unravel_index(sandgrid.argmax(), sandgrid.shape)  # Find site with max grains:
        m = m+1
        n = n+1

        if self.sandPile.check_site(m, n):  # Avalanche
            _ = self.sandPile.execute_avalanche(m, n)  # Avalanche occurs at (m,n)
            for i in range(self.M):
                for j in range(self.N):
                    # self.buttons[i*self.N+j].setText(f'{self.sandPile.grid[i+1][j+1]}')
                    self.buttons[i*self.N+j].setStyleSheet("background-color : "+self.colours[self.sandPile.grid[i+1][j+1]])
        else:  # no avalanche
            self.buttons[i*self.N+j].setStyleSheet("background-color : "+self.colours[self.sandPile.grid[i+1][j+1]])

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
        elif np.sum(self.sandPile.grid) == 0:
            print("Simulating grains dropped in center")
            pos_i = self.M//2 * np.ones(total_grains, dtype=int)
            pos_j = self.N//2 * np.ones(total_grains, dtype=int)
        elif np.sum(self.sandPile.grid) == 1:  # start on initial point
            print("Starting on initial seed")
            [i_index, j_index] = np.where(self.sandPile.grid == 1)
            pos_i = (i_index-1) * np.ones(total_grains, dtype=int)
            pos_j = (j_index-1) * np.ones(total_grains, dtype=int)
        else:
            print("Choose only one starting cell")
            return
        for grain in range(total_grains):
            self.add_grain(pos_i[grain], pos_j[grain])

    def clear_grid(self):
        plt.imshow(self.sandPile.grid[1:self.M+1, 1:self.N+1], cmap='Blues', interpolation='nearest')  # ,shading='gouraud')
        plt.show()
        self.sandPile.grid = np.zeros([self.M+2, self.N+2], dtype=int)
        for i in range(self.M):
            for j in range(self.N):
                # self.buttons[i*self.N+j].setText(f'{self.sandPile.grid[i+1][j+1]}')
                self.buttons[i*self.N+j].setStyleSheet("background-color : white")


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = Window()
    sys.exit(app.exec_())
