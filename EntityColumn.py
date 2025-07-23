import tkinter as tk
from tkinter import ttk

class EntityColumn(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.entities = {}
        self.maxWidth = 0      
        
    def AddButton(self, name, **kwargs):
        button = tk.Button(self, **kwargs)
        button.pack(fill="both", expand=True)
        self.AddToEntityList(button, name)
        self.UpdateWidth(button.winfo_width())

    def AddField(self, name, text = "Unnamed"):
        frame = ttk.Frame(self)
        entryBox = tk.Entry(frame)
        label = tk.Label(frame, text = text)
        entryBox.pack(side = "left")
        label.pack(side = "left")
        frame.pack(side = "top", anchor="nw", fill="both", expand=True)
        self.AddToEntityList(entryBox, name)
        self.UpdateWidth(entryBox.winfo_width())

    def AddCheckBox(self, parent, name, **kwargs):
        checkBox = tk.Checkbutton(parent, **kwargs)
        checkBox.pack(fill="both", expand=True)
        self.AddToEntityList(checkBox, name)
        self.UpdateWidth(checkBox.winfo_width())

    def AddToEntityList(self, myObject, name):
        if name in self.entities.values():
            object.destroy()
            raise("Entity name already in use in this column")
        else:
            self.entities[name] = myObject

    def UpdateWidth(self, entityWidth):
        for name, entity in self.entities.items():
            if entityWidth > self.maxWidth:
                self.maxWidth = entityWidth
        
        self.configure(width=self.maxWidth)
