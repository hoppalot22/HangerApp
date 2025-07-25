import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import EntityColumn

class OptionWindow(tk.Toplevel):
    def __init__(self, funcMap : dict = {}):
        super().__init__()

        self.funcMap = funcMap
        
        self.buttonColumn = EntityColumn.EntityColumn(self)

        for bText, func in self.funcMap.items():
            self.buttonColumn.AddButton(bText, text = bText, command = lambda f=func: self.ReturnSelection(f))
        self.buttonColumn.pack(expand=True, fill="both")

    def ReturnSelection(self, func):
        self.destroy()
        func()
