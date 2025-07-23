import tkinter as tk
import EntityColumn

class JobPrepareTab(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.statusText = "empty"

        self.hangerData = None

        processColumn = EntityColumn.EntityColumn(self)
        processColumn.AddButton("Generate", text="Generate QR codes", command = self.GenerateQRs)
        processColumn.AddButton("Template", text ="Create .xlsx template", command = self.CreateTemp)

        processColumn.pack(anchor = "ne")

    def GenerateQRs(self):
        pass

    def CreateTemp(self):
        pass
