from Memory_Allocation import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
import sys

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        # Window setup
        self.setWindowTitle("Memory Allocation Simulator")
        self.setWindowIcon(QIcon('logo.png'))

        # Main layout
        main_widget = QWidget()
        main_layout = QHBoxLayout()

        # Job Panel
        left_panel = self.create_left_panel()

        # Combine layouts
        main_layout.addWidget(left_panel)

        # Set layout to main widget
        main_widget.setLayout(main_layout)
        self.setCentralWidget(main_widget)

        self.showMaximized()

    def create_left_panel(self):
        # Create the container widget
        left_panel_widget = QWidget()
        left_panel = QVBoxLayout()
        left_panel_widget.setLayout(left_panel)
        left_panel_widget.setFixedSize(400, 900)

        # Header
        label = QLabel("Job List/Queue")
        label.setFont(QFont('Consolas', 20))
        label.setStyleSheet("QLabel {font-weight: bold;}")
        left_panel.addWidget(label)

        # Scroll Area for Jobs
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_layout = QVBoxLayout()
        self.scroll_area.setLayout(self.scroll_layout)

        left_panel.addWidget(self.scroll_area)

        return left_panel_widget
    
    def create_middle_panel(self):
        #Container Widget
        middle_panel_widget = QWidget()
        middle_panel = QVBoxLayout()
        middle_panel_widget.setLayout(middle_panel)
        middle_panel_widget.setFixedSize(400, 900)
        
        #Headers
        
        self.best_fit_output = QTextEdit()
        self.best_fit_output.setReadOnly(True)
        middle_panel.addWidget(self.best_fit_output)
        
        
        
        self.best_fit_output = QTextEdit()
        self.best_fit_output.setReadOnly(True)
        middle_panel.addWidget(self.first_fit_output)
        
        return middle_panel_widget

    def populate_job_list(self, jobs, memory):
        # Clear previous jobs
        for i in reversed(range(self.scroll_layout.count())): 
            self.scroll_layout.itemAt(i).widget().deleteLater()

        # Create job boxes
        for i, job in enumerate(jobs[:5], 1):
            job = min(job, 80)  

            job_widget = QWidget()
            job_layout = QVBoxLayout()

            job_widget.setStyleSheet("QWidget {background-color: #8f9bf2; border-radius: 10px}")
            job_widget.setMinimumHeight(job*2)

            label = QLabel(f"Job {i}: {job} KB")
            label.setFont(QFont('Consolas', 14))
            label.setAlignment(Qt.AlignCenter)
            job_layout.addWidget(label)

            job_widget.setLayout(job_layout)
            self.scroll_layout.addWidget(job_widget)

        self.scroll_layout.addStretch()
        
        self.update_allocations(jobs, memory)
        
    def update_allocations(self, jobs, memory):
        best_fit_alloc = best_fit(jobs, memory)
        first_fit_alloc = first_fit(jobs, memory)
        
        best_fit_text = "\n".join([f"Job {i+1}:  {alloc}" for i, alloc in enumerate(best_fit_alloc)])
        first_fit_text = "\n".join([f"Job {i+1}:  {alloc}" for i, alloc in enumerate(first_fit_alloc)])

        self.best_fit_output.setText(best_fit_text)
        self.first_fit_output.setText(first_fit_text)

def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    
    mem = randomMemoryStatus()
    free = mem.freeSpaces()
    requests = requestsMemories(free)
    window.populate_job_list(requests, free)

    window.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
