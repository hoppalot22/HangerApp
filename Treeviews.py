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

        self.focusItem = None
        self.selectionPath = ""
        self.editBox = None
        self.editItem = None

        self.tree.bind('<<TreeviewSelect>>', self.onSelectNode)
        self.tree.bind('<Double-1>', self.beginEdit)
        self.tree.bind('<F2>', self.beginEdit)

    def onSelectNode(self, event=None):
        pass

    def getPathToFocus(self):
        """Returns list of labels from root to the focused node."""
        if not self.focusItem:
            return []
        path = [self.tree.item(self.focusItem, "text")]
        parent = self.tree.parent(self.focusItem)
        while parent:
            path.append(self.tree.item(parent, "text"))
            parent = self.tree.parent(parent)
        return list(reversed(path))

    def clear(self):
        """Remove all nodes from the tree."""
        for node in self.tree.get_children():
            self.tree.delete(node)

    def insertNode(self, parent='', text='', values=None):
        """Insert a single node into the tree."""
        return self.tree.insert(parent, 'end', text=text, values=values or [])

    def deleteNode(self, item=None):
        """Delete the specified node or currently focused one."""
        if not item:
            item = self.tree.focus()
        if item:
            self.tree.delete(item)

    def setHeadingText(self, text):
        self.tree.heading('#0', text=text, anchor='w')


    def beginEdit(self, event=None):
        item = self.tree.identify_row(event.y) if event else self.tree.focus()
        if not item:
            return

        self.editItem = item
        bbox = self.tree.bbox(item)
        if not bbox:
            return  # Avoid crash if item is collapsed

        text = self.tree.item(item, "text")
        self.editBox = tk.Entry(self, width=bbox[2])
        self.editBox.insert(0, text)
        self.editBox.place(x=bbox[0], y=bbox[1])
        self.editBox.focus()
        self.editBox.selection_range(0, tk.END)

        self.editBox.bind("<Return>", self.finishEdit)
        self.editBox.bind("<Escape>", self.cancelEdit)
        self.editBox.bind("<FocusOut>", self.finishEdit)

    def finishEdit(self, event=None):
        if self.editItem and self.editBox:
            newText = self.editBox.get()
            self.tree.item(self.editItem, text=newText)
            self.cancelEdit()

    def cancelEdit(self, event=None):
        if self.editBox:
            self.editBox.destroy()
            self.editBox = None
            self.editItem = None

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
        newNode = self.tree.insert(currentNode, 'end', text = newName)
        self.nodes.append(newNode)

    def DeleteNode(self):
        self.tree.delete(self.tree.focus())

    def EditNode(self, event):
        for node in self.nodes:
            if ((self.tree.bbox(node)[0] < event.x) and (self.tree.bbox(node)[0] + self.tree.bbox(node)[2] > event.x) and (self.tree.bbox(node)[1] < event.y) and (self.tree.bbox(node)[1] + self.tree.bbox(node)[3] > event.y)):
                text = tk.StringVar(value = self.tree.item(node, "text"))
                self.editNode = node
                self.editBox = tk.Entry(self, textvariable = text, width = self.tree.bbox(node)[2])
                self.editBox.place(x = self.tree.bbox(node)[0], y = self.tree.bbox(node)[1])

                self.editBox.bind("<FocusOut>", self.FinishEdit)
                self.editBox.bind("<Return>", self.FinishEdit)
                self.editBox.bind("<Escape>", self.FinishEdit)
                self.editBox.bind("<FocusIn>", self.Highlight)

                self.editBox.focus()

    def Highlight(self, event):
        self.editBox.selection_range(0, tk.END)

    def FinishEdit(self, event : tk.Event):     
        if not (event.keysym == "Escape"):
            self.tree.item(self.editNode, text = self.editBox.get())
        self.editBox.destroy()

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
            else:
                self.leaves.append(newNode)


    def onSelectNode(self, event):
        self.focus = self.tree.focus()
        self.item = self.tree.item(self.focus)
        self.currentSiblings = list(self.tree.get_children(self.tree.parent(self.focus)))
        self.currentSibling = self.currentSiblings.index(self.focus)
        

        if(self.focus in self.leaves):
            self.currentLeaf = self.focus
            self.selectionPath = self.item["values"][0]

            if(os.path.isfile(self.selectionPath)):
                self.event_generate("<<NodeSelect>>")

    def SelectNext(self, inc):
        self.currentSibling += inc
        for i in range(len(self.currentSiblings)):
            if(self.tree.item(self.currentSiblings[self.currentSibling%len(self.currentSiblings)])["values"][0].split(".")[-1].lower() not in ["jpg", "png", "jpeg"]):
                self.currentSibling += inc
            else:
                break
        self.tree.focus(self.currentSiblings[self.currentSibling%len(self.currentSiblings)])
        self.SelectNode("pass")

    def SelectNextParent(self, inc):

        if self.currentLeaf in self.leaves:
            currentLeaf = self.leaves.index(self.currentLeaf)
        else:
            currentLeaf = 0

        while self.tree.parent(self.leaves[currentLeaf]) == self.tree.parent(self.leaves[(currentLeaf+inc)%len(self.leaves)]):
            inc+=inc
        newLeaf = (currentLeaf+inc)%len(self.leaves)
        self.tree.focus(self.leaves[newLeaf])     
        self.SelectNode("pass")

    def PathToFocus(self):
        path = [self.tree.item(self.focus, "text")]
        parent = self.tree.parent(self.focus)
        while not parent == '':
            path.append(self.tree.item(parent, "text"))
            parent = self.tree.parent(parent)
        path.reverse()
        return path
    