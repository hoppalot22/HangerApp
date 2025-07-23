import tkinter as tk
from tkinter import filedialog
import EntityColumn
import Treeviews
import ImportWizard

class ReportGenTab(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.statusText = "empty"

        self.buttonColumn = EntityColumn.EntityColumn(self)

        self.buttonColumn.AddButton("Open", text ="Open Project...", command = self.Open)
        self.buttonColumn.AddButton("Save", text ="Save Project", command = self.Save)
        self.buttonColumn.AddButton("Generate", text ="Generate Report", command = self.GenerateReport)
        self.buttonColumn.AddButton("Import", text ="Import Excel", command = self.ImportXlsx)

        self.treeView = Treeviews.ProjectTree(self, "MyProject")
        self.treeView.bind("<<TreeViewSelect>>", self.TreeUpdate)
        self.treeView.pack(anchor="ne")
        self.buttonColumn.pack(anchor="ne", pady = 3)

    def ImportXlsx(self):
        docPath = filedialog.askopenfilename()
        excelWizard = ImportWizard.ExcelImportWizard(self, docPath)
        self.wait_window(excelWizard)
        self.data = excelWizard.result

    def Open(self):
        pass

    def Save(self):
        pass
    
    def GenerateReport(self):
        pass

    def TreeUpdate(self):
        pass
