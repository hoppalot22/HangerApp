import cv2 as cv
from PIL import Image, ImageTk
import matplotlib.pyplot as plt
import numpy as np
import os
import sys
import tkinter
from tkinter import ttk

class App():
    def __init__(self):
        self.root = tkinter.Tk()
        self.root.title("TestApp")
        self.imgEditor = ImageEditor(self.root)
        self.imgEditor.grid()
        

class ImageEditor(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.img = None
        self.tkImg = None
        self.w = None
        self.h = None
        self.parent = parent
        self.canvas1 = tkinter.Canvas(self, bg = "white")
        self.canvas2 = tkinter.Label(self)
        self.canvas1.bind("<Button-1>", self.OnClick)    
        self.canvas1.bind("<ButtonRelease-1>", self.OnRelease)
        self.canvas1.bind("<Motion>", self.OnMouseMove)

        self.perspectiveRect = [CanvasObject([50,50]),CanvasObject([100,50]),CanvasObject([100,100]),CanvasObject([50,100])]
        self.selected = None

        self.canvas1.grid()
        self.canvas2.grid()

    def loadImg(self, imgPath):
        self.img = Image.open(imgPath)
        self.img.thumbnail([500,500])
        self.tkImg = ImageTk.PhotoImage(self.img)
        self.img = np.array(self.img)
        self.w,self.h = [self.tkImg.width(), self.tkImg.height()]

        self.canvas1.configure(width=self.w, height=self.h)
        self.UpdateScreen()

    def Select(self, obj):
        self.selected = obj
        return

    def OnClick(self, event):
        for obj in self.perspectiveRect:
            if (obj.pos[0]+obj.radius > event.x > obj.pos[0]-obj.radius) and (obj.pos[1]+obj.radius > event.y > obj.pos[1]-obj.radius):
                self.Select(obj)
                break
 
    def OnRelease(self, event):
        self.selected = None
        return
    
    def OnMouseMove(self, event):
        if self.selected is not None:
            self.selected.pos = [event.x, event.y]
            self.UpdateScreen()

    def UpdateScreen(self):
        self.canvas1.create_image(0,0,image = self.tkImg, anchor = "nw")

        rect = [self.perspectiveRect[0].pos,self.perspectiveRect[1].pos,self.perspectiveRect[2].pos,self.perspectiveRect[3].pos]

        self.canvas1.create_polygon(*rect, fill="", outline = "black")

        for obj in self.perspectiveRect:
            self.canvas1.create_oval(obj.pos[0]+obj.radius, obj.pos[1]+obj.radius, obj.pos[0]-obj.radius, obj.pos[1]-obj.radius, fill = "red", outline="red")


        matrix = cv.getPerspectiveTransform(np.float32(rect), np.float32([[self.w*0.2,self.h*0.2],[self.w*.8,self.h*0.2],[self.w*0.8,self.h*0.8],[self.w*0.2, self.h*0.8]]))
        warpedImg = cv.warpPerspective(self.img, matrix, [self.w,self.h])
        self.warpedImg = ImageTk.PhotoImage(Image.fromarray(warpedImg))
        
        self.canvas2.configure(image = self.warpedImg)



class CanvasObject():
    def __init__(self, pos):
        self.pos = pos
        self.fill = [255,0,0]
        self.outline = [0,0,0]
        self.radius = 5


def Main():

    myApp = App()
    myApp.root.mainloop()
    return

if __name__ == "__main__":
    Main()