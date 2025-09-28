import cv2 as cv
from PIL import Image, ImageTk
import matplotlib.pyplot as plt
import numpy as np
import os
import sys
import tkinter as tk
from tkinter import ttk

class App():
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("TestApp")
        self.imgEditor = ImageEditor(self.root)
        self.imgEditor.grid()
        

class ImageEditor(ttk.Frame):
    def __init__(self, parent : ttk.Frame):
        super().__init__(parent)
        self.img = None #Original image

        self.canv1Img = None #Display image
        self.canv2Img = None #Image after perspective correction
        self.canv1ImgDisp = None #Display image
        self.canv2ImgDisp = None #Image after perspective correction

        self.imageWidth = None
        self.imageHeight = None
        self.targetDims = [400, 400]
        self.zoom = 1.0
        self.zoomRect = None
        self.parent = parent
        self.canvas1 = tk.Canvas(self, bg = "white")
        self.canvas2 = tk.Canvas(self, bg = "white")
        self.canvas1.bind("<Button-1>", self.OnClick)    
        self.canvas1.bind("<ButtonRelease-1>", self.OnRelease)
        self.canvas1.bind("<Motion>", self.OnMouseMove)
        self.canvas2.bind("<MouseWheel>", self.OnZoom)

        self.perspectiveOverlay = tk.BooleanVar()
        self.perspectiveRect = [CanvasObject([50,50]),CanvasObject([100,50]),CanvasObject([100,100]),CanvasObject([50,100])]
        self.selected = None

        self.canvas1.grid()
        self.canvas2.grid()

    def loadImg(self, imgPath):
        #load image into memory, assign self.img and self.finalImg to cv2 format then resize and assign the display imgage (tkImg)
        pil_img = Image.open(imgPath)
        self.img = np.array(pil_img)
        pil_img.thumbnail(self.targetDims, Image.LANCZOS)
        self.imageWidth, self.imageHeight = pil_img.size

        # Create a downscaled version for display/zoom

        self.canv1Img = np.array(pil_img)
        self.canv2Img = self.canv1Img.copy()
        self.canv1ImgDisp = makeThumb(self.canv1Img, size = self.targetDims)
        self.canv2ImgDisp = makeThumb(self.canv1Img, size = self.targetDims)

        self.displayWidth, self.displayHeight = self.canv1ImgDisp.width(), self.canv1ImgDisp.height()
        self.zoomRect = [0, 0, self.displayWidth, self.displayHeight]
        self.zoom = 1.0

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

    def OnResize(self, event):
        #print(event)
        #self.UpdateScreen()
        pass
    
    def OnZoom(self, event):
    
        # Mouse position on canvas
        if hasattr(event, 'x') and hasattr(event, 'y'):
            mx, my = event.x, event.y
            # Map mouse position to image coordinates within the crop
            rel_x = mx / self.displayWidth
            rel_y = my / self.displayHeight

            if hasattr(event, 'delta'):
                if event.delta > 0:
                    self.zoom *= 1.1
                else:
                    self.zoom /= 1.1
            elif hasattr(event, 'num'):
                if event.num == 4:
                    self.zoom *= 1.1
                elif event.num == 5:
                    self.zoom /= 1.1
                else:
                    pass
            else:
                pass

            self.zoom = max(1, min(self.zoom, 10.0))
            zoom_w = int(self.displayWidth / self.zoom)
            zoom_h = int(self.displayHeight / self.zoom)

            zx, zy = self.zoomRect[0] + int(rel_x * zoom_w), self.zoomRect[1] + int(rel_y * zoom_h)

            x0 = int(min(max(0,zx * (1-zoom_w/self.displayWidth)), self.displayWidth - zoom_w))
            y0 = int(min(max(0, zy * (1-zoom_h/self.displayHeight)), self.displayHeight - zoom_h))
            x1 = int(max(min(x0 + zoom_w, self.displayWidth), zoom_w))
            y1 = int(max(min(y0 + zoom_h, self.displayHeight), zoom_h))

            self.zoomRect = [x0, y0, x1, y1]

        else:
            # No mouse info, just zoom on center
            if hasattr(event, 'delta'):
                if event.delta > 0:
                    self.zoom *= 1.1
                else:
                    self.zoom /= 1.1
            elif hasattr(event, 'num'):
                if event.num == 4:
                    self.zoom *= 1.1
                elif event.num == 5:
                    self.zoom /= 1.1
        self.zoom = max(1, min(self.zoom, 10.0))
        self.UpdateScreen(canvas1=True)

    def UpdateScreen(self, canvas1 = True, canvas2 = True, resetZoom = False):

        if (self.targetDims[0] == 0) or (self.targetDims[1] == 0):
            return
        
        if resetZoom:
            self.zoom = 1.0
            self.zoomFocus = [self.targetDims[0] // 2, self.targetDims[1] // 2] 
        
        if canvas1:
            self.canv1ImgDisp = makeThumb(self.canv1Img, size=self.targetDims)
            self.canvas1.configure(width=self.canv1ImgDisp.width(), height=self.canv1ImgDisp.height())
            self.canvas2.configure(width=self.canv1ImgDisp.width(), height=self.canv1ImgDisp.height())
            self.canvas1.create_image(0,0, image = self.canv1ImgDisp, anchor = "nw")

        if canvas2:
            if (self.perspectiveOverlay.get()):
                rect = [obj.pos for obj in self.perspectiveRect]
                self.canvas1.create_polygon(*rect, fill="", outline = "black")

                for obj in self.perspectiveRect:
                    self.canvas1.create_oval(obj.pos[0]+obj.radius, obj.pos[1]+obj.radius, obj.pos[0]-obj.radius, obj.pos[1]-obj.radius, fill = "red", outline="red")
    
                matrix = cv.getPerspectiveTransform(
                    np.float32(rect), 
                    np.float32([
                        [0, 0],
                        [self.imageWidth, 0],
                        [self.imageWidth ,self.imageHeight],
                        [0, self.imageHeight]
                    ])
                )
                self.canv2Img = cv.warpPerspective(self.canv1Img, matrix, (self.imageWidth, self.imageHeight))
            else:
                self.canv2Img = self.canv1Img.copy()

            self.canvas1.create_rectangle(*self.zoomRect, outline="green", width=1)

            x0, y0, x1, y1 = self.zoomRect

            # Crop and then resize to display size for true zoom
            cropped = self.canv2Img[y0:y1, x0:x1]
            pil_cropped = Image.fromarray(cropped)
            pil_cropped = pil_cropped.resize([self.displayWidth, self.displayHeight], Image.LANCZOS)
            self.canv2ImgDisp = ImageTk.PhotoImage(pil_cropped)
            
            self.canvas2.create_image(0,0, image = self.canv2ImgDisp, anchor = "nw")


class CanvasObject():
    def __init__(self, pos):
        self.pos = pos
        self.fill = [255,0,0]
        self.outline = [0,0,0]
        self.radius = 5

def makeThumb(img, size = [500, 500]):
    img = Image.fromarray(img)
    img.thumbnail(size)
    return ImageTk.PhotoImage(img)

def Main():

    myApp = App()
    myApp.root.mainloop()
    return

if __name__ == "__main__":
    Main()