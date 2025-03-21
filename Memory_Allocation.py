
import numpy as np
import matplotlib
matplotlib.use('Qt5Agg')  # Set backend before importing pyplot
import matplotlib.pyplot as plt

from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *

import sys
import random


## Memory Block Information.
class MemoryBlock:
    colors = [np.array([0.5, 0.9, 0.7]),
              np.array([1.0, 0.9, 0.5]),
              np.array([0.4, 0.4, 0.9])]

    def __init__(self, range, type="used"):
        self.range = range
        self.type = type

    def space(self):
        return self.range[1] - self.range[0]

    def typeID(self):
        if self.type == "used":
            return 0
        if self.type == "free":
            return 1
        if self.type == "fit":
            return 2
        return 0

    def paint(self, painter, x, y0, w, h_scale):
        y = y0 + h_scale * self.range[0]
        h = self.space() * h_scale

        gradient = QLinearGradient(x, y, x, y + h)

        color = self.colors[self.typeID()]
        dark_color = 0.85 * color

        gradient.setColorAt(0.0, QColor(int(255 * color[0]), int(255 * color[1]), int(255 * color[2])))
        gradient.setColorAt(0.7, QColor(int(255 * dark_color[0]), int(255 * dark_color[1]), int(255 * dark_color[2])))

        painter.setBrush(gradient)

        # Convert to int before calling drawRect
        painter.drawRect(int(x), int(y), int(w), int(h))

        if self.typeID() == 2:
            painter.drawText(int(x + 0.5 * w - 5), int(y + 0.5 * h + 5), "%s MB" % self.space())



## Memory information.
class Memory:
    def __init__(self, memory_size, used_blocks, free_blocks):
        self.memory_size = memory_size
        self.used_blocks = used_blocks
        self.free_blocks = free_blocks
        self.fit_blocks = []
        self.success = 0.0

    def copy(self):
        return Memory(self.memory_size, self.used_blocks.copy(), self.free_blocks.copy())

    def freeSpaces(self):
        return [free_block.space() for free_block in self.free_blocks]

    def fit(self, memory_requests, fit_func):
        success, fit_blocks = fit_func(self.freeSpaces(), memory_requests)
        self.setFitBlocks(fit_blocks)
        self.success = success

    def setFitBlocks(self, fit_blocks):
        for i, fit_blocks_i in enumerate(fit_blocks):
            if i >= len(self.free_blocks):
                continue  # Prevent index error
            fit_address = self.free_blocks[i].range[0]
            for fit_block in fit_blocks_i:
                block = MemoryBlock((fit_address, fit_address + fit_block), "fit")
                self.fit_blocks.append(block)
                fit_address += fit_block

    def paint(self, painter, x, y, w, h):
        h_scale = h / float(self.memory_size)
        for block in self.used_blocks + self.free_blocks + self.fit_blocks:
            block.paint(painter, x, y, w, h_scale)


## Memory requests.
class MemoryRequests:
    def __init__(self, memory_size, memory_requests):
        self.memory_size = memory_size
        self.memory_requests = memory_requests

    def paint(self, painter, x, y, w, h):
        h_scale = h / float(self.memory_size)
        y_pos = 30
        for request in self.memory_requests:
            block = MemoryBlock((y_pos, y_pos + request), "fit")
            block.paint(painter, x, y, w, h_scale)
            y_pos += request + 20


## Int attribute.
class IntAttribute:
    def __init__(self, name="", val=0, val_min=0, val_max=100):
        self._name = name
        self._val = val
        self._val_min = val_min
        self._val_max = val_max

    def name(self):
        return self._name

    def setValue(self, val):
        self._val = val

    def value(self):
        return self._val

    def validator(self, parent=None):
        return QIntValidator(self._val_min, self._val_max, parent)


## Simulation setting.
class SimulationSetting:
    def __init__(self):
        self.memory_size = IntAttribute("Memory Size", 1000, 500, 2000)
        self.block_min = IntAttribute("Memory Block Min", 50, 10, 100)
        self.block_max = IntAttribute("Memory Block Max", 200, 100, 500)
        self.num_trials = IntAttribute("Num Trials", 50, 5, 10000)


def randomMemoryStatus(memory_size=1000, block_min=10, block_max=100):
    memory_lists = [0]
    total = 0

    while total < memory_size:
        remaining = memory_size - total
        if remaining < block_min:
            break
        block = random.randint(block_min, min(block_max, remaining))
        total += block
        memory_lists.append(total)

    if memory_lists[-1] != memory_size:
        memory_lists.append(memory_size)

    used_blocks = []
    free_blocks = []
    for i in range(len(memory_lists) - 1):
        start = memory_lists[i]
        end = memory_lists[i+1]
        if start >= end:
            continue
        if i % 2 == 0:
            used_blocks.append(MemoryBlock((start, end), "used"))
        else:
            free_blocks.append(MemoryBlock((start, end), "free"))

    return Memory(memory_size, used_blocks, free_blocks)


def requestsMemories(free_spaces):
    total_free = sum(free_spaces)
    if total_free == 0:
        return []
    memory_size = 0.8 * total_free
    block_min = max(1, min(free_spaces) // 3) if free_spaces else 1
    block_max = max(free_spaces) if free_spaces else 1

    memory_requests = []
    total = 0
    while total < memory_size:
        req = random.randint(block_min, block_max)
        memory_requests.append(req)
        total += req
    return memory_requests


def commonFit(free_spaces, memory_requests, fit_func):
    fit_spaces = [0] * len(free_spaces)
    fit_blocks = [[] for _ in range(len(free_spaces))]
    num_fitted = 0

    for req in memory_requests:
        fitted = fit_func(free_spaces, req, fit_spaces, fit_blocks)
        num_fitted += fitted

    success = num_fitted / len(memory_requests) if memory_requests else 0.0
    return success, fit_blocks


def firstFit(free_spaces, memory_requests):
    def fit_func(free_spaces, req, fit_spaces, fit_blocks):
        for i in range(len(free_spaces)):
            if (fit_spaces[i] + req) <= free_spaces[i]:
                fit_blocks[i].append(req)
                fit_spaces[i] += req
                return 1
        return 0
    return commonFit(free_spaces, memory_requests, fit_func)


def bestFit(free_spaces, memory_requests):
    def fit_func(free_spaces, req, fit_spaces, fit_blocks):
        best_idx = -1
        min_remaining = float('inf')
        for i in range(len(free_spaces)):
            remaining = free_spaces[i] - (fit_spaces[i] + req)
            if remaining >= 0 and remaining < min_remaining:
                min_remaining = remaining
                best_idx = i
        if best_idx != -1:
            fit_blocks[best_idx].append(req)
            fit_spaces[best_idx] += req
            return 1
        return 0
    return commonFit(free_spaces, memory_requests, fit_func)


def worstFit(free_spaces, memory_requests):
    def fit_func(free_spaces, req, fit_spaces, fit_blocks):
        worst_idx = -1
        max_remaining = -1
        for i in range(len(free_spaces)):
            remaining = free_spaces[i] - (fit_spaces[i] + req)
            if remaining >= 0 and remaining > max_remaining:
                max_remaining = remaining
                worst_idx = i
        if worst_idx != -1:
            fit_blocks[worst_idx].append(req)
            fit_spaces[worst_idx] += req
            return 1
        return 0
    return commonFit(free_spaces, memory_requests, fit_func)


def runSimulationTrials(num_trials=50, memory_size=1000, block_min=10, block_max=100):
    plt.figure()
    plt.title("Memory Allocation Simulation: %s Trials" % num_trials)
    strategies = [('First-Fit', firstFit), ('Best-Fit', bestFit), ('Worst-Fit', worstFit)]
    data = {name: [] for name, _ in strategies}

    for _ in range(num_trials):
        mem = randomMemoryStatus(memory_size, block_min, block_max)
        free = mem.freeSpaces()
        requests = requestsMemories(free)
        for name, func in strategies:
            success, _ = func(free, requests)
            data[name].append(success)

    xs = range(num_trials)
    for name, _ in strategies:
        avg = np.mean(data[name]) * 100
        plt.plot(xs, data[name], label=f"{name} (Avg: {avg:.1f}%)")

    plt.ylabel("Success Rate")
    plt.xlabel("Trial")
    plt.legend()
    plt.show()


class SimulationSettingUI(QWidget):
    def __init__(self, setting):
        super().__init__()
        self._setting = setting
        self.initUI()

    def initUI(self):
        layout = QGridLayout()
        attrs = [
            self._setting.memory_size,
            self._setting.block_min,
            self._setting.block_max,
            self._setting.num_trials
        ]
        for i, attr in enumerate(attrs):
            lbl = QLabel(attr.name())
            edit = QLineEdit(str(attr.value()))
            edit.setValidator(attr.validator(self))
            edit.editingFinished.connect(lambda e=edit, a=attr: a.setValue(int(e.text())))
            layout.addWidget(lbl, i, 0)
            layout.addWidget(edit, i, 1)
        self.setLayout(layout)


class SimulatorView(QWidget):
    def __init__(self, setting):
        super().__init__()
        self._setting = setting
        self._simulate()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.fillRect(self.rect(), Qt.white)
        w = self.width() // 5
        h = self.height() - 40
        self._requests.paint(painter, 20, 30, w, h)
        x = 40 + w
        for mem, title in zip(self._memories, ['First-Fit', 'Best-Fit', 'Worst-Fit']):
            painter.drawText(x, 20, f"{title}: {mem.success*100:.1f}%")
            mem.paint(painter, x, 30, w, h)
            x += w + 20

    def mousePressEvent(self, event):
        self._simulate()
        self.update()

    def _simulate(self):
        mem_size = self._setting.memory_size.value()
        mem = randomMemoryStatus(mem_size, self._setting.block_min.value(), self._setting.block_max.value())
        self._memories = [mem.copy() for _ in range(3)]
        free = mem.freeSpaces()
        requests = requestsMemories(free)
        self._requests = MemoryRequests(mem_size, requests)
        for mem, func in zip(self._memories, [firstFit, bestFit, worstFit]):
            mem.fit(requests, func)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Memory Allocation Simulator")
        self._setting = SimulationSetting()
        self.view = SimulatorView(self._setting)
        self.setCentralWidget(self.view)
        self._settings_ui = SimulationSettingUI(self._setting)
        self._initMenu()

    def _initMenu(self):
        menu = self.menuBar().addMenu("Simulation")
        menu.addAction("Settings", self._settings_ui.show)
        menu.addAction("Run Trials", self._runTrials)

    def _runTrials(self):
        runSimulationTrials(
            self._setting.num_trials.value(),
            self._setting.memory_size.value(),
            self._setting.block_min.value(),
            self._setting.block_max.value()
        )


def main():
    app = QApplication(sys.argv)
    win = MainWindow()
    win.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()