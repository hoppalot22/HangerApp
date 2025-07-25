import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import EntityColumn
import Treeviews
import ImportWizard
import OptionWindow

class ReportGenTab(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.statusText = "empty"

        self.data = None

        self.buttonColumn = EntityColumn.EntityColumn(self)

        self.buttonColumn.AddButton("Open", text ="Open Project...", command = self.Open)
        self.buttonColumn.AddButton("Save", text ="Save Project", command = self.Save)
        self.buttonColumn.AddButton("Generate", text ="Generate Report", command = self.GenerateReport)
        self.buttonColumn.AddButton("Import", text ="Import Excel", command = self.ImportXlsx)
        self.buttonColumn.AddButton("GenProj", text = "Generate From...", command = self.GenerateProj)

        self.treeView = Treeviews.ProjectTree(self, "MyProject")
        self.treeView.bind("<<TreeViewSelect>>", self.TreeUpdate)

        self.treeView.pack(anchor="ne")
        self.buttonColumn.pack(anchor="ne", pady = 3)

    def ImportXlsx(self):
        docPath = filedialog.askopenfilename()
        excelWizard = ImportWizard.ExcelImportWizard(docPath)
        self.wait_window(excelWizard)
        self.data = excelWizard.result

    def GenerateProj(self):
        projTree = self.treeView.tree

        if not (len(projTree.get_children()) == 0):
            if not (messagebox.askyesno("Are you sure you would like to overwite the current project tree?")):
                return        

        funcMap = {
            "From Photo Directory" : self.GenProjFromDirTree,
            "From Excel File" : self.GenProjFromXlsx
        }

        OptionWindow.OptionWindow(funcMap = funcMap)

    def GenProjFromDirTree(self):
        print("Dir called")

    def GenProjFromXlsx(self):

        excelPath = filedialog.askopenfilename()
        wizard = ImportWizard.ExcelImportWizard(excelPath) 
        wizard.wait_window()
        self.data = wizard.result
        print(self.data)
    
    def Open(self):
        pass

    def Save(self):
        pass
    
    def GenerateReport(self):
        pass

    def TreeUpdate(self):
        pass
