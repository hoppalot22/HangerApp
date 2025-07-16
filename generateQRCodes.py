import os
import sys
import pandas as pd
import openpyxl
import docx
import qrcode
import cv2

def getData(xlDoc):

    sheets = pd.read_excel(xlDoc, sheet_name = None, header  = 1)

    print(sheets)

    data = pd.DataFrame()

    for sheet in sheets:
        data = pd.concat([data, sheets[sheet]], join = "outer", ignore_index=True)

    data.round(decimals=1)
    return data

def Read():
    detector = cv2.QRCodeDetector()
    ret = detector.detectAndDecodeMulti(cv2.imread(sys.argv[1]))
    print(ret)

def Main():

    CURR_DIR = __file__[:-len(os.path.basename(__file__))]

    hangerData = getData(sys.argv[1])
    print(hangerData)

    wordDoc = docx.Document()
    numCols = 4
    rowsPerPage = 4
    codesPerPage = rowsPerPage*numCols

    codeSize = 1.5

    for i in hangerData.index:
        ID = f"{hangerData["Line"][i]} {hangerData["Hanger Designation"][i]}"
        print(ID)
        qrCode = qrcode.QRCode()
        qrCode.add_data(ID)
        img = qrCode.make_image()
        img.save(f"{CURR_DIR}\\QRCodes\\{ID}.png")

        if i%codesPerPage == 0:
            offset = i
            table = wordDoc.add_table(rows = rowsPerPage, cols = numCols)
            wordDoc.add_page_break()

        table.cell(int((i-offset)/numCols), (i-offset)%numCols).paragraphs[0].add_run(ID+"\n").add_picture(f"{CURR_DIR}\\QRCodes\\{ID}.png", width=docx.shared.Inches(codeSize), height = docx.shared.Inches(codeSize))

    wordDoc.save(f"{CURR_DIR}\\qrTest.docx")

    return

if __name__ == "__main__":
    #Main()
    Read()