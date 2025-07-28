import tkinter as tk
from tkinter import messagebox, filedialog, ttk
import EntryBoxTable
import PrevNextUI
import pandas as pd
import traceback
import OrderedListBox
import Project

class ExcelImportWizard(tk.Toplevel):
    def __init__(self, project : Project.Project, docPath = None, debug = False):
        super().__init__()
        self.grab_set()
        self.title("Import Wizard")
        #self.geometry("600x400")
        self.project = project
        self.result = None
        self.data = None
        self.selectedHierarchyCols = []
        self.sheetNames = []  

        self.navButtons = PrevNextUI.PrevNextButtonUI(self, labelText = "Sheet Navigation")
        self.tableFrame = tk.Frame(self)
        self.table = None
        self.currentTable = 0
        self.label = tk.Label(self)

        self.buttonFrame = tk.Frame(self)        
        self.heirarchyButton = ttk.Button(self.buttonFrame, command = self.SetHeirarchyCols, text = "Make Heirarchy Columns")
        self.openButton = ttk.Button(self.buttonFrame, command = self.OpenXlsx, text = "Open...")
        self.reloadButton = ttk.Button(self.buttonFrame, command = self.Reload, text = "Reload Excel")
        self.finishButton = ttk.Button(self.buttonFrame, command = self.Finish, text = "Finish")
        self.hierarchyListbox = OrderedListBox.OrderedListbox(self.buttonFrame, text = "Heirarchy Order", height = 5)

        if debug:
            self.buttonFrame.configure(bg="lightblue")
            self.hierarchyListbox.configure(bg = "green")

        self.hierarchyListbox.grid(row=0, column=0, rowspan=2, sticky="nswe", padx=4, pady=4)
        self.heirarchyButton.grid(row=0, column=1, sticky="new", padx=2)
        self.openButton.grid(row=0, column=2, sticky="new", padx=2)
        self.reloadButton.grid(row=0, column=3, sticky="new", padx=2)
        self.finishButton.grid(row=0, column=4, sticky="new", padx=2) 
        
        self.navButtons.pack()
        self.tableFrame.pack(fill="both", expand=True)
        self.buttonFrame.pack(padx=4, pady=4, expand = True)
        self.label.pack(expand = True)

        self.bind("<<Left>>", lambda e: self.ChangeTable(-1))
        self.bind("<<Right>>", lambda e: self.ChangeTable(1))
        
        if docPath is not None:
            self.OpenXlsx(path = docPath)
        else:
            self.LoadFromProject()


    def ChangeTable(self, inc, save = True):

        if self.table is not None:
            if save:
                self.SaveTable()
            self.table.destroy()

        self.currentTable+=inc

        self.table = EntryBoxTable.EntryBoxTable(self.tableFrame)
        self.table.ImportDataFrame(list(self.data.values())[self.currentTable%len(self.data)])
        self.table.pack(fill="both", expand = True)
        self.label.config(text=f"Sheet: {self.currentTable%len(self.data) + 1}")

        self.Finish(destroy=False)

    def LoadFromProject(self):
        print("Loading Project Data")
        try:
            data = self.project.data
            assert type(data) == pd.DataFrame
            self.data = {0 : data}  # or self.project.tables
            self.sheetNames = list(self.data.keys())
            for col in self.project.hierarchyColumns:
                self.hierarchyListbox.insert(tk.END, col)
            self.ChangeTable(0)
        except Exception as e:
            traceback.print_exc()
            messagebox.showerror("Failed to load project data", str(e))

    def OpenXlsx(self, path = None):
        if path is None:
            path = filedialog.askopenfilename()
            self.path = path
        if path == "":
            return False
        else:
            try:
                self.data = pd.read_excel(path, sheet_name=None)
                self.sheetNames = list(self.data.keys())
                self.path = path
                
            except Exception as e:
                messagebox.showerror(f"Could not load file", message=e)
                self.path = None
                return False
        self.ChangeTable(0, save=False) 
 
    def SetHeirarchyCols(self):
        self.hierarchyListbox.deleteAll()
        for col in self.table.workingData[[label.Get() for label in self.table.selectedColumns]].columns:
            self.hierarchyListbox.insert(tk.END, col)
        self.table.DeselectAll()
    
    def Reload(self):
        self.OpenXlsx(path = self.path)
    
    def SaveTable(self):
        self.table.Save()        
        self.data[self.sheetNames[self.currentTable%len(self.sheetNames)]] = self.table.allData               

    def Finish(self, destroy = True):
        self.SaveTable()
        result = pd.DataFrame()
        for k,v in self.data.items():
            result = pd.concat([result, v], ignore_index=True)
        self.project.data = result
        self.project.SetHierarchyColumns(list(self.hierarchyListbox.get()))
        if destroy:
            self.destroy()

def main():
    root = tk.Tk()
    path = r"C:\Users\alexm\OneDrive\Documents\Code Projects\PYTHON\apps\Inspection App\dummy HRSG1.xlsx"
    project = Project.Project("Wizard Testing")
    importWizard = ExcelImportWizard(project, debug=True, docPath=path)
    root.wait_window(importWizard)
    root.destroy()
    root.mainloop()

if __name__ == "__main__":
    main()