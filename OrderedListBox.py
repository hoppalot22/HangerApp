import tkinter as tk
from tkinter import ttk

class OrderedListbox(tk.LabelFrame):
    def __init__(self, master=None, height = 0, **kwargs):
        super().__init__(master, **kwargs)

        self.listbox = tk.Listbox(self, selectmode="extended", exportselection=False, height=height)

        # Reorder buttons
        btn_frame = tk.Frame(self)

        # Add scrollbar
        scrollbar = ttk.Scrollbar(self, orient="vertical", command=self.listbox.yview)

        self.listbox.configure(yscrollcommand=scrollbar.set)

        self.up_button = ttk.Button(btn_frame, text=" ↑ ", command=self.move_up, width=0)
        self.up_button.pack(fill="x")

        self.down_button = ttk.Button(btn_frame, text=" ↓ ", command=self.move_down, width=0)
        self.down_button.pack(fill="x")

        scrollbar.pack(side="left", fill="y")
        btn_frame.pack(side="left", fill="y", padx=5)
        self.listbox.pack(side="left", fill="both", expand=True)

    def insert(self, index, item):
        self.listbox.insert(index, item)

    def get(self, start=None, end=None):
        if start is None and end is None:
            return self.listbox.get(0, tk.END)
        return self.listbox.get(start, end)

    def deleteAll(self):
        for index, item in enumerate(self.get()):
            self.delete(0)
    
    def delete(self, index):
        self.listbox.delete(index)

    def move_up(self):
        selected = self.listbox.curselection()
        for i in selected:
            if i == 0:
                continue
            text = self.listbox.get(i)
            self.listbox.delete(i)
            self.listbox.insert(i - 1, text)
            self.listbox.selection_set(i - 1)

    def move_down(self):
        selected = list(self.listbox.curselection())[::-1]
        count = self.listbox.size()
        for i in selected:
            if i >= count - 1:
                continue
            text = self.listbox.get(i)
            self.listbox.delete(i)
            self.listbox.insert(i + 1, text)
            self.listbox.selection_set(i + 1)
