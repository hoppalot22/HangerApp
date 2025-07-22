import tkinter as tk
from tkinter import ttk
from string import ascii_uppercase
from tkinter import font

class EntryBoxTable(tk.Frame):
    def __init__(self, parent, cellWidth = 15):
        super().__init__(parent)
        self.numRows = 0
        self.numColumns = 0
        self.cellWidth = cellWidth

        self.font = font.nametofont("TkDefaultFont")

        self.frame = tk.Frame()
        self.canvas = tk.Canvas(self.frame)
        self.tableFrame = tk.Frame(self.canvas)
        
        self.buttonFrame = tk.Frame(self)
        self.addRowsField = tk.Entry(self.buttonFrame)
        self.addColsField = tk.Entry(self.buttonFrame)

        self.addRowsButton = ttk.Button(self.buttonFrame, text = "Add Rows", command=self.AddRowsButton)
        self.addColsButton = ttk.Button(self.buttonFrame, text = "Add Columns", command=self.AddColsButton)

        self.addRowsField.pack(side = "left")
        self.addRowsButton.pack(side = "left")
        self.addColsField.pack(side = "left")
        self.addColsButton.pack(side = "left")

        self.grid = []



        # Create a Canvas and Scrollbars

        scroll_y = tk.Scrollbar(self.frame, orient="vertical", command=self.canvas.yview)
        scroll_x = tk.Scrollbar(self.frame, orient="horizontal", command=self.canvas.xview)

        # Configure the Canvas to scroll the Frame
        self.canvas.create_window((0, 0), window=self.tableFrame, anchor="nw")
        self.canvas.configure(yscrollcommand=scroll_y.set, xscrollcommand=scroll_x.set)

        # Pack the Canvas and Scrollbars
        self.canvas.grid(row=1, column=1, sticky="nsew")
        scroll_y.grid(row=1, column=2, sticky="ns")
        scroll_x.grid(row=2, column=1, sticky="ew")


        self.header_frame = tk.Frame(self.frame)
        self.header_frame.grid(row=0, column=1, sticky="ew")
        self.left_header_frame = tk.Frame(self.frame)
        self.left_header_frame.grid(row=1, column=0, sticky="ns")

        self.frame.pack()
        self.buttonFrame.pack()
        self.tableFrame.bind("<Configure>", self._on_frame_configure)

        self.AddRows(1)
        self.AddCols(1)

    def _on_frame_configure(self, event):
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def AddRowsButton(self):
        numRows = int(self.addRowsField.get())
        self.AddRows(numRows)

    def AddColsButton(self):
        numCols = int(self.addColsField.get())
        self.AddCols(numCols)

    def AddRows(self, numRows):
        for i in range(numRows):
            cells = []
            header = tk.Label(self.left_header_frame, text=str(self.numRows + i + 1), width=4, relief="ridge", font = self.font)
            header.grid(row=self.numRows + i, column=0)
            for j in range(self.numColumns):
                entry = tk.Entry(self.tableFrame, width=self.cellWidth, font = self.font)
                cells.append(entry)
                entry.grid(row=self.numRows+i, column=j, padx=0, pady=0)
            self.grid.append(cells)
        self.numRows += numRows

    def AddCols(self, numCols):
        for j in range(numCols):
            header = tk.Label(self.header_frame, text=ascii_uppercase[(self.numColumns + j) % 26], width=self.cellWidth, relief="ridge", font=self.font)
            header.grid(row=0, column=self.numColumns + j, sticky="nsew")
            for i in range(self.numRows):
                entry = tk.Entry(self.tableFrame, width=self.cellWidth, font = self.font)
                self.grid[i].append(entry)
                entry.grid(row=i, column=self.numColumns + j, padx=0, pady=0)
        
        self.numColumns += numCols

def main():
    root = tk.Tk()
    table = EntryBoxTable(root)
    table.pack()
    tk.mainloop()

if __name__ == "__main__":
    main()