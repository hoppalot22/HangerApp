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
        self.data = None
        self.result = None       

        self.navButtons = PrevNextUI.PrevNextButtonUI(self, labelText = "Sheet Navigation")
        self.tableFrame = tk.Frame(self)
        self.table = EntryBoxTable.EntryBoxTable(self.tableFrame)
        self.currentTable = 0
        self.label = tk.Label(self)

        self.buttonFrame = tk.Frame(self)
        self.openButton = ttk.Button(self.buttonFrame, command = self.OpenXlsx, text = "Open...")
        self.reloadButton = ttk.Button(self.buttonFrame, command = self.Reload, text = "Reload Excel")
        #self.saveButton = ttk.Button(self.buttonFrame, command = self.SaveTable, text = "Save Table")
        self.finishButton = ttk.Button(self.buttonFrame, command = self.Finish, text = "Finish")

        self.openButton.pack(side = "left")
        self.reloadButton.pack(side = "left")    
        #self.saveButton.pack(side = "left")    
        self.finishButton.pack(side = "left")    
        
        self.navButtons.pack()
        self.tableFrame.pack(fill="both", expand=True)
        self.buttonFrame.pack(side = "right", padx=4, pady=4)
        self.label.pack(fill="x")

        self.bind("<<Left>>", lambda e: self.ChangeTable(-1))
        self.bind("<<Right>>", lambda e: self.ChangeTable(1))
        
        self.OpenXlsx(path = docPath)


    def ChangeTable(self, inc):

        print(self.data)
        self.SaveTable()
        self.currentTable+=inc

        self.table.destroy()
        self.table = EntryBoxTable.EntryBoxTable(self.tableFrame)
        self.table.ImportDataFrame(list(self.data.values())[self.currentTable%len(self.data)])
        self.table.pack(fill="both", expand = True)
        self.label.config(text=f"Sheet: {self.currentTable%len(self.data) + 1}")

    def OpenXlsx(self, path = None):
        if path is None:
            path = filedialog.askopenfilename()
            self.path = path
        if path == "":
            return False
        else:
            try:
                self.data = pd.read_excel(path, sheet_name=None)
                self.path = path
                
            except Exception as e:
                messagebox.showerror(f"Could not load file", message=e)
                self.path = None
                return False
        self.ChangeTable(0) 
 
    def Reload(self):
        self.OpenXlsx(path = self.path)
    
    def SaveTable(self):
        self.table.Save()
        
        self.data[self.table.sheetNames[self.currentTable%len(self.table.sheetNames)]] = self.table.allData               

    def Finish(self):
        self.table.Save()
        result = pd.DataFrame()
        for k,v in self.data.items():
            result = pd.concat([result, v], ignore_index=True)
        self.result = result
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