import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import EntityColumn
import Treeviews
import ImportWizard
import OptionWindow
import pickle
import Project
import TreeItemDataViewer

class ReportGenTab(tk.Frame):
    def __init__(self, parent, project : Project.Project):
        super().__init__(parent)
        self.parent = parent
        self.project = project
        self.statusText = "empty"

        self.data = None
        self.currentRowIndex = 0

        self.dataViewerFrame = tk.Frame(self)
        self.rhsFrame = tk.Frame(self)

        self.buttonColumn = EntityColumn.EntityColumn(self.rhsFrame)

        self.buttonColumn.AddButton("Open", text ="Open Project...", command = self.Open)
        self.buttonColumn.AddButton("Save", text ="Save Project", command = self.Save)
        self.buttonColumn.AddButton("Edit", text ="Edit Data", command = self.Edit)
        self.buttonColumn.AddButton("Generate", text ="Generate Report", command = self.GenerateReport)
        self.buttonColumn.AddButton("GenProj", text = "Generate From...", command = self.GenerateProj)

        self.treeView = Treeviews.ProjectTree(self.rhsFrame, "MyProject")
        self.treeView.tree.bind("<<TreeviewSelect>>", self.OnTreeSelect)

        self.dataViewer = TreeItemDataViewer.TreeItemDataViewer(self.dataViewerFrame)
        self.dataViewer.tree.bind("<Double-1>", self.OnDoubleClick)
        self.interestBtn = tk.Button(self.dataViewerFrame, text="Toggle Relevant Fields", command=self.ToggleInterest)
        self.interestBtn.pack()


        self.dataViewer.pack(fill="both", expand=True)

        self.treeView.pack(anchor="ne")
        self.buttonColumn.pack(pady = 3, side = "right", anchor="ne")

        self.dataViewerFrame.pack(side="left", expand=True, fill="both")
        self.rhsFrame.pack(side="left", expand=True, fill="y")

    def GenerateProj(self):
        projTree = self.treeView.tree

        if not (len(projTree.get_children()) == 0):
            if not (messagebox.askyesno("Are you sure you would like to overwite the current project tree?")):
                return        

        funcMap = {
            "From Photo Directory" : self.GenProjFromDirTree,
            "From Excel File" : self.GenProjFromXlsx
        }

        OptionWindow.OptionWindow(funcMap = funcMap)

    def GenProjFromDirTree(self):
        print("Dir called")

    def GenProjFromXlsx(self):

        excelPath = filedialog.askopenfilename()
        wizard = ImportWizard.ExcelImportWizard(self.project, docPath = excelPath) 
        wizard.wait_window()
        self.UpdateTree()
    
    def GenerateReport(self):
        pass

    def OnTreeSelect(self, event):
        selectedItem = self.treeView.tree.selection()
        if not selectedItem:
            return

        itemText = self.treeView.tree.item(selectedItem, "text")

        def TreeDepth(tree : ttk.Treeview, nodeId):
            depth = 0
            while tree.parent(nodeId):
                nodeId = tree.parent(nodeId)
                depth += 1
            return depth

        # Find matching row (based on deepest hierarchy level)
        hierarchyColumns = self.project.hierarchyColumns
        targetLevel = TreeDepth(self.treeView.tree, selectedItem)

        # Traverse up to build full hierarchy path
        path = []
        node = selectedItem[0]
        while node:
            item = self.treeView.tree.item(node)
            path.insert(0, item['text'])
            node = self.treeView.tree.parent(node)

        # Find matching rows
        df = self.project.data
        for col, val in zip(hierarchyColumns, path):
            df = df[df[col] == val]

        self.currentRowIndex = df.index[0]
        
        if not df.empty:
            rowData = self.project.data.iloc[self.currentRowIndex].to_dict()
            self.dataViewer.DisplayData(rowData, prioityFields = self.project.fieldsOfInterest)
        else:
            self.dataViewer.DisplayData({"Note": "No data found."})

    def Edit(self):
        wizard = ImportWizard.ExcelImportWizard(project = self.project) 
        wizard.wait_window()
        self.UpdateTree()

    def UpdateTree(self):
        self.treeView.tree.delete(*self.treeView.tree.get_children())

        hierarchyColumns = self.project.hierarchyColumns
        if not hierarchyColumns:
            return

        data = self.project.data.to_dict(orient="records")

        def InsertRecursive(parent, rows, depth):
            if depth >= len(hierarchyColumns):
                return

            col = hierarchyColumns[depth]
            seen = {}
            for row in rows:
                key = row[col]
                seen.setdefault(key, []).append(row)

            for key in sorted(seen.keys(), key=str):
                children = seen[key]
                nodeId = self.treeView.tree.insert(parent, "end", text=key)
                InsertRecursive(nodeId, children, depth + 1)

        InsertRecursive("", data, 0)

    def OnDoubleClick(self, event):
        region = self.dataViewer.tree.identify("region", event.x, event.y)
        if region != "cell":
            return

        rowId = self.dataViewer.tree.identify_row(event.y)
        column = self.dataViewer.tree.identify_column(event.x)

        if column != "#2":  # Only allow editing in the 'value' column
            return

        x, y, width, height = self.dataViewer.tree.bbox(rowId, column)
        value = self.dataViewer.tree.set(rowId, column)

        entry = tk.Entry(self.dataViewer.tree)
        entry.insert(0, value)
        entry.place(x=x, y=y, width=width, height=height)
        entry.focus()

        def SaveEdit(event=None):
            newValue = entry.get()
            self.dataViewer.tree.set(rowId, column, newValue)
            entry.destroy()

            key = self.dataViewer.tree.set(rowId, "#1")  # Get the corresponding key
            if self.currentRowIndex is not None:
                # Update the project data at the correct row and column
                self.project.data.at[self.currentRowIndex, key] = newValue

        entry.bind("<Return>", SaveEdit)
        entry.bind("<FocusOut>", SaveEdit)
    
    def ToggleInterest(self):
        for item in self.dataViewer.tree.selection():
            field = self.dataViewer.tree.set(item, "Field")
            if field in self.project.fieldsOfInterest:
                self.project.fieldsOfInterest.remove(field)
                self.dataViewer.tree.item(item, tags=("nonInterest"))
            else:
                self.project.fieldsOfInterest.add(field)
                self.dataViewer.tree.item(item, tags=("interest"))
        print(self.project.fieldsOfInterest)
        self.OnTreeSelect(None)
    
    def Save(self, saveAs = False):
        if self.project.savePath is None:
            saveAs = True
        if saveAs:
            self.project.savePath = filedialog.askopenfilename()
        with open(f'{self.project.savePath}.pkl', 'wb') as f:
            pickle.dump(self.project, f)

    def Open(self):
        self.project.savePath = filedialog.askopenfilename()
        with open(self.project.savePath, 'rb') as f:
            project = pickle.load(f)
        assert type(project) == Project.Project
        self.project = project
        self.UpdateTree()