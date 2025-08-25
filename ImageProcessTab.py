import tkinter as tk
from tkinter import ttk, filedialog
import threading
import EntityColumn
import PrevNextUI
import perspectiveCorrect
import Treeviews
import os
import Project

class ImageProcessTab(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.parent = parent
        self.controller = controller

        project = controller.project
        assert type(project) == Project.Project
        self.project = project

        projTree = controller.reportGen.treeView
        assert type(projTree) == Treeviews.ProjectTree
        self.projTree = projTree

        self.imgPaths = None
        self.statusText = "empty"

        self.hangerButtons = PrevNextUI.PrevNextButtonUI(self, labelText = "Hangers")
        self.hangerButtons.pack(expand = True)

        self.photoButtons = PrevNextUI.PrevNextButtonUI(self, labelText = "Photos")
        self.photoButtons.pack(expand = True)

        self.gui = perspectiveCorrect.ImageEditor(self)
        self.gui.pack(side = "left", expand=1)

        self.hangerButtons.bind("<<Left>>", lambda e: self.HangerNav(-1))
        self.hangerButtons.bind("<<Right>>", lambda e: self.HangerNav(1))
        self.photoButtons.bind("<<Left>>", lambda e: self.PhotoNav(-1))
        self.photoButtons.bind("<<Right>>", lambda e: self.PhotoNav(1))

        self.treeView = Treeviews.DirectoryTree(self)
        self.treeView.bind("<<NodeSelect>>", self.TreeUpdate)
        self.treeView.pack(expand=False)

        self.unionTree = self.treeView.TreeUnion(self.projTree)

        processColumn = EntityColumn.EntityColumn(self)
        processColumn.AddButton("Select Folder", text="Select Root Folder", command = self.SelectDirectory)
        processColumn.AddField("Cold Reading", text="Cold Reading")
        processColumn.AddField("Hot Reading", text="Hot Reading")
        processColumn.AddField("Cold Indicator", text="Cold Indicator")
        processColumn.AddField("Hot Indicator",text="Hot Indicator")
        processColumn.AddCheckBox(self, "Perspective", text = "Perspective Correction", variable=self.gui.perspectiveOverlay, command = self.gui.UpdateScreen)
        processColumn.pack()

        statusLabel = tk.Label(self, text = self.statusText, wraplength = 100, justify = "center")
        statusLabel.pack(side = 'bottom')

        self.statusLabel = statusLabel

        self.SelectDirectory(askDialog=False)

    def getPictures(self):
        img_paths = []
        rootWalk = os.walk(self.project.photoFolder)
        rootWalk = [walk for walk in rootWalk]
        numFiles = sum([len(files[2]) for files in rootWalk])
        counter = 0
        for root, dirs, files in rootWalk:
            for file in files:
                counter += 1
                if counter%int(numFiles/100) == 0:
                    self.statusText = f"Looking for Photos in {self.project.photoFolder}, {round(counter/numFiles*100,2)}% of paths searched"
                    self.after(0, lambda s=self.statusText: self.statusLabel.config(text=s))
                ext = file.lower().split(".")[-1]
                if ext in ["jpg", "jpeg"]:
                    img_paths.append(os.path.join(root, file))
        self.imgPaths = img_paths
        self.UpdatePicture()

    def SelectDirectory(self, askDialog = True):
        if askDialog or (self.project.photoFolder is None):
            self.project.photoFolder = filedialog.askdirectory()
        self.treeView.LoadTree(self.project.photoFolder)
        self.treeView.tree.focus(list(self.treeView.leaves.keys())[0])
        self.treeView.OnSelectNode()
        myThead = threading.Thread(target=self.getPictures)
        myThead.start()

    def UpdateLabel(self):
        self.statusLabel.configure(text = self.statusText)

    def UpdatePicture(self, event : tk.Event = None):

        node = self.treeView.tree.focus()        
        assert type(node) == str

        filepath = self.treeView.tree.item(node, "values")[0]
        if os.path.isfile(filepath) and (filepath.split(".")[-1].lower() in ["jpg", "png", "jpeg"]):
            self.gui.loadImg(filepath)

    def TreeUpdate(self, event):
        self.statusText = f"Image: {' -> '.join(self.treeView.GetPathToNode(self.treeView.tree.focus(), asText=True))}"
        print(f"Trees differ at {self.treeView.TreeDiff(self.projTree)}")
        self.UpdateLabel()
        self.UpdatePicture(event)

    def HangerNav(self, inc):
        self.treeView.SelectNextParent(inc)

    def PhotoNav(self, inc):
        self.treeView.SelectNext(inc)

def Main():
    root = tk.Tk()
    imgTab = ImageProcessTab(root)
    imgTab.pack()
    root.mainloop()

if __name__ == "__main__":
    Main()