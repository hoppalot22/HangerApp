import tkinter as tk
import EntityColumn
import Project

class JobPrepareTab(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.parent = parent
        self.controller = controller

        project = controller.project
        assert type(project) == Project.Project
        self.project = project

        self.statusText = "empty"

        self.hangerData = None

        processColumn = EntityColumn.EntityColumn(self)
        processColumn.AddButton("Generate", text="Generate QR codes", command = self.GenerateQRs)
        processColumn.AddButton("Template", text ="Create .xlsx template", command = self.CreateTemp)

        processColumn.pack(anchor = "ne")

    def Update(self):
        self.project = self.controller.project
        pass
    
    def GenerateQRs(self):
        pass

    def CreateTemp(self):
        pass
