import tkinter as tk
from tkinter import ttk

class FieldsWidget(tk.Frame):
    def __init__(self, parent, fields = []):
        super().__init__(parent)
        self.parent = parent
        self.comboBox = ttk.Combobox(self, values=["New Field", *fields])
        self.comboBox.set("New Field")
        self.comboBox.pack(side="top", fill="x", expand=True)
        self.fields = fields
        self.holdString = None
        self.lastChangedField = None
        self.lastChangedEntry = None

        self.entries = {}

        self.comboBox.bind("<<ComboboxSelected>>", self.OnSelect)


    def OnSelect(self, event):
        fieldName = self.comboBox.get()
        if not fieldName == "New Field":

            if fieldName in self.entries.keys():
                return

            self.entryFrame = tk.Frame(self)
            self.entryFrame.pack(side="top", fill="x", expand=True)

            label = tk.Label(self.entryFrame, text=fieldName)
            label.pack(side="left")

            self.entries[fieldName] = tk.Entry(self.entryFrame)
            self.entries[fieldName].bind("<FocusIn>", lambda e: self.HoldEntry(e))
            self.entries[fieldName].bind("<FocusOut>", lambda e: self.RevertChanges(e))
            self.entries[fieldName].bind("<Return>", lambda e, f = fieldName: self.UpdateData(e, f))
            self.entries[fieldName].pack(side="left", fill="x", expand=True)

            self.confirmButton = tk.Button(self.entryFrame, text="✓", command= lambda e, f=fieldName: self.UpdateData(e, f))
            self.confirmButton.pack(side="left")
            
            self.removeButton = tk.Button(self.entryFrame, text="X", command=lambda f=fieldName: self.RemoveField(f))
            self.removeButton.pack(side="left")

            self.comboBox.pack_forget()
            self.comboBox.pack(side="top", fill="x", expand=True)
            self.comboBox.set("New Field")

    def RemoveField(self, fieldName):
        if fieldName in self.entries.keys():
            self.entries[fieldName].master.destroy()
            del self.entries[fieldName]

    def HoldEntry(self, event):
        self.holdString = event.widget.get()
    
    def RevertChanges(self, event):
        if self.holdString is not None:
            event.widget.delete(0, tk.END)
            event.widget.insert(0, self.holdString)
            self.holdString = None
    
    def UpdateData(self, event, fieldName):
        #Emit signal notifying data has changed
        callingWidget = event.widget
        assert type(callingWidget) == tk.Entry
        self.lastChangedField = fieldName
        self.lastChangedEntry = callingWidget
        self.holdString = None
        self.event_generate("<<FieldsChanged>>", when="tail")
