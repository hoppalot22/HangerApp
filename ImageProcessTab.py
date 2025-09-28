import tkinter as tk
from tkinter import ttk, filedialog
import threading
import EntityColumn
import PrevNextUI
import perspectiveCorrect
import Treeviews
import os
import Project
import FieldsWidget
import copy

class ImageProcessTab(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.parent = parent
        self.controller = controller

        project = controller.project
        assert type(project) == Project.Project
        self.project = project

        self.imgPaths = None
        self.statusText = "empty"

        #Gui buttons/interface
        self.guiFrame = tk.Frame(self)
        self.guiFrame.pack(side = "left")

        self.hangerButtons = PrevNextUI.PrevNextButtonUI(self.guiFrame, labelText = "Hangers")
        self.hangerButtons.pack(expand = True)

        self.photoButtons = PrevNextUI.PrevNextButtonUI(self.guiFrame, labelText = "Photos")
        self.photoButtons.pack(expand = True)

        self.gui = perspectiveCorrect.ImageEditor(self.guiFrame)
        self.gui.pack(expand=1)

        self.perspcetiveCheckbox = tk.Checkbutton(self.guiFrame, text = "Perspective Correction Overlay", variable=self.gui.perspectiveOverlay, command = lambda : self.gui.UpdateScreen(resetZoom = True))
        self.perspcetiveCheckbox.pack(anchor = "w")

        self.hangerButtons.bind("<<Left>>", lambda e: self.HangerNav(-1))
        self.hangerButtons.bind("<<Right>>", lambda e: self.HangerNav(1))
        self.photoButtons.bind("<<Left>>", lambda e: self.PhotoNav(-1))
        self.photoButtons.bind("<<Right>>", lambda e: self.PhotoNav(1))

        #Treeview buttons/interface
        self.rhsFrame = tk.Frame(self)
        self.rhsFrame.pack(anchor="w")

        self.treeFrame = tk.Frame(self.rhsFrame)
        self.treeFrame.pack()

        self.buttonFrame = tk.Frame(self.rhsFrame)
        self.buttonFrame.pack()

        self.mapImgButton = tk.Button(self.buttonFrame, text = "Map Image/Folder", command = self.MapFolderToComponent)
        self.mapImgButton.pack(side="left")
        self.unmapImgButton = tk.Button(self.buttonFrame, text = "Unmap Image/Folder", command = self.UnMapComponent)
        self.unmapImgButton.pack(side="left")

        self.hideLooseImgs = tk.BooleanVar()
        self.hideLooseCheck = tk.Checkbutton(self.buttonFrame, text = "Hide Loose Images", variable=self.hideLooseImgs, command = lambda : print("Not implemented"))
        self.hideLooseCheck.pack(side="left")

        self.hideMappedImgs = tk.BooleanVar()
        self.hideMappedCheck = tk.Checkbutton(self.buttonFrame, text = "Hide Mapped Components", variable=self.hideMappedImgs, command = lambda : print("Not implemented"))
        self.hideMappedCheck.pack(side="left")

        self.dirTreeFrame = tk.Frame(self.treeFrame)
        self.dirTreeFrame.pack(side="left")
        self.projTreeFrame = tk.Frame(self.treeFrame)
        self.projTreeFrame.pack(side="left")

        self.dirTreeLabel = tk.Label(self.dirTreeFrame, text = "Directory Tree: ")
        self.dirTreeLabel.pack(anchor = "nw")

        self.projTreeLabel = tk.Label(self.projTreeFrame, text = "Project Tree: ")
        self.projTreeLabel.pack(anchor="nw")

        projTree = controller.reportGen.treeView
        assert type(projTree) == Treeviews.ProjectTree
        self.projTree = projTree.copy(self.projTreeFrame)

        self.dirTreeView = Treeviews.DirectoryTree(self.dirTreeFrame, headingText = "Image Folder")
        self.dirTreeView.bind("<<NodeSelect>>", self.TreeUpdate)
        self.dirTreeView.pack(expand=False, side = "left")

        self.projTree.bind("<<NodeSelect>>", self.TreeUpdate)
        self.projTree.pack(expand=False, side="left")

        self.treeStatusLabel = tk.Label(self.rhsFrame, text = "Tree Status: N/A")
        self.treeStatusLabel.pack(side="bottom")

        processColumn = EntityColumn.EntityColumn(self)
        processColumn.AddButton("Select Folder", text="Select Root Folder", command = self.SelectDirectory)
        processColumn.pack(anchor="nw")

        self.fieldWidget = FieldsWidget.FieldsWidget(self, fields = list(project.data.columns) if (project.data is not None) and (not project.data.empty) else [])
        self.fieldWidget.bind("<<FieldsChanged>>", lambda e: self.UpdateDataFromField(e))
        self.fieldWidget.pack(anchor="nw")

        statusLabel = tk.Label(self, text = self.statusText, wraplength = 400, justify = "center")
        statusLabel.pack(side = 'bottom')

        self.statusLabel = statusLabel

        self.SelectDirectory(askDialog=False)

    def getPictures(self):
        img_paths = []
        rootWalk = os.walk(self.project.photoFolder)
        rootWalk = [walk for walk in rootWalk]
        numFiles = sum([len(files[2]) for files in rootWalk])
        if numFiles == 0:
            self.statusText = f"No images found in {self.project.photoFolder}"
            print(rootWalk)
            self.after(0, lambda s=self.statusText: self.statusLabel.config(text=s))
            return
        
        counter = 0
        for root, dirs, files in rootWalk:
            for file in files:
                counter += 1
                if counter%10 == 0 or counter == numFiles:
                    self.statusText = f"Looking for Photos in {self.project.photoFolder}, {round(counter/numFiles*100,2)}% of paths searched"
                    self.after(0, lambda s=self.statusText: self.statusLabel.config(text=s))
                ext = file.lower().split(".")[-1]
                if ext in ["jpg", "jpeg"]:
                    img_paths.append(os.path.join(root, file))
        self.imgPaths = img_paths
        self.UpdatePicture()

    def SelectDirectory(self, askDialog = True):
        if askDialog or (self.project.photoFolder is None) or (not os.path.isdir(self.project.photoFolder)):
            self.project.photoFolder = filedialog.askdirectory()
        self.dirTreeView.LoadTreeFromDir(self.project.photoFolder)
        self.dirTreeView.tree.focus(list(self.dirTreeView.leaves.keys())[0])
        self.dirTreeView.OnSelectNode()
        myThead = threading.Thread(target=self.getPictures)
        myThead.start()

    def UpdateLabel(self):
        self.statusLabel.configure(text = self.statusText)        
        self.UpdateDirLabel()
        self.UpdateProjLabel()
        self.ValidateMappings()   

    def UpdateTreeLabel(self):
        self.treeStatusLabel.configure(text = f"Tree Status: {len(self.GetMappedComponents() or [])} of {len(self.project.data[self.project.hierarchyColumns[-1]])} Components Mapped")
    
    def UpdateProjLabel(self):
        projTree = self.projTree.tree
        node = projTree.selection()[0] if len(projTree.selection()) > 0 else None
        if node is None:
            self.projTreeLabel.configure(text = "Component Mapped to: No Selection")
            return
        else:
            componentCol = self.project.hierarchyColumns[-1] if self.project.hierarchyColumns is not None else None
            componentName = projTree.item(node, "text")
            if node not in self.projTree.GetLeafNodePaths().keys():
                self.projTreeLabel.configure(text = "Component Mapped to: Not a Component")
                return
            if componentCol is None:
                self.projTreeLabel.configure(text = "Component Mapped to: No Component Column Set")
                return
            data = self.project.data
            mappedFolder = str(list(data['Photo Folder'][data[componentCol] == componentName])[0]) 

            if mappedFolder is None:
                self.projTreeLabel.configure(text = f"Component not Mapped")
            elif os.path.isdir(mappedFolder):
                pathList = mappedFolder.replace("\\", "/").split("/")
                rootIndex = pathList.index(os.path.basename(self.project.photoFolder))
                self.projTreeLabel.configure(text = f"Component Mapped to: {"->".join(pathList[rootIndex:])}")
            else:
                self.projTreeLabel.configure(text = f"Component not Mapped")

    def UpdateDirLabel(self):
        dirTree = self.dirTreeView.tree
        data = self.project.data
        node = dirTree.selection()[0] if len(dirTree.selection()) > 0 else None
        componentCol = self.project.hierarchyColumns[-1] if self.project.hierarchyColumns is not None else None
        if componentCol is None:
            self.dirTreeLabel.configure(text = "Image Folder Mapped to: No Component Column Set")
            return
        if node is None:
            self.dirTreeLabel.configure(text = "Image Folder Mapped to: No Selection")
        else:
            path = dirTree.item(node, "values")[0]
            if os.path.isfile(path) and (path.split(".")[-1].lower() in ["jpg", "png", "jpeg"]):
                folder = os.path.dirname(path)
            elif os.path.isdir(path):
                folder = path
            else:
                self.dirTreeLabel.configure(text = "Image Folder Mapped to: Invalid Selection")
                return
            mappedComps = list(set(data.loc[data['Photo Folder'] == folder][componentCol]))
            if len(mappedComps) > 1:
                self.dirTreeLabel.configure(text = f"Warning, Image Folder mapped to: {', '.join(mappedComps)}")
            elif len(mappedComps) == 0:
                self.dirTreeLabel.configure(text = f"Image Folder not mapped")
            else:
                self.dirTreeLabel.configure(text = f"Image Folder mapped to: {mappedComps[0]}")

    def UpdatePicture(self, event : tk.Event = None):

        node = self.dirTreeView.tree.focus()        
        assert type(node) == str

        filepath = self.dirTreeView.tree.item(node, "values")[0]
        if os.path.isfile(filepath) and (filepath.split(".")[-1].lower() in ["jpg", "png", "jpeg"]):
            self.gui.loadImg(filepath)

    def TreeUpdate(self, event):
        self.statusText = f"Image: {' -> '.join(self.dirTreeView.GetPathToNode(self.dirTreeView.tree.focus(), asText=True))}"
        #print(f"Trees differ at {self.dirTreeView.TreeDiff(self.projTree)}")
        self.PopulateFields()
        self.UpdateLabel()
        self.UpdatePicture(event)

    def HangerNav(self, inc):
        self.dirTreeView.SelectNextParent(inc)

    def PhotoNav(self, inc):
        self.dirTreeView.SelectNext(inc)

    def MapFolderToComponent(self):
        dirNode = self.dirTreeView.tree.selection()[0] if len(self.dirTreeView.tree.selection()) > 0 else None
        if dirNode is None:
            print("No Image selected")
            return
 
        projNode = self.projTree.tree.selection()[0] if len(self.projTree.tree.selection()) > 0 else None
        if projNode is None:
            print("No Component selected")
            return
        
        data = self.project.data
        if data is None or data.empty:
            return

        path = self.dirTreeView.tree.item(dirNode, "values")[0]
        if os.path.isfile(path) and (path.split(".")[-1].lower() in ["jpg", "png", "jpeg"]):
            folder = os.path.dirname(path)
        elif os.path.isdir(path):
            folder = path
        else:
            print("Invalid Selection")
        
        componentName = self.projTree.tree.item(projNode, "text")        
        data.loc[data[self.project.hierarchyColumns[-1]] == componentName, "Photo Folder"] = folder
        self.project.data = data
        print(f"Mapped {path} to {componentName}")
        self.UpdateLabel()

    def UnMapComponent(self):
        projNode = self.projTree.tree.selection()[0] if len(self.projTree.tree.selection()) > 0 else None
        if projNode is None:
            print("No Component selected")
            return
        
        data = self.project.data
        if data is None or data.empty:
            print("No data in project")
            return
        
        componentName = self.projTree.tree.item(projNode, "text")  
        data.loc[data[self.project.hierarchyColumns[-1]] == componentName, "Photo Folder"] = None
        print(f"Unmapped {componentName}")
        self.UpdateLabel()
        
    def GetMappedComponents(self):        
        data = self.project.data
        if data is None or data.empty:
            return None

        mapped = []
        unmapped = []
        for i, component in enumerate(data[self.project.hierarchyColumns[-1]]):
            if os.path.isdir(data.iloc[i]['Photo Folder']):
                mapped.append(component)
            else:
                unmapped.append(component)
        return mapped, unmapped
    
    def ValidateMappings(self, debug = False):
        valid = True
        data = self.project.data
        if data is None or data.empty:
            return False

        compCol = self.project.hierarchyColumns[-1] if self.project.hierarchyColumns is not None else None
        unmappedComps = self.GetMappedComponents()[1]

        errors = ""

        if compCol is None or len(compCol) == 0:
            errors += "No component column set\n"
            if debug:
                print("No component columns set")
            valid = False

        if 'Photo Folder' not in data.columns:
            errors += "No Photo Folder column in data\n"
            if debug:
                print("No Photo Folder column in data")
            valid = False
        
        if len(data['Photo Folder'].unique()) < len(data[compCol]):
            errors += "Multiple components mapped to same folder\n"
            if debug:
                print("Warning, multiple components are mapped to the same folder")
            valid = False            
        
        if len(unmappedComps) > 0:
            unMappedString = ", ".join(unmappedComps)
            errors += f"The following components are not mapped to a valid folder: {unMappedString[0:min(100, len(unMappedString))]}\n"
            if debug:
                print(f"The following components are not mapped to a valid folder: {', '.join(unmappedComps)}")
            valid = False
        
        validationMessage = f"Valid Mapping: {valid}{("/n" + errors) if not valid else ''}"
        if debug:
            print(validationMessage)
        self.treeStatusLabel.configure(text = validationMessage)
        return valid

    def UpdateDataFromField(self, event : tk.Event = None):
        print(event)
        if self.project.data is None or self.project.data.empty:
            print("No data in project")
            return
        
        field = event.widget.lastChangedField
        assert type(field) == str
        data = self.project.data

        if field not in data.columns:
            print(f"Field {field} not in data columns")
            return

        currentComp = self.projTree.tree.selection()[0] if len(self.projTree.tree.selection()) > 0 else None        
        if currentComp is None:
            print("No Component selected")
            return
        componentName = self.projTree.tree.item(currentComp, "text")       
        
        compCol = self.project.hierarchyColumns[-1] if self.project.hierarchyColumns is not None else None
        if compCol is None:
            print("No component column set")
            return
        
        data.loc[data[compCol] == componentName, field] = self.fieldWidget.entries[field].get()
        print(f"Set {field} for {componentName} to {self.fieldWidget.entries[field].get()}")
    
    def PopulateFields(self):                           

        compCol = self.project.hierarchyColumns[-1] if self.project.hierarchyColumns is not None else None
        currentComp = self.projTree.tree.selection()[0] if len(self.projTree.tree.selection()) > 0 else None
        componentName = self.projTree.tree.item(currentComp, "text")     
        data = self.project.data

        for field, entry in self.fieldWidget.entries.items():
            entry.delete(0, tk.END)
            entry.insert(0, str(data[field][data[compCol] == componentName].value[0]))

def Main():
    root = tk.Tk()
    imgTab = ImageProcessTab(root)
    imgTab.pack()
    root.mainloop()

if __name__ == "__main__":
    Main()