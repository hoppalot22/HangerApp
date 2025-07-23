import tkinter as tk

class PrevNextButtonUI(tk.Frame):
    def __init__(self, parent, labelText = None, **kwargs):
        super().__init__(parent)
        self.parent = parent
        self.label = tk.Label(self, text = labelText)
        self.leftButton = tk.Button(self, text = "<", command = self.Left)
        self.rightButton = tk.Button(self, text = ">", command = self.Right)

        self.leftButton.pack(side="left")
        self.label.pack(side="left", expand = True)
        self.rightButton.pack(side="right")

    def Left(self):
        self.event_generate("<<Left>>")

    def Right(self):
        self.event_generate("<<Right>>")   
