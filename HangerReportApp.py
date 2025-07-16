import tkinter as tk
from tkinter import ttk
from tkinter import filedialog
import os
import threading
import pandas
import perspectiveCorrect

class MainWindow():
    def __init__(self):
        root = tk.Tk()
        root.title("Hanger Report Generator")
        root.iconbitmap("Are you working.ico")
        self.root = root
        #root.geometry('700x400')

        self.tabControl = ttk.Notebook(root)
        reportGen = ReportGenTab(self.tabControl)
        photoProcessTab = ImageProcessTab(self.tabControl)
        newJobTab = JobPrepareTab(self.tabControl)

        self.tabControl.add(reportGen, text = "Report Generation")
        self.tabControl.add(photoProcessTab, text = "Image Processing")
        self.tabControl.add(newJobTab, text = "Prepare for Job")
        
        self.tabControl.pack(expand=1, fill = "both")

        numHangersLabel = tk.Label(root, text = "N/A Hangers")
        numHangersLabel.pack()

        root.mainloop()

        self.hangerData = None
        self.photoFolder = None

class ReportGenTab(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.statusText = "empty"

        buttonColumn = EntityColumn(self)

        buttonColumn.AddButton("Open", text ="Open Project...", command = self.Open)
        buttonColumn.AddButton("Save", text ="Save Project", command = self.Save)
        buttonColumn.AddButton("Generate", text ="Generate Report", command = self.GenerateReport)

        buttonColumn.pack()

        self.treeView = ProjectTree(self, "MyProject")
        self.treeView.bind("<<TreeViewSelect>>", self.TreeUpdate)
        self.treeView.pack()

    def Open(self):
        pass

    def Save(self):
        pass
    
    def GenerateReport(self):
        pass

    def TreeUpdate(self):
        pass


class JobPrepareTab(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.statusText = "empty"

        self.hangerData = None

        processColumn = EntityColumn(self)
        processColumn.AddButton("Generate", text="Generate QR codes", command = self.GenerateQRs)
        processColumn.AddButton("Template", text ="Create .xlsx template", command = self.CreateTemp)

        processColumn.pack()

    def GenerateQRs(self):
        pass

    def CreateTemp(self):
        pass

class ImageProcessTab(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.rootFolderPath = None
        self.imgPaths = None
        self.statusText = "empty"

        self.hangerButtons = PrevNextButtonUI(self, labelText = "Hangers")
        self.hangerButtons.pack(expand = True)

        self.photoButtons = PrevNextButtonUI(self, labelText = "Photos")
        self.photoButtons.pack(expand = True)

        self.gui = perspectiveCorrect.ImageEditor(self)
        self.gui.pack(side = "left", expand=1)

        self.hangerButtons.bind("<<Left>>", lambda e: self.HangerNav(-1))
        self.hangerButtons.bind("<<Right>>", lambda e: self.HangerNav(1))
        self.photoButtons.bind("<<Left>>", lambda e: self.PhotoNav(-1))
        self.photoButtons.bind("<<Right>>", lambda e: self.PhotoNav(1))

        self.treeView = DirectoryTree(self)
        self.treeView.bind("<<TreeViewSelect>>", self.TreeUpdate)
        self.treeView.pack()

        processColumn = EntityColumn(self)
        processColumn.AddButton("Select Folder", text="Select Root Folder", command = self.SelectDirectory)
        processColumn.AddField("Cold Reading", text="Cold Reading")
        processColumn.AddField("Hot Reading", text="Hot Reading")
        processColumn.AddField("Cold Indicator", text="Cold Indicator")
        processColumn.AddField("Hot Indicator",text="Hot Indicator")
        processColumn.AddCheckBox(self, "Perspective", text = "Perspective Correction", variable=self.gui.perspectiveOverlay, command = self.gui.UpdateScreen)
        processColumn.pack()

        statusLabel = tk.Label(self, text = self.statusText)
        statusLabel.pack(side = 'bottom')

        self.statusLabel = statusLabel

    def getPictures(self):
        img_paths = []
        rootWalk = os.walk(self.rootFolderPath)
        rootWalk = [walk for walk in rootWalk]
        numFiles = sum([len(files[2]) for files in rootWalk])
        counter = 0
        for root, dirs, files in rootWalk:
            for file in files:
                counter += 1
                if counter%int(numFiles/100) == 0:
                    self.statusText = f"Looking for Photos in {self.rootFolderPath}, {round(counter/numFiles*100,2)}% of paths searched"
                    self.UpdateLabel()
                ext = file.lower().split(".")[-1]
                if ext in ["jpg", "jpeg"]:
                    img_paths.append(os.path.join(root, file))
        self.imgPaths = img_paths
        self.UpdatePicture()

    def SelectDirectory(self):
        self.rootFolderPath = filedialog.askdirectory()
        self.treeView.SelectFolder(self.rootFolderPath)
        myThead = threading.Thread(target=self.getPictures)
        myThead.start()

    def UpdateLabel(self):
        self.statusLabel.configure(text = self.statusText)

    def UpdatePicture(self):
        if(os.path.isfile(self.treeView.selectionPath)) and self.treeView.selectionPath.split(".")[-1].lower() in ["jpg", "png", "jpeg"]:
            self.gui.loadImg(self.treeView.selectionPath)

    def Update(self, event):
        self.UpdateLabel()
        self.UpdatePicture()

    def TreeUpdate(self, event):
        self.statusText = f"Image: {self.treeView.selectionPath}"
        self.Update(event)

    def HangerNav(self, inc):
        if self.treeView.item is not None:
            self.treeView.SelectNextParent(inc)

    def PhotoNav(self, inc):
        if self.treeView.item is not None:
            self.treeView.SelectNext(inc)

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

class EntityColumn(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.entities = {}
        
        
    def AddButton(self, name, **kwargs):
        button = tk.Button(self, **kwargs)
        self.entities[name] = button
        button.pack()

    def AddField(self, name, text = "Unnamed"):
        frame = ttk.Frame(self)
        entryBox = tk.Entry(frame)
        label = tk.Label(frame, text = text)
        entryBox.pack(side = "left")
        label.pack(side = "left")
        self.entities[name] = entryBox
        frame.pack(side = "top", anchor="nw", expand = True)

    def AddCheckBox(self, parent, name, **kwargs):
        checkBox = tk.Checkbutton(parent, **kwargs)
        self.entities[name] = checkBox
        checkBox.pack()

class ProjectTree(tk.Frame):
    def __init__(self, parent, projName):
        super().__init__(parent)
        self.projName = projName

        self.nodes = dict()
        self.tree = ttk.Treeview(self)
        ysb = ttk.Scrollbar(self, orient='vertical', command=self.tree.yview)
        xsb = ttk.Scrollbar(self, orient='horizontal', command=self.tree.xview)
        self.tree.configure(yscroll=ysb.set, xscroll=xsb.set)
        self.tree.heading('#0', text='Project tree', anchor='w')

        self.tree.grid()
        ysb.grid(row=0, column=1, sticky='ns')
        xsb.grid(row=1, column=0, sticky='ew')

        self.tree.bind('<<TreeviewSelect>>', self.SelectNode)

        self.treeContols = EntityColumn(self)
        self.treeContols.AddField("Amount", text = "No. nodes to add")
        self.treeContols.AddButton("Add", text = "Add", command = self.AddNodes)

        self.treeContols.grid(row = 2, column = 0)

    def AddNodes(self):
        for i in range(int(self.treeContols.entities["Amount"].get())):
            self.AddNode()

    def AddNode(self, name = "New Node"):
        currentNode = self.tree.focus()
        currentSiblings = list(self.tree.get_children(self.tree.parent(currentNode)))        
        counter = 0
        newName = name
        while newName in [self.tree.item(i)["text"] for i in currentSiblings]:
            counter += 1
            newName = name + f"({counter})"
        self.tree.insert(currentNode, 'end', text = newName)

    def SelectNode(self, event):
        pass

    

class DirectoryTree(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.nodes = dict()
        self.tree = ttk.Treeview(self)
        ysb = ttk.Scrollbar(self, orient='vertical', command=self.tree.yview)
        xsb = ttk.Scrollbar(self, orient='horizontal', command=self.tree.xview)
        self.tree.configure(yscroll=ysb.set, xscroll=xsb.set)
        self.tree.heading('#0', text='Project tree', anchor='w')

        self.currentSiblings = []
        self.currentSibling = 0

        self.item = None
        self.selectionPath = ""

        self.tree.grid()
        ysb.grid(row=0, column=1, sticky='ns')
        xsb.grid(row=1, column=0, sticky='ew')

        self.tree.bind('<<TreeviewOpen>>', self.open_node)
        self.tree.bind('<<TreeviewSelect>>', self.SelectNode)

        
    def SelectFolder(self, path):  
        for i in self.tree.get_children():
            self.tree.delete(i)
        abspath = os.path.abspath(path)
        self.insert_node('', abspath, abspath)

    def SelectNode(self, event):
        self.focus = self.tree.focus()
        self.item = self.tree.item(self.focus)
        self.currentSiblings = list(self.tree.get_children(self.tree.parent(self.focus)))
        self.currentSibling = self.currentSiblings.index(self.focus)   

        path = [self.item["text"]]
        focus = self.focus
        for i in range(50):
            parent = self.tree.parent(focus)
            text = self.tree.item(parent)["text"]
            if text != "":
                path.append(text)
            else:
                break
            focus = parent
        else:
            print("Warning, tree depth exceeded")
        path = "\\".join(list(reversed(path)))
        self.selectionPath = path
        if(os.path.isfile(path)):
            self.event_generate("<<TreeViewSelect>>")

    def insert_node(self, parent, text, abspath):
        node = self.tree.insert(parent, 'end', text=text, open=False)
        if os.path.isdir(abspath):
            self.nodes[node] = abspath
            self.tree.insert(node, 'end')

    def open_node(self, event):
        node = self.tree.focus()
        abspath = self.nodes.pop(node, None)
        if abspath:
            self.tree.delete(self.tree.get_children(node))
            for p in os.listdir(abspath):
                self.insert_node(node, p, os.path.join(abspath, p))

    def SelectNext(self, inc):
        self.currentSibling += inc
        for i in range(50):
            if(self.tree.item(self.currentSiblings[self.currentSibling%len(self.currentSiblings)])["text"].split(".")[-1].lower() not in ["jpg", "png", "jpeg"]):
                self.currentSibling += inc
            else:
                break
        self.tree.focus(self.currentSiblings[self.currentSibling%len(self.currentSiblings)])
        self.SelectNode(inc)
    
    
#Need to account for parents being both images and folders

    def SelectNextParent(self, inc):
        self.currentSibling = 0
        currentParents = list(self.tree.get_children(self.tree.parent(self.tree.parent(self.focus))))
        currentParent = currentParents.index(self.tree.parent(self.focus))+inc
        print(currentParent)
        print(currentParents)

        for i in range(1000):
            if not(os.path.isdir(f"{self.tree.item(currentParents[currentParent])["text"]}")):
                currentParent+=inc
            else:
                break

        self.tree.focus(self.tree.get_children(currentParents[(currentParent+inc)%len(currentParents)])[0])
        print(self.tree.item(self.tree.get_children(currentParents[(currentParent+inc)%len(currentParents)])[0]))
        self.SelectNode(inc)
    
class Project():
    def __init__(self, name):
        self.name = name
        self.savePath = None
        self.projTree = None
        self.fields = None
        self.QAcodes = None
        self.componentIDs = []
        self.nextID = 0

    def AddComponent(self):
        self.componentIDs.append(self.nextID)
        self.nextID += 1


def Main():
    myWindow = MainWindow()

if __name__ == '__main__':
    Main()