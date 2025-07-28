import tkinter as tk
from tkinter import ttk

class TreeItemDataViewer(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent)

        self.selectedKeys = set()

        # Create Treeview with two columns: Key and Value
        self.tree = ttk.Treeview(self, columns=("Field", "Value"), show="headings")
        self.tree.bind("<Button-1>", self.OnClick)
        
        self.tree.heading("Field", text="Field")
        self.tree.heading("Value", text="Value")

        self.tree.column("Field", anchor="w")
        self.tree.column("Value", anchor="w")

        # Scrollbar
        scrollbar = ttk.Scrollbar(self, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)

        self.tree.insert("", "end", text = "No Data")
        self.defaultColour = ttk.Style().lookup("Treeview", "background")
        self.highlightColour = "#021caf"

        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

    def OnClick(self, event):
        pass

    def DeSelectAll(self):
        pass
    
    def GetSelectedKeys(self):
        return list(self.selectedKeys)
    
    def DisplayData(self, dataDict, prioityFields = None):
        self.tree.delete(*self.tree.get_children())

        if prioityFields is None:
            prioityFields = []

        # First show fields of interest
        for key in prioityFields:
            if key in dataDict:
                self.tree.insert("", "end", values=(key, dataDict[key]))

        # Then show remaining fields
        for key, value in dataDict.items():
            if key not in prioityFields:
                self.tree.insert("", "end", values=(key, value), tags = ("nonInterest"))

        self.tree.tag_configure("nonInterest", background="#fcb0b0")  # light red
