from PIL import Image, ImageDraw, ImageFont
import os

def GenTextImg(savePath, textString):

    w = 255
    h = 255

    img1 = Image.new("RGB", [w,h], color = (255,255,255))
    img2 = Image.new("RGB", [w,h], color = (255,255,255))
    draw1 = ImageDraw.Draw(img1)
    draw2 = ImageDraw.Draw(img2)
    font = ImageFont.load_default()

    text_x = int(20)
    text_y = int(h/2)

    text_color = (0, 0, 0) 

    draw1.text((text_x, text_y), textString + " 1", font=font, fill=text_color)
    draw2.text((text_x, text_y), textString + " 2", font=font, fill=text_color)

    img1.save(savePath + "\\" + textString + "_1.jpg")
    img2.save(savePath + "\\" + textString + "_2.jpg")

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

def main():

    root = "\\".join(os.path.abspath(__file__).split("\\")[0:-1])
    structure = {
        "PowerStation" :{
            "Unit1" : {
                "MS" : {
                    "H1" : {},
                    "H2" : {
                        "East" : {},
                        "West" : {},
                    },
                    "H3" : {},
                    "H4" : {},
                    "H5" : {
                        "East" : {},
                        "West" : {},
                    },
                    "H6" : {
                        "North" : {},
                        "South" : {},
                    },
                    "H7" : {
                        "East" : {},
                        "West" : {},
                    },
                    "H8" : {},
                    "H9" : {},
                },
                "HRH" : {
                    "H1" : {
                        "East" : {},
                        "West" : {},
                    },
                    "H2" : {},
                    "H3" : {},
                    "H4" : {
                        "East" : {},
                        "West" : {},
                    },
                    "H5" : {},
                    "H6" : {},
                    "H7" : {
                        "North" : {},
                        "South" : {},
                    },
                    "H8" : {},
                    "H9" : {},
                },
                "CRH" : {
                    "H1" : {},
                    "H2" : {
                        "East" : {},
                        "West" : {},
                    },
                    "H3" : {},
                    "H4" : {},
                    "H5" : {},
                    "H6" : {},
                    "H7" : {},
                    "H8" : {
                        "North" : {},
                        "South" : {},
                    },
                    "H9" : {},
                },
                "Feedwater" : {
                    "H1" : {},
                    "H2" : {},
                    "H3" : {
                        "East" : {},
                        "West" : {},
                    },
                    "H4" : {},
                    "H5" : {},
                    "H6" : {},
                    "H7" : {
                        "East" : {},
                        "West" : {},
                    },
                    "H8" : {
                        "North" : {},
                        "South" : {},
                    },
                    "H9" : {},
                },
                "Bypass" : {
                    "H1" : {},
                    "H2" : {},
                    "H3" : {},
                    "H4" : {},
                    "H5" : {},
                    "H6" : {},
                    "H7" : {},
                    "H8" : {},
                    "H9" : {},
                },
                "Misc" : {}

            },
            "Unit2" : {
                "MS" : {
                    "H1" : {},
                    "H2" : {
                        "East" : {},
                        "West" : {},
                    },
                    "H3" : {},
                    "H4" : {},
                    "H5" : {
                        "East" : {},
                        "West" : {},
                    },
                    "H6" : {
                        "North" : {},
                        "South" : {},
                    },
                    "H7" : {
                        "East" : {},
                        "West" : {},
                    },
                    "H8" : {},
                    "H9" : {},
                },
                "HRH" : {
                    "H1" : {
                        "East" : {},
                        "West" : {},
                    },
                    "H2" : {},
                    "H3" : {},
                    "H4" : {
                        "East" : {},
                        "West" : {},
                    },
                    "H5" : {},
                    "H6" : {},
                    "H7" : {
                        "North" : {},
                        "South" : {},
                    },
                    "H8" : {},
                    "H9" : {},
                },
                "CRH" : {
                    "H1" : {},
                    "H2" : {
                        "East" : {},
                        "West" : {},
                    },
                    "H3" : {},
                    "H4" : {},
                    "H5" : {},
                    "H6" : {},
                    "H7" : {},
                    "H8" : {
                        "North" : {},
                        "South" : {},
                    },
                    "H9" : {},
                },
                "Feedwater" : {
                    "H1" : {},
                    "H2" : {},
                    "H3" : {
                        "East" : {},
                        "West" : {},
                    },
                    "H4" : {},
                    "H5" : {},
                    "H6" : {},
                    "H7" : {
                        "East" : {},
                        "West" : {},
                    },
                    "H8" : {
                        "North" : {},
                        "South" : {},
                    },
                    "H9" : {},
                },
                "Bypass" : {
                    "H1" : {},
                    "H2" : {},
                    "H3" : {},
                    "H4" : {},
                    "H5" : {},
                    "H6" : {},
                    "H7" : {},
                    "H8" : {},
                    "H9" : {},
                },
                "Misc" : {}
            }}
        }

    GenImgs(root, structure)

if __name__ == "__main__":
    main()