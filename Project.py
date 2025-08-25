import os
import pandas as pd

class Project():
    def __init__(self, name):
        self.name = name
        self.savePath = os.path.join(os.path.dirname(__file__), self.name)
        self.hierarchyColumns = None
        self.projTree = None
        self.fields = None
        self.data = pd.DataFrame()
        self.fieldsOfInterest = set()
        self.photoFolder = None
        self.QAcodes = None
        self.componentIDs = []
        self.nextID = 0

    def SetHierarchyColumns(self, cols):
        self.hierarchyColumns = cols

    def AddComponent(self):
        self.componentIDs.append(self.nextID)
        self.nextID += 1

    def __repr__(self):
        attrs = "\n".join(f"{k}={v!r}" for k, v in vars(self).items())
        return f"{self.__class__.__name__}\n{attrs}"
