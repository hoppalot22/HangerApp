import tkinter as tk
from tkinter import ttk, font as tkFont
import EntityColumn
import os
import Project

class BaseTree(tk.Frame):
    def __init__(self, parent, headingText="Tree", width = 300, height = 400):
        super().__init__(parent)
        self.grid_propagate(False)
        self.width = width
        self.height = height
        self.config(width=width, height=height)
        self.tree = ttk.Treeview(self, columns=("dummy",))

        self.tree.column("dummy", width=0, stretch=False)
        self.tree.heading("dummy", text="")
        self.tree.heading('#0', text=headingText, anchor='w')
        self.tree.column("#0", stretch=False, minwidth=800)

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

        style = ttk.Style()
        font_name = style.lookup("Treeview", "font")
        if not font_name:  # fallback
            font_name = "TkDefaultFont"
        self._font = tkFont.nametofont(font_name)

    def autosizeColumn(self, col="#0"):
        """Resize column to fit the longest text in the whole tree (all depths)."""
        max_width = 0

        def measure_node(node, depth=0):
            nonlocal max_width
            text = self.tree.item(node, "text")
            width = int(self._font.measure(text)*1.05 + depth * 20)  # indent adds width
            max_width = max(max_width, width)

            for child in self.tree.get_children(node):
                measure_node(child, depth + 1)

        # Start with all top-level nodes
        for root in self.tree.get_children(""):
            measure_node(root, depth=0)

        # Apply column width
        self.tree.column(col, width=max_width + 10)
    
    def OnSelectNode(self, event=None):
        self.event_generate("<<NodeSelect>>")

    def GetPathToNode(self, node = None, asText = True):
        """Returns list of labels from root to the focused node."""
        if node is None:
            node = self.tree.focus()
        
        if asText:
            path = [self.tree.item(node, "text")]
        else:
            path = [node]

        parent = self.tree.parent(node)
        while parent:
            if asText:
                path.append(self.tree.item(parent, "text"))
            else:
                path.append(parent)
            parent = self.tree.parent(parent)
        return list(reversed(path))
    
    def GetAllNodes(self):
        allNodes = []
        def recurse(node):
            allNodes.append(node)
            for child in self.tree.get_children(node):
                recurse(child)

        for root in self.tree.get_children():
            recurse(root)
        
        return allNodes

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

    def GetShape(self, node = ''):
        shape = {}
        children = self.tree.get_children(node)
        for i, child in enumerate(children):
            shape[i] = self.GetShape(child)
        return shape
        
    def TreeUnion(self, otherTree):
        assert isinstance(otherTree, BaseTree)

        shape1 = self.GetShape()
        shape2 = otherTree.GetShape()

        def union_dict(d1, d2):
            all_keys = set(d1.keys()) | set(d2.keys())
            result = {}
            for k in all_keys:
                result[k] = union_dict(d1.get(k, {}), d2.get(k, {}))
            return result

        return union_dict(shape1, shape2)

    def TreeDiff(self, otherTree):
        assert isinstance(otherTree, BaseTree)

        base = self.TreeUnion(otherTree)     # dict representing union
        sub = self.GetShape()                # dict representing this tree’s shape

        def diff_dict(base_dict, sub_dict):
            missing = {}
            for k, v in base_dict.items():
                if k not in sub_dict:
                    missing[k] = v
                else:
                    diff = diff_dict(v, sub_dict[k])
                    if diff:
                        missing[k] = diff
            return missing

        return diff_dict(base, sub)

    def Clear(self):
        """Remove all nodes from the tree."""
        for node in self.tree.get_children():
            self.tree.delete(node)
        self.tree.column("#0", width=100)

    def InsertNode(self, parent='', text='', values=None):
        """Insert a single node into the tree."""
        item = self.tree.insert(parent, 'end', text=text, values=values or [])
        return item

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
        self.editBox.bind("<FocusOut>", lambda e, node = node : self.finishEdit(event = e, node = node))

    def finishEdit(self, event : tk.Event = None, node = None):
        box = event.widget
        assert type(box) == tk.Entry
        newText = box.get()
        self.tree.item(node, text=newText)
        self.cancelEdit(event)

    def cancelEdit(self, event):
        box = event.widget
        assert type(box) == tk.Entry
        box.destroy()

    def LoadTreeFromProj(self, project : Project.Project):
        
        self.Clear()
        hierarchyColumns = project.hierarchyColumns
        if not hierarchyColumns:
            print("No hierarchy columns defined in project")
            return

        data = project.data.to_dict(orient="records")

        def InsertRecursive(parent, rows : list[dict], depth):
            if depth >= len(hierarchyColumns):
                return

            col = hierarchyColumns[depth]
            seen = {}
            for row in rows:
                key = row[col]
                assert type(key) == str
                seen.setdefault(key, []).append(row)

            for key in sorted(seen.keys(), key=str):
                children = seen[key]
                nodeId = self.tree.insert(parent, "end", text=key)
                InsertRecursive(nodeId, children, depth + 1)

        InsertRecursive("", data, 0)

        self.leaves = self.GetLeafNodePaths()
        self.autosizeColumn()

    def copy(self, master):
        newTree = BaseTree(master, headingText=self.tree.heading('#0')['text'], width=self.width, height=self.height)
        
        def recurse_copy(node, parent=''):
            text = self.tree.item(node, 'text')
            values = self.tree.item(node, 'values')
            new_node = newTree.tree.insert(parent, 'end', text=text, values=values)
            for child in self.tree.get_children(node):
                recurse_copy(child, new_node)

        for root in self.tree.get_children(''):
            recurse_copy(root)

        newTree.leaves = newTree.GetLeafNodePaths()
        newTree.autosizeColumn()
        return newTree

class ProjectTree(BaseTree):
    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)

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
    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)
        self.photoDir = None

    def OnSelectNode(self, event = None):
        
        self.event_generate("<<NodeSelect>>")

    def LoadTreeFromDir(self, rootPath):
        self.Clear()
        self.photoDir = rootPath
        if rootPath is None:
            return
        self.tree.column("#0", stretch=False)

        def recurse(rootPath, node = ''):
            for item in os.listdir(rootPath):
                newNode = self.tree.insert(node, 'end', text = item, values=[rootPath + "\\" + item])
                if os.path.isdir(rootPath + "\\" + item):
                    recurse(rootPath + "\\" + item, node = newNode)
        
        recurse(rootPath)
        self.leaves = self.GetLeafNodePaths()
        self.autosizeColumn()

    def SelectNext(self, inc):
        focus = self.tree.focus()  
        currentSiblings = list(self.tree.get_children(self.tree.parent(focus)))
        currentSibling = currentSiblings.index(focus)   
        currentSibling += inc

        for i in range(len(currentSiblings)):
            if(self.tree.item(currentSiblings[currentSibling%len(currentSiblings)])["values"][0].split(".")[-1].lower() not in ["jpg", "png", "jpeg"]):
                currentSibling += inc
            else:
                break
        self.tree.focus(currentSiblings[currentSibling%len(currentSiblings)])
        self.OnSelectNode()

    def SelectNextParent(self, inc):
        
        node = self.tree.focus()
        leaves = list(self.GetLeafNodePaths().keys())
        allNodes = self.GetAllNodes()

        leafIndex = allNodes.index(node)

        while (self.tree.parent(allNodes[leafIndex]) == self.tree.parent(allNodes[(leafIndex+inc)%len(allNodes)]) or (allNodes[(leafIndex+inc)%len(allNodes)] not in leaves)):
            inc+=int(inc/abs(inc))
        newParent = self.tree.parent(allNodes[(leafIndex+inc)%len(allNodes)])
        newLeaf = list(self.tree.get_children(newParent))[0]
        print(leafIndex + inc, newParent, newLeaf, self.tree.item(newLeaf, "text"))
        self.tree.focus(newLeaf)
        self.OnSelectNode()
    