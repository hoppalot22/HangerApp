import tkinter as tk
from tkinter import ttk
from string import ascii_uppercase
from tkinter import font
import EditableLabel
import pandas as pd

class EntryBoxTable(tk.Frame):
    def __init__(self, parent, cellWidth = 15):
        super().__init__(parent)

        self.allData = pd.DataFrame()
        self.workingData = pd.DataFrame()
        self.cellWidth = cellWidth
        self.headings = {}
        self.rowHeadings = {}

        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        self.selectedRows = []
        self.selectedColumns = []

        self.font = font.nametofont("TkDefaultFont")

        self.frame = tk.Frame(self)
        self.frame.grid_rowconfigure(1, weight=1)
        self.frame.grid_columnconfigure(1, weight=1)

        self.canvas = tk.Canvas(self.frame, background="gray")

        self.tableFrame = tk.Frame(self.canvas)
        
        self.buttonFrame1 = tk.Frame(self)
        self.buttonFrame2 = tk.Frame(self)
        self.addRowsField = tk.Entry(self.buttonFrame1)
        self.addColsField = tk.Entry(self.buttonFrame1)

        self.addRowsButton = ttk.Button(self.buttonFrame1, text = "Add Rows", command=self.AddRowsButton)
        self.addColsButton = ttk.Button(self.buttonFrame1, text = "Add Columns", command=self.AddColsButton)
        self.delRowsButton = ttk.Button(self.buttonFrame2, text = "Delete Rows", command=self.DeleteRows)
        self.delColsButton = ttk.Button(self.buttonFrame2, text = "Delete Columns", command=self.DeleteCols)

        self.addRowsField.pack(side = "left")
        self.addRowsButton.pack(side = "left")
        self.addColsField.pack(side = "left")
        self.addColsButton.pack(side = "left")
        self.delRowsButton.pack(side = "left")
        self.delColsButton.pack(side = "left")

        self.grid = []

        # Create a Canvas and Scrollbars

        scroll_y = tk.Scrollbar(self.frame, orient="vertical", command=self.canvas.yview)
        scroll_x = tk.Scrollbar(self.frame, orient="horizontal", command=self.canvas.xview)

        # Configure the Canvas to scroll the Frame
        self.canvas.create_window((0, 0), window=self.tableFrame, anchor="nw")
        self.canvas.configure(yscrollcommand=scroll_y.set, xscrollcommand=scroll_x.set)

        # Pack the Canvas and Scrollbars
        self.canvas.grid(row=1, column=1, sticky="nsew")
        scroll_y.grid(row=1, column=2, sticky="nse")
        scroll_x.grid(row=2, column=1, sticky="sew")

        self.frame.pack(fill="both", expand=True)
        self.buttonFrame1.pack()
        self.buttonFrame2.pack()
        self.tableFrame.bind("<Configure>", self._on_frame_configure)        

        self.AddRows(1)
        self.AddCols(1)

        self.bind_mousewheel_recursive(self.canvas)

        initLabel = self.headings[0]
        assert type(initLabel) == EditableLabel.EditableLabel
        self.defaultColour = initLabel.cget("background")

    def bind_mousewheel_recursive(self, widget):
        widget.bind("<Enter>", lambda e: self._bind_mousewheel(e))
        widget.bind("<Leave>", lambda e: self._unbind_mousewheel(e))
        for child in widget.winfo_children():
            self.bind_mousewheel_recursive(child)
    
    def _bind_mousewheel(self, event):
        self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)         # Windows & macOS
        self.canvas.bind_all("<Shift-MouseWheel>", self._on_shift_mousewheel)
        self.canvas.bind_all("<Button-4>", self._on_mousewheel_linux)     # Linux scroll up
        self.canvas.bind_all("<Button-5>", self._on_mousewheel_linux)     # Linux scroll down

    def _unbind_mousewheel(self, event):
        self.canvas.unbind_all("<MouseWheel>")
        self.canvas.bind_all("<Shift-MouseWheel>")
        self.canvas.unbind_all("<Button-4>")
        self.canvas.unbind_all("<Button-5>")

    def _on_mousewheel(self, event):
        self.canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

    def _on_shift_mousewheel(self, event):
        self.canvas.xview_scroll(-1 * (event.delta // 120), "units")

    def _on_mousewheel_linux(self, event):
        if event.num == 4:
            self.canvas.yview_scroll(-1, "units")
        elif event.num == 5:
            self.canvas.yview_scroll(1, "units")

    def _on_frame_configure(self, event):
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def AddRowsButton(self):
        numRows = int(self.addRowsField.get())
        self.AddRows(numRows)

    def AddColsButton(self):
        numCols = int(self.addColsField.get())
        self.AddCols(numCols)

    def ImportDataFrame(self, df : pd.DataFrame, overwrite = True):
        if overwrite:
            self.allData = df
        self.workingData = df    
        rows, cols = df.shape
        for row in self.grid:
            for cell in row:
                assert type(cell) == tk.Entry
                cell.destroy()
        for heading in self.headings.values():
            heading.destroy()
        for rowHeading in self.rowHeadings.values():
            rowHeading.destroy()

        self.grid = []
        self.headings = {}
        self.rowHeadings = {}
        headings = df.columns

        self.AddRows(rows)
        self.AddCols(cols)
        self.Headings(headings)

        for i, row in enumerate(self.grid):
            for j, cell in enumerate(row):
                assert type(cell) == tk.Entry
                cell.insert(0, str(df[df.columns[j]][i]))

        self.bind_mousewheel_recursive(self.canvas)

    
    def AddRows(self, numRows):
        for i in range(numRows):
            cells = []
            header = EditableLabel.EditableLabel(self.tableFrame, text=str(len(self.grid) + 1), width=4, relief="ridge", font = self.font)
            self.rowHeadings[len(self.grid) + 1] = header
            header.grid(row=len(self.grid)+1, column=0)
            header.bind("<Button-1>", self.SelectRow)
            for j in range(len(self.headings)):
                entry = tk.Entry(self.tableFrame, font = self.font)
                cells.append(entry)
                entry.grid(row=len(self.grid)+1, column=j+1, padx=0, pady=0, sticky="nsew")
            self.grid.append(cells)

    def AddCols(self, numCols):
        for j in range(numCols):
            header = EditableLabel.EditableLabel(self.tableFrame, text=ascii_uppercase[(len(self.headings)) % 26], width=0, relief="ridge", font=self.font)
            self.headings[len(self.headings)] = header
            header.grid(row=0, column=len(self.headings), sticky="nsew")
            header.bind("<Button-1>", self.SelectCol)
            for i in range(len(self.grid)):
                entry = tk.Entry(self.tableFrame, font = self.font)
                self.grid[i].append(entry)
                entry.grid(row=i+1, column=len(self.headings), padx=0, pady=0, sticky="nsew")


    def DeleteRows(self):
        df = self.workingData.drop([int(text.cget("text"))-1 for text in self.selectedRows]).reset_index(drop=True)
        self.selectedRows = []
        self.selectedColumns = []
        self.ImportDataFrame(df, overwrite=False)

    def DeleteCols(self):
        print(self.selectedColumns)
        df = self.workingData.drop([text.cget("text") for text in self.selectedColumns], axis = 1)
        self.selectedRows = []
        self.selectedColumns = []
        self.ImportDataFrame(df, overwrite=False)
            

    def Headings(self, headings):
        numColsRequired = len(headings) - len(self.headings)
        if numColsRequired > 0:
            self.AddCols(numColsRequired)
        for i, header in enumerate(headings):
            label = self.headings[i]
            assert type(label) == EditableLabel.EditableLabel
            label.configure(text=header)
    
    def SelectRow(self, event : tk.Event):
        heading = event.widget
        assert type(heading) == EditableLabel.EditableLabel
        if heading in self.selectedRows:
            self.selectedRows.remove(heading)
            heading.configure(background = self.defaultColour)
        else:
            self.selectedRows.append(heading)
            heading.configure(background = "#%02x%02x%02x" % (200, 220, 255))

    def SelectCol(self, event : tk.Event):
        heading = event.widget
        assert type(heading) == EditableLabel.EditableLabel
        if heading in self.selectedColumns:
            self.selectedColumns.remove(heading)
            heading.configure(background = self.defaultColour)
        else:
            self.selectedColumns.append(heading)
            heading.configure(background = "#%02x%02x%02x" % (200, 220, 255))



def main():
    root = tk.Tk()
    myDf = pd.DataFrame()
    myDf["x"] = [1,2,3]
    myDf["y"] = [3,4,5]
    myDf["z"] = [3,2,1]
    table = EntryBoxTable(root)
    table.ImportDataFrame(myDf)
    table.pack(expand=True, fill="both")
    tk.mainloop()

if __name__ == "__main__":
    main()