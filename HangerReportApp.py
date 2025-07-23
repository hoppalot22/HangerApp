import tkinter as tk
from tkinter import ttk
from tkinter import filedialog, messagebox
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
        #root.geometry('700x400')

        self.project = Project("New Project")
        self.excelWizard = None

        self.tabControl = ttk.Notebook(root)
        self.reportGen = ReportGen.ReportGenTab(self.tabControl)
        self.photoProcessTab = ImageProcessTab.ImageProcessTab(self.tabControl)
        self.newJobTab = JobPrepareTab.JobPrepareTab(self.tabControl)

        #root.bind("<Configure>", photoProcessTab.gui.OnResize)
        self.optionWindow = None

        self.tabControl.add(self.reportGen, text = "Report Generation")
        self.tabControl.add(self.photoProcessTab, text = "Image Processing")
        self.tabControl.add(self.newJobTab, text = "Prepare for Job")        
        
        self.tabControl.pack(expand=1, fill = "both")

        self.reportGen.buttonColumn.AddButton("GenProj", text = "Generate From...", command = self.GenerateProj)

        numHangersLabel = tk.Label(root, text = "N/A Hangers")
        numHangersLabel.pack()

        root.mainloop()

        self.hangerData = None
        self.photoFolder = None

    def GenerateProj(self):
        projTree = self.reportGen.treeView.tree

        if not (len(projTree.get_children()) == 0):
            if not (messagebox.askyesno("Are you sure you would like to overwite the current project tree?")):
                return        

        self.optionWindow = tk.Toplevel()
        self.optionWindow.grab_set()

        fromDirButton = ttk.Button(self.optionWindow, text = "From Photo Directory", command = self.GenProjFromDirTree)
        fromXlsxButton = ttk.Button(self.optionWindow, text = "From Excel File", command = self.GenProjFromXlsx)   

        fromDirButton.pack()
        fromXlsxButton.pack()

    def GenProjFromDirTree(self):
        self.optionWindow.grab_release()
        self.optionWindow.destroy()

        self.reportGen.treeView.tree = self.photoProcessTab.treeView.tree

    def GenProjFromXlsx(self):
        self.optionWindow.grab_release()
        self.optionWindow.destroy()

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