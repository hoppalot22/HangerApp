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

        self.tabControl = ttk.Notebook(root)       
        self.tabs = {}
        self.tabs["reportGen"] = ReportGen.ReportGenTab(self.tabControl, self)
        self.tabs["imageProcess"] = ImageProcessTab.ImageProcessTab(self.tabControl, self)
        self.tabs["jobPrepare"] = JobPrepareTab.JobPrepareTab(self.tabControl, self)   

        self.tabControl.add(self.tabs["reportGen"], text = "Report Generation")
        self.tabControl.add(self.tabs["imageProcess"], text = "Image Processing")
        self.tabControl.add(self.tabs["jobPrepare"], text = "Prepare for Job")        
        
        self.tabControl.pack(expand=1, fill = "both")

        self.StatusLabel = tk.Label(root, text = "N/A Hangers")
        self.StatusLabel.pack()

        root.mainloop()

    def NewProject(self):
        project = Project.Project("New Project")
        self.project = project

        for tab in self.tabs.values():
            tab.Update()

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