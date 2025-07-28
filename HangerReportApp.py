import tkinter as tk
from tkinter import ttk, filedialog
import os
import pandas as pd
import ImageProcessTab
import JobPrepareTab
import ReportGen
import Project

class MainWindow():
    def __init__(self):
        root = tk.Tk()
        root.title("Hanger Report Generator")
        root.iconbitmap("Are you working.ico")
        self.root = root

        self.project = Project.Project("New Project")

        self.tabControl = ttk.Notebook(root)
        self.reportGen = ReportGen.ReportGenTab(self.tabControl, project=self.project)
        self.photoProcessTab = ImageProcessTab.ImageProcessTab(self.tabControl)
        self.newJobTab = JobPrepareTab.JobPrepareTab(self.tabControl)

        self.tabControl.add(self.reportGen, text = "Report Generation")
        self.tabControl.add(self.photoProcessTab, text = "Image Processing")
        self.tabControl.add(self.newJobTab, text = "Prepare for Job")        
        
        self.tabControl.pack(expand=1, fill = "both")

        self.StatusLabel = tk.Label(root, text = "N/A Hangers")
        self.StatusLabel.pack()

        root.mainloop()


def Main():
    myWindow = MainWindow()

if __name__ == '__main__':
    Main()