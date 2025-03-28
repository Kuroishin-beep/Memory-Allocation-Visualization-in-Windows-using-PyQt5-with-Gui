from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QPushButton, QVBoxLayout, QHBoxLayout, QListWidget, QComboBox, QSpinBox, QMessageBox, QGraphicsView, QGraphicsScene, QGraphicsRectItem, QTextEdit
from PyQt5.QtGui import QBrush, QColor, QFont, QPen
from PyQt5.QtCore import QTimer
import sys
import random

class MemoryAllocationApp(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle("Memory Allocation Simulator")
        self.setGeometry(100, 200, 1100, 500) #Bigger size
        
        # Job List
        self.jobList = QListWidget()
        self.addJobBtn = QPushButton("Add Job")
        self.removeJobBtn = QPushButton("Remove Job")
        self.jobSizeInput = QSpinBox()
        self.jobSizeInput.setRange(1, 200)
        
        # Block List
        self.blockList = QListWidget()
        self.addBlockBtn = QPushButton("Add Block")
        self.removeBlockBtn = QPushButton("Remove Block")
        self.blockSizeInput = QSpinBox()
        self.blockSizeInput.setRange(1, 200)
        
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
        self.graphicsView.setMinimumWidth(500)  #made the visualization allocation initial size big
        self.graphicsView.setMinimumHeight(400) 
        
        # Step-by-step process log
        self.processLog = QListWidget()
        
        # Layouts
        mainLayout = QVBoxLayout()
        topLayout = QHBoxLayout()
        leftLayout = QVBoxLayout()
        middleLayout = QVBoxLayout()
        rightLayout = QVBoxLayout()
        rightmostLayout = QVBoxLayout()  # New layout for visualization

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
        self.processLog.setMinimumWidth(250) #set a min size for the step by step
        rightLayout.addWidget(self.processLog)

        rightmostLayout.addWidget(QLabel("Visualize Allocation"))  # Move visualization here
        rightmostLayout.addWidget(self.graphicsView)

        # Adjust top layout to include visualization at the rightmost position
        topLayout.addLayout(leftLayout)
        topLayout.addLayout(middleLayout)
        topLayout.addLayout(rightLayout)
        topLayout.addLayout(rightmostLayout)  # Added visualization layout to the rightmost position

        mainLayout.addLayout(topLayout)
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
        allocation = [-1] * len(jobs)  # Initialize allocation list (-1 means unallocated)
        allocated_blocks = [False] * len(blocks)  # Track whether a block is already assigned

        for i, job in enumerate(jobs):
            best_idx = -1
# Made it so that it doesn't put other jobs in the occupied blocks
            if algorithm == "First-Fit":
                for j, block in enumerate(blocks):
                    if job <= block and not allocated_blocks[j]:  # Check if block is free
                        best_idx = j
                        break

            elif algorithm == "Best-Fit":
                min_block_size = float('inf')
                for j, block in enumerate(blocks):
                    if job <= block and not allocated_blocks[j] and block < min_block_size:
                        best_idx = j
                        min_block_size = block

            if best_idx != -1:
                allocation[i] = best_idx
                allocated_blocks[best_idx] = True  # Mark block as occupied
                self.allocation_steps.append(
                    f"Job {job}K assigned to Block {best_idx+1} ({blocks[best_idx]}K)"
                )
            else:
                self.allocation_steps.append(f"Job {job}K could not be allocated.")

        return allocation


    


    def visualizeAllocation(self, allocation, blocks, jobs):
        self.scene.clear()
        total_height = 400  # Fixed total height for all blocks combined
        block_width = 300   # Width of the column
        total_memory = sum(blocks)  # Total memory across all blocks
        y_position = 0  # Start from the top

        # Generate random colors for jobs
        job_colors = [QColor(random.randint(50, 255), random.randint(50, 255), random.randint(50, 255)) for _ in jobs]

        for i, block in enumerate(blocks):
            block_height = (block / total_memory) * total_height  # Scale block size proportionally
            rect = QGraphicsRectItem(0, y_position, block_width, block_height)
            rect.setBrush(QBrush(QColor("gray")))

            # Make the block boundary lines bolder
            rect.setPen(QPen(QColor("black"), 3))  # Thicker boundary lines
            self.scene.addItem(rect)

            used_space = sum(job for job, alloc in zip(jobs, allocation) if alloc == i)
            free_space = block - used_space

            current_y = y_position  # Start filling used memory from the top of this block

            for job, alloc in zip(jobs, allocation):
                if alloc == i:
                    job_height = (job / block) * block_height  # Scale job size within this block
                    used_rect = QGraphicsRectItem(0, current_y, block_width, job_height)
                    used_rect.setBrush(QBrush(job_colors[jobs.index(job)]))  # Assign unique color
                    used_rect.setPen(QPen(QColor("black"), 2))  # Thin border for each job
                    self.scene.addItem(used_rect)
                    current_y += job_height  # Move downward for the next job

            label = self.scene.addText(f"Block {i+1}: {block}K (Used: {used_space}K, Free: {free_space}K)")
            label.setFont(QFont("Arial", 10))
            label.setPos(block_width + 10, y_position)  # Position the label beside the block

            y_position += block_height  # Move down for the next block

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