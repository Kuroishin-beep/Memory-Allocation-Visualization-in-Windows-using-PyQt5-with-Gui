from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QPushButton, QVBoxLayout, QHBoxLayout, QListWidget, QComboBox, QSpinBox, QMessageBox, QGraphicsView, QGraphicsScene, QGraphicsRectItem, QTextEdit
from PyQt5.QtGui import QBrush, QColor, QFont
from PyQt5.QtCore import QTimer
import sys
import random

class MemoryAllocationApp(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle("Memory Allocation Simulator")
        self.setGeometry(100, 100, 1000, 500)
        
        # Job List
        self.jobList = QListWidget()
        self.addJobBtn = QPushButton("Add Job")
        self.removeJobBtn = QPushButton("Remove Job")
        self.jobSizeInput = QSpinBox()
        self.jobSizeInput.setRange(1, 100)
        
        # Block List
        self.blockList = QListWidget()
        self.addBlockBtn = QPushButton("Add Block")
        self.removeBlockBtn = QPushButton("Remove Block")
        self.blockSizeInput = QSpinBox()
        self.blockSizeInput.setRange(1, 100)
        
        # Allocation Algorithm Selection
        self.algorithmSelector = QComboBox()
        self.algorithmSelector.addItems(["First-Fit", "Best-Fit"])
        self.runBtn = QPushButton("Run Allocation")
        self.randomBtn = QPushButton("Randomize")
        self.clearBtn = QPushButton("Clear All")
        self.nextStepBtn = QPushButton("Next Step")
        self.autoPlayBtn = QPushButton("Auto-Play")
        
        # Memory Visualization
        self.graphicsView = QGraphicsView()
        self.scene = QGraphicsScene()
        self.graphicsView.setScene(self.scene)
        self.graphicsView.setMinimumHeight(300)
        
        # Step-by-step process log
        self.processLog = QListWidget()
        
          # Layouts
        mainLayout = QVBoxLayout()
        topLayout = QHBoxLayout()
        leftLayout = QVBoxLayout()
        middleLayout = QVBoxLayout()
        rightLayout = QVBoxLayout()
        logLayout = QVBoxLayout()
        
        leftLayout.addWidget(QLabel("Job List (Process Queue)"))
        leftLayout.addWidget(self.jobList)
        leftLayout.addWidget(self.jobSizeInput)
        leftLayout.addWidget(self.addJobBtn)
        leftLayout.addWidget(self.removeJobBtn)
        
        middleLayout.addWidget(QLabel("Memory Blocks"))
        middleLayout.addWidget(self.blockList)
        middleLayout.addWidget(self.blockSizeInput)
        middleLayout.addWidget(self.addBlockBtn)
        middleLayout.addWidget(self.removeBlockBtn)
        middleLayout.addWidget(QLabel("Allocation Algorithm"))
        middleLayout.addWidget(self.algorithmSelector)
        middleLayout.addWidget(self.runBtn)
        middleLayout.addWidget(self.randomBtn)
        middleLayout.addWidget(self.clearBtn)
        middleLayout.addWidget(self.nextStepBtn)
        middleLayout.addWidget(self.autoPlayBtn)
        
        rightLayout.addWidget(QLabel("Step-by-Step Process"))
        rightLayout.addWidget(self.processLog)
        
        topLayout.addLayout(leftLayout)
        topLayout.addLayout(middleLayout)
        topLayout.addLayout(rightLayout)
        
        visualizeLayout = QVBoxLayout()
        visualizeLayout.addWidget(QLabel("Visualize Allocation"))
        visualizeLayout.addWidget(self.graphicsView)
        
        mainLayout.addLayout(topLayout)
        mainLayout.addLayout(visualizeLayout)
        self.setLayout(mainLayout)
        
        # Event Listeners
        self.addJobBtn.clicked.connect(self.addJob)
        self.removeJobBtn.clicked.connect(self.removeJob)
        self.addBlockBtn.clicked.connect(self.addBlock)
        self.removeBlockBtn.clicked.connect(self.removeBlock)
        self.runBtn.clicked.connect(self.runAllocation)
        self.randomBtn.clicked.connect(self.randomize)
        self.clearBtn.clicked.connect(self.clearAll)
        self.nextStepBtn.clicked.connect(self.nextStep)
        self.autoPlayBtn.clicked.connect(self.autoPlay)
        
        # Step Tracking
        self.allocation_steps = []
        self.current_step = 0
    
    def addJob(self):
        size = self.jobSizeInput.value()
        self.jobList.addItem(f"Job - {size}K")
    
    def removeJob(self):
        selected = self.jobList.currentRow()
        if selected >= 0:
            self.jobList.takeItem(selected)
    
    def addBlock(self):
        size = self.blockSizeInput.value()
        self.blockList.addItem(f"Block - {size}K")
    
    def removeBlock(self):
        selected = self.blockList.currentRow()
        if selected >= 0:
            self.blockList.takeItem(selected)
    
    def runAllocation(self):
        self.processLog.clear()
        self.allocation_steps.clear()
        self.current_step = 0
        
        algorithm = self.algorithmSelector.currentText()
        jobs = [int(self.jobList.item(i).text().split('-')[1][:-1]) for i in range(self.jobList.count())]
        blocks = [int(self.blockList.item(i).text().split('-')[1][:-1]) for i in range(self.blockList.count())]
        
        if not jobs or not blocks:
            QMessageBox.warning(self, "Warning", "Please add jobs and memory blocks before running allocation.")
            return
        
        allocation = self.allocateMemory(jobs, blocks, algorithm)
        self.visualizeAllocation(allocation, blocks, jobs)
    
    def allocateMemory(self, jobs, blocks, algorithm):
        allocation = [-1] * len(jobs)
        remaining_blocks = blocks[:]
        
        for i, job in enumerate(jobs):
            best_idx = -1
            if algorithm == "First-Fit":
                for j, block in enumerate(remaining_blocks):
                    if job <= block:
                        best_idx = j
                        break
            elif algorithm == "Best-Fit":
                best_idx = min((j for j, b in enumerate(remaining_blocks) if job <= b), key=lambda x: remaining_blocks[x], default=-1)
            if best_idx != -1:
                allocation[i] = best_idx
                remaining_blocks[best_idx] -= job
                self.allocation_steps.append(f"Job {job}K assigned to Block {best_idx+1} ({blocks[best_idx]}K)")
            else:
                self.allocation_steps.append(f"Job {job}K could not be allocated.")
        
        return allocation
    
    def visualizeAllocation(self, allocation, blocks, jobs):
        self.scene.clear()
        y_position = 0
        block_height = 40
        
        for i, block in enumerate(blocks):
            used_space = sum(job for job, alloc in zip(jobs, allocation) if alloc == i)
            free_space = block - used_space
            
            rect = QGraphicsRectItem(0, y_position, 300, block_height)
            rect.setBrush(QBrush(QColor("gray")))
            self.scene.addItem(rect)
            
            if used_space > 0:
                used_rect = QGraphicsRectItem(0, y_position, (used_space / block) * 300, block_height)
                used_rect.setBrush(QBrush(QColor("blue")))
                self.scene.addItem(used_rect)
                
            label = self.scene.addText(f"Block {i+1}: {block}K (Used: {used_space}K, Free: {free_space}K)")
            label.setFont(QFont("Arial", 10))
            label.setPos(310, y_position)
            
            y_position += block_height + 10
    
    def nextStep(self):
        if self.current_step < len(self.allocation_steps):
            self.processLog.addItem(self.allocation_steps[self.current_step])
            self.current_step += 1
    
    def autoPlay(self):
        self.processLog.clear()  # Clear previous logs
        self.current_step = 0  # Reset step counter
        
        if not self.allocation_steps:
            QMessageBox.warning(self, "Warning", "No allocation steps available. Run allocation first.")
            return

        def play_step():
            if self.current_step < len(self.allocation_steps):
                self.processLog.addItem(self.allocation_steps[self.current_step])
                self.current_step += 1
                QTimer.singleShot(1000, play_step)  # Delay of 1 second (1000 ms)

        play_step()
    
    def clearAll(self):
        self.jobList.clear()
        self.blockList.clear()
        self.processLog.clear()
        self.scene.clear()
    
    def randomize(self):
        self.jobList.clear()
        self.blockList.clear()
        for _ in range(random.randint(3, 6)):
            self.jobList.addItem(f"Job - {random.randint(5, 50)}K")
        for _ in range(random.randint(3, 6)):
            self.blockList.addItem(f"Block - {random.randint(5, 100)}K")

    
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MemoryAllocationApp()
    window.show()
    sys.exit(app.exec_())