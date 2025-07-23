import tkinter as tk
from tkinter import ttk
import EntityColumn
import os

class ProjectTree(tk.Frame):
    def __init__(self, parent, projName):
        super().__init__(parent)
        self.projName = projName

        self.nodes = []
        self.tree = ttk.Treeview(self)
        ysb = ttk.Scrollbar(self, orient='vertical', command=self.tree.yview)
        xsb = ttk.Scrollbar(self, orient='horizontal', command=self.tree.xview)
        self.tree.configure(yscroll=ysb.set, xscroll=xsb.set)
        self.tree.heading('#0', text='Project tree', anchor='w')
        self.tree.column("#0", stretch=False)

        self.editBox = None

        self.tree.grid()
        ysb.grid(row=0, column=1, sticky='ns')
        xsb.grid(row=1, column=0, sticky='ew')

        self.tree.bind('<<TreeviewSelect>>', self.SelectNode)        
        self.tree.bind("<Double-1>", self.EditNode)
        self.tree.bind("<F2>", self.EditNode)

        self.treeContols = EntityColumn.EntityColumn(self)
        self.treeContols.AddField("Amount", text = "No. nodes to add")
        self.treeContols.AddButton("Add", text = "Add", command = self.AddNodes)
        self.treeContols.AddButton("Delete", text = "Delete", command = self.DeleteNode)

        self.treeContols.entities["Amount"].bind("<Return>", lambda e : self.AddNodes())

        self.treeContols.grid(row = 2, column = 0)

    def LoadFromDir(self, dirTree):
        for node in self.tree.get_children():
            self.tree.delete(node)

        

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

class DirectoryTree(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.nodes = dict()
        self.tree = ttk.Treeview(self)
        self.leaves = []
        ysb = ttk.Scrollbar(self, orient='vertical', command=self.tree.yview)
        xsb = ttk.Scrollbar(self, orient='horizontal', command=self.tree.xview)
        self.tree.configure(yscrollcommand=ysb.set, xscrollcommand=xsb.set)
        self.tree.heading('#0', text='Project tree', anchor='w')
        self.tree.column("#0", stretch=False)

        self.currentSiblings = []
        self.currentSibling = 0
        self.currentLeaf = ''

        self.item = None
        self.selectionPath = ""

        self.tree.grid()
        ysb.grid(row=0, column=1, sticky='ns')
        xsb.grid(row=1, column=0, sticky='ew')

        self.tree.bind('<<TreeviewSelect>>', self.SelectNode)



    def LoadTree(self, rootPath, node = ''):
        self.tree.column("#0", width=1800, stretch=False)
        for item in os.listdir(rootPath):
            newNode = self.tree.insert(node, 'end', text = item, values=[rootPath + "\\" + item])
            if os.path.isdir(rootPath + "\\" + item):
                self.LoadTree(rootPath + "\\" + item, node = newNode)
            else:
                self.leaves.append(newNode)


    def SelectNode(self, event):
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
    