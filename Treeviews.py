import tkinter as tk
from tkinter import ttk
import EntityColumn
import os

class BaseTree(tk.Frame):
    def __init__(self, parent, headingText="Tree"):
        super().__init__(parent)
        self.tree = ttk.Treeview(self)
        self.tree.heading('#0', text=headingText, anchor='w')
        self.tree.column("#0", stretch=False)

        self.leaves = {}

        self.ysb = ttk.Scrollbar(self, orient='vertical', command=self.tree.yview)
        self.xsb = ttk.Scrollbar(self, orient='horizontal', command=self.tree.xview)
        self.tree.configure(yscrollcommand=self.ysb.set, xscrollcommand=self.xsb.set)

        self.tree.grid(row=0, column=0, sticky='nsew')
        self.ysb.grid(row=0, column=1, sticky='ns')
        self.xsb.grid(row=1, column=0, sticky='ew')

        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        self.editBox = None

        self.tree.bind('<<TreeviewSelect>>', self.OnSelectNode)
        self.tree.bind('<Double-1>', self.BeginEdit)
        self.tree.bind('<F2>', self.BeginEdit)

    def OnSelectNode(self, event=None):
        pass

    def GetPathToNode(self, node = None):
        """Returns list of labels from root to the focused node."""
        if node is None:
            node = self.tree.focus()
        path = [node]
        parent = self.tree.parent(node)
        while parent:
            path.append(self.tree.item(parent, "text"))
            parent = self.tree.parent(parent)
        return list(reversed(path))
    
    def GetLeafNodePaths(self):
        leafPaths = {}
        def recurse(node, pathSoFar : list):

            pathSoFar.append(node)
            children = self.tree.get_children(node)            

            if not children:
                leafPaths[node] = pathSoFar
            else:
                for child in children:
                    recurse(child, pathSoFar)

        for root in self.tree.get_children():
            recurse(root, [])
        
        return leafPaths        


    def Clear(self):
        """Remove all nodes from the tree."""
        for node in self.tree.get_children():
            self.tree.delete(node)

    def InsertNode(self, parent='', text='', values=None):
        """Insert a single node into the tree."""
        return self.tree.insert(parent, 'end', text=text, values=values or [])

    def DeleteNode(self, node = None):
        """Delete the specified node or currently focused one."""
        if node is not None:
            node = self.tree.focus()
        
        self.tree.delete(node)

    def SetHeadingText(self, text):
        self.tree.heading('#0', text=text, anchor='w')


    def BeginEdit(self, event=None):
        node = self.tree.identify_row(event.y) if event else self.tree.focus()
        if not node:
            return
        
        bbox = self.tree.bbox(node)
        if not bbox:
            return  # Avoid crash if item is collapsed

        text = self.tree.item(node, "text")
        self.editBox = tk.Entry(self, width=bbox[2])
        self.editBox.insert(0, text)
        self.editBox.place(x=bbox[0], y=bbox[1])
        self.editBox.focus()
        self.editBox.selection_range(0, tk.END)

        self.editBox.bind("<Return>", lambda e, node = node : self.finishEdit(event = e, node = node))
        self.editBox.bind("<Escape>", self.cancelEdit)
        self.editBox.bind("<FocusOut>", self.finishEdit)

    def finishEdit(self, event : tk.Event = None, node = None):
        box = event.widget
        assert type(box) == tk.Entry
        newText = box.get()
        self.tree.item(self.editItem, text=newText)
        self.cancelEdit()

    def cancelEdit(self, event : tk.Event = None):
        if box is not None:
            box = event.widget
        assert type(box) == tk.Entry
        box.destroy()

class ProjectTree(BaseTree):
    def __init__(self, parent, projName):
        super().__init__(parent)
        self.projName = projName

        self.treeContols = EntityColumn.EntityColumn(self)
        self.treeContols.AddField("Amount", text = "No. nodes to add")
        self.treeContols.AddButton("Add", text = "Add", command = self.AddNodes)
        self.treeContols.AddButton("Delete", text = "Delete", command = self.DeleteNode)
        self.treeContols.entities["Amount"].bind("<Return>", lambda e : self.AddNodes())

        self.treeContols.grid(row = 2, column = 0)       

    def AddNodes(self):
        for i in range(int(self.treeContols.entities["Amount"].get())):
            self.AddNode()

    def AddNode(self, name = "New Node"):
        currentNode = self.tree.focus()      
        counter = 0
        newName = name
        while newName in [self.tree.item(i)["text"] for i in self.tree.get_children(currentNode)]:
            counter += 1
            newName = name + f"({counter})"
        self.tree.insert(currentNode, 'end', text = newName)

    def DeleteNode(self):
        self.tree.delete(self.tree.focus())

    def SelectNode(self, event):
        pass

class DirectoryTree(BaseTree):
    def __init__(self, parent):
        super().__init__(parent)

    def LoadTree(self, rootPath, node = ''):
        self.tree.column("#0", width=1800, stretch=False)
        for item in os.listdir(rootPath):
            newNode = self.tree.insert(node, 'end', text = item, values=[rootPath + "\\" + item])
            if os.path.isdir(rootPath + "\\" + item):
                self.LoadTree(rootPath + "\\" + item, node = newNode)

        if node == '':
            self.leaves = self.GetLeafNodePaths()

    def OnSelectNode(self, event = None):
        focus = self.tree.focus()     

        if(focus in self.leaves.keys()):
            selectionPath = self.tree.item(focus, "values")[0]
            if(os.path.isfile(selectionPath)):
                self.event_generate("<<NodeSelect>>")

    def SelectNext(self, inc):
        focus = self.tree.focus()  
        currentSiblings = list(self.tree.get_children(self.tree.parent(focus)))
        currentSibling = currentSiblings.index(focus)   
        currentSibling += inc

        for i in range(len(currentSiblings)):
            if(self.tree.item(currentSiblings[currentSibling%len(currentSiblings)])["values"][0].split(".")[-1].lower() not in ["jpg", "png", "jpeg"]):
                self.currentSibling += inc
            else:
                break
        self.tree.focus(currentSiblings[self.currentSibling%len(currentSiblings)])
        self.OnSelectNode()

    def SelectNextParent(self, inc):
        
        node = self.tree.focus()
        leaves = list(self.GetLeafNodePaths().keys())
        leafIndex = leaves.index(node)

        while self.tree.parent(leaves[node]) == self.tree.parent(leaves[(leafIndex+inc)%len(leaves)]):
            inc+=inc
        newLeafIndex = (leafIndex+inc)%len(leaves)
        self.tree.focus(self.leaves[newLeafIndex])     
        self.OnSelectNode()
    