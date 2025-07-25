import tkinter as tk
from tkinter import ttk

import pandas as pd
import ImageProcessTab
import JobPrepareTab
import ReportGen

class MainWindow():
    def __init__(self):
        root = tk.Tk()
        root.title("Hanger Report Generator")
        root.iconbitmap("Are you working.ico")
        self.root = root

        self.project = Project("New Project")
        self.data = None
        self.photoFolder = None

        self.tabControl = ttk.Notebook(root)
        self.reportGen = ReportGen.ReportGenTab(self.tabControl)
        self.photoProcessTab = ImageProcessTab.ImageProcessTab(self.tabControl)
        self.newJobTab = JobPrepareTab.JobPrepareTab(self.tabControl)

        self.tabControl.add(self.reportGen, text = "Report Generation")
        self.tabControl.add(self.photoProcessTab, text = "Image Processing")
        self.tabControl.add(self.newJobTab, text = "Prepare for Job")        
        
        self.tabControl.pack(expand=1, fill = "both")

        self.StatusLabel = tk.Label(root, text = "N/A Hangers")
        self.StatusLabel.pack()

        root.mainloop()

class Project():
    def __init__(self, name):
        self.name = name
        self.savePath = None
        self.projTree = None
        self.fields = None
        self.data = None
        self.QAcodes = None
        self.componentIDs = []
        self.nextID = 0

    def AddComponent(self):
        self.componentIDs.append(self.nextID)
        self.nextID += 1




def Main():
    myWindow = MainWindow()

if __name__ == '__main__':
    Main()