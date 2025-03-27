from Memory_Allocation import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
import sys

def simulate_best_fit(jobs, initial_blocks):
    free_blocks = initial_blocks.copy()
    allocated = []
    for job in jobs:
        suitable = [b for b in free_blocks if b >= job]
        if not suitable:
            continue
        selected = min(suitable)
        free_blocks.remove(selected)
        frag = selected - job
        allocated.append({'size': selected, 'job': job, 'frag': frag})
    # Combine allocated and remaining free blocks (in their order)
    blocks = []
    # Add allocated blocks first, then remaining free blocks
    blocks.extend(allocated)
    blocks.extend([{'size': b, 'free': True} for b in free_blocks])
    return blocks

def simulate_first_fit(jobs, initial_blocks):
    free_blocks = initial_blocks.copy()
    allocated = []
    for job in jobs:
        for i in range(len(free_blocks)):
            if free_blocks[i] >= job:
                selected = free_blocks.pop(i)
                frag = selected - job
                allocated.append({'size': selected, 'job': job, 'frag': frag})
                break
    # Combine allocated and remaining free blocks (in their order)
    blocks = []
    blocks.extend(allocated)
    blocks.extend([{'size': b, 'free': True} for b in free_blocks])
    return blocks

class MainWindow(QMainWindow):
    def __init__(self, best_fit_blocks, first_fit_blocks, jobs):
        super().__init__()
        self.setWindowTitle("Memory Allocation Simulator")
        self.setWindowIcon(QIcon('logo.png'))
        
        # Store the jobs and blocks data
        self.jobs = jobs
        self.best_fit_blocks = best_fit_blocks
        self.first_fit_blocks = first_fit_blocks
        
        # Create main widget and layout
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        main_layout = QHBoxLayout(main_widget)
        
        # Create panels
        self.left_panel = self.create_left_panel()
        self.best_fit_panel = self.create_middle_panel("Best Fit", self.best_fit_blocks)
        self.first_fit_panel = self.create_middle_panel("First Fit", self.first_fit_blocks)
        
        # Add panels to layout
        main_layout.addWidget(self.left_panel)
        main_layout.addWidget(self.best_fit_panel)
        main_layout.addWidget(self.first_fit_panel)
        
        self.showMaximized()

    def create_left_panel(self):
        container = QWidget()
        container.setFixedSize(400, 900)
        layout = QVBoxLayout(container)
        
        # Header
        label = QLabel("Job List/Queue")
        label.setFont(QFont('Consolas', 20))
        label.setStyleSheet("font-weight: bold;")
        layout.addWidget(label)
        
        # Scroll Area
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        content = QWidget()
        self.job_layout = QVBoxLayout(content)
        
        # Create job items with original styling
        for i, job in enumerate(self.jobs[:5], 1):
            job_widget = QWidget()
            job_widget.setStyleSheet("background-color: #8f9bf2; border-radius: 10px;")
            job_widget.setMinimumHeight(min(job, 80) * 2)
            
            item_layout = QVBoxLayout(job_widget)
            label = QLabel(f"Job {i}: {job} KB")
            label.setFont(QFont('Consolas', 14))
            label.setAlignment(Qt.AlignCenter)
            item_layout.addWidget(label)
            
            self.job_layout.addWidget(job_widget)
        
        self.job_layout.addStretch()
        scroll.setWidget(content)
        layout.addWidget(scroll)
        
        return container

    def create_middle_panel(self, title, blocks):
        container = QWidget()
        container.setFixedSize(400, 900)
        layout = QVBoxLayout(container)
        
        # Header
        label = QLabel(title)
        label.setFont(QFont('Consolas', 20))
        label.setStyleSheet("font-weight: bold;")
        layout.addWidget(label)
        
        # Scroll Area
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        content = QWidget()
        block_layout = QVBoxLayout(content)
        
        # Create block items matching left panel style
        for block in blocks:
            widget = QWidget()
            size = block['size']
            
            # Color coding
            if 'job' in block:
                color = '#99ff99' if block['frag'] == 0 else '#ff9999'
                text = f"Job: {block['job']}KB\nBlock: {size}KB"
                if block['frag'] > 0:
                    text += f"\nFrag: {block['frag']}KB"
            else:
                color = '#9999ff'
                text = f"Free: {size}KB"
            
            widget.setStyleSheet(f"""
                background-color: {color}; 
                border-radius: 10px;
                min-height: {min(size, 80)*2}px;
            """)
            
            item_layout = QVBoxLayout(widget)
            label = QLabel(text)
            label.setFont(QFont('Consolas', 12))
            label.setAlignment(Qt.AlignCenter)
            item_layout.addWidget(label)
            
            block_layout.addWidget(widget)
        
        block_layout.addStretch()
        scroll.setWidget(content)
        layout.addWidget(scroll)
        
        return container

def main():
    app = QApplication(sys.argv)
    
    mem = randomMemoryStatus()
    free = mem.freeSpaces()
    requests = requestsMemories(free)
    
    # Use first 5 jobs to match left panel display
    visible_jobs = requests[:5]
    best_fit_blocks = simulate_best_fit(visible_jobs, free)
    first_fit_blocks = simulate_first_fit(visible_jobs, free)
    
    window = MainWindow(best_fit_blocks, first_fit_blocks, requests)
    window.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()