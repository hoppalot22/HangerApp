import tkinter as tk
from tkinter import messagebox, filedialog, ttk
import EntryBoxTable
import PrevNextUI
import pandas as pd

class ExcelImportWizard(tk.Toplevel):
    def __init__(self, docPath):
        super().__init__()
        self.grab_set()
        self.title("Import Wizard")
        self.geometry("600x400")
        self.result = None       

        self.navButtons = PrevNextUI.PrevNextButtonUI(self, labelText = "Sheet Navigation")
        self.tableFrame = tk.Frame(self)
        self.table = EntryBoxTable.EntryBoxTable(self.tableFrame)
        self.currentTable = 0
        self.label = tk.Label(self)

        self.OpenXlsx(path = docPath)

        self.buttonFrame = tk.Frame(self)
        self.openButton = ttk.Button(self.buttonFrame, command = self.OpenXlsx, text = "Open...")
        self.finishButton = ttk.Button(self.buttonFrame, command = self.Finish, text = "Finish")

        self.openButton.pack(side = "left")
        self.finishButton.pack(side = "left")    
        
        self.navButtons.pack()
        self.tableFrame.pack(fill="both", expand=True)
        self.buttonFrame.pack(side = "right", padx=4, pady=4)
        self.label.pack(fill="x")

        self.bind("<<Left>>", lambda e: self.ChangeTable(-1))
        self.bind("<<Right>>", lambda e: self.ChangeTable(1))

    def ChangeTable(self, inc):
        self.currentTable+=inc

        self.table.destroy()
        self.table = EntryBoxTable.EntryBoxTable(self.tableFrame)
        self.table.ImportDataFrame(list(self.data.values())[self.currentTable%len(self.data)])
        self.table.pack(fill="both", expand = True)
        self.label.config(text=f"Sheet: {self.currentTable%len(self.data) + 1}")

    def OpenXlsx(self, path = None):
        if path is None:
            path = filedialog.askopenfilename()
        try:
            self.data = pd.read_excel(path, sheet_name=None)
        except Exception as e:
            messagebox.showerror(f"Could not load file", message=e)
        self.ChangeTable(0)  

    def Finish(self):
        self.result = self.table.workingData
        self.destroy()

def main():
    root = tk.Tk()
    path = "D:\\Python\\Apps\\Report Generation\\Hanger Report\\NRG 2024\\U4 Inspection information R3.xlsx"

    importWizard = ExcelImportWizard(path)
    root.wait_window(importWizard)
    print(importWizard.result)

    root.mainloop()

if __name__ == "__main__":
    main()