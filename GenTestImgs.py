from PIL import Image, ImageDraw, ImageFont
import os
import random

def GenTextImg(savePath, textString):

    w = 1600
    h = 1200
    n = 40 # how many characters per line

    font = ImageFont.load_default(50)

    text_x = int(20)
    text_y = int(h/2)

    text_color = (0, 0, 0)

    for i in range(0, random.randint(1,5)):
        img = Image.new("RGB", [w,h], color = (255,255,255))
        draw = ImageDraw.Draw(img)
        draw.text((text_x, text_y), "\n".join([textString[i:i+n] for i in range(0, len(textString), n)]) + f" {i+1}", font=font, fill=text_color)
        img.save(savePath + "\\" + textString + f"_{i+1}.jpg")

    


def GenImgs(root : str, structureDict : dict):

    absRoot = os.path.abspath(__file__).split("\\")[0:-1]
    
    for k,v in structureDict.items():
        newPath = root + "\\" + k
        if not os.path.isdir(newPath):
            os.mkdir(newPath)
        if not v:
            text = ""
            for t in newPath.split("\\"):
                if t in set(newPath.split("\\")).difference(set(absRoot)):
                    text += t + " "
            text = text[0:-1]
            GenTextImg(newPath, text)
        
        GenImgs(newPath, v)

def GenStructureDict(xlsPath : str) -> dict:
    import pandas as pd
    data = pd.read_excel(xlsPath, sheet_name="Structure")
    structure = {}
    for i, row in data.iterrows():
        levels = [str(row[c]) for c in data.columns if str(row[c]) != "nan"]
        currentLevel = structure
        for level in levels:
            if level not in currentLevel:
                currentLevel[level] = {}
            currentLevel = currentLevel[level]
    return structure


def main():

    root = "\\".join(os.path.abspath(__file__).split("\\")[0:-1])
    structure = GenStructureDict(root + "\\HRSG data.xlsx")

    GenImgs(root+"\\HRSG Test", structure)

if __name__ == "__main__":
    main()