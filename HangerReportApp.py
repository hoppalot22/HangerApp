import tkinter as tk
from tkinter import ttk, filedialog
import os
import pandas as pd
import ImageProcessTab
import JobPrepareTab
import ReportGen
import Project
import pickle

class MainWindow():
    def __init__(self, project = None):
        root = tk.Tk()
        root.title("Hanger Report Generator")
        root.iconbitmap("Are you working.ico")
        root.bind("<Button-3>", lambda e : self.PrintProject())
        self.root = root

        if project is not None:
            self.project = project
        else:
            self.project = Project.Project("New Project")

        #print(self.project)

        self.tabControl = ttk.Notebook(root)
        self.reportGen = ReportGen.ReportGenTab(self.tabControl, self)
        self.imageTab = ImageProcessTab.ImageProcessTab(self.tabControl, self)
        self.newJobTab = JobPrepareTab.JobPrepareTab(self.tabControl, self)

        self.tabControl.add(self.reportGen, text = "Report Generation")
        self.tabControl.add(self.imageTab, text = "Image Processing")
        self.tabControl.add(self.newJobTab, text = "Prepare for Job")        
        
        self.tabControl.pack(expand=1, fill = "both")

        self.StatusLabel = tk.Label(root, text = "N/A Hangers")
        self.StatusLabel.pack()

        root.mainloop()

    def PrintProject(self):
        print(self.project)


def Main():
    wd = os.path.dirname(__file__)
    with open(f"{wd}\\HRSG Hangers.pkl", 'rb') as f:
        project = pickle.load(f)
    assert type(project) == Project.Project
    myWindow = MainWindow(project=project)

if __name__ == '__main__':
    Main()