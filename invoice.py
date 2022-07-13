from PIL import Image, ImageEnhance, ImageFilter
import sys
import json
import pytesseract
from pytesseract import Output
import re
from matplotlib import pyplot as plt

#----image_preprocess----

im = Image.open(sys.argv[1])
# im=Image.open('Tn2page0.jpg')
#im=Image.open('Tn2page0.jpg')
im=im.convert('L')
im=im.resize((3000,4000), Image.BICUBIC)
im=im.point(lambda p: p >100  and p + 50)
amount = im.crop((2300, 900, 3000, 4000))
rest = im.crop((100, 150, 2900, 1000))
im.save('1.jpg', 'JPEG')


#-----Reading the image-----------------------------------------------------

import cv2
import numpy as np
img = cv2.imread('1.jpg', 1)
tessdata_dir_config = "C:\\Program Files\\Tesseract-OCR\\tesseract.exe"

#----plot bboxes-------

def plot_rgb(image):
    plt.figure(figsize=(14, 10))
    return plt.imshow(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))

d = pytesseract.image_to_data(img, output_type=Output.DICT)
n_boxes = len(d['text'])
boxes = cv2.cvtColor(img.copy(), cv2.COLOR_BGR2RGB)
for i in range(n_boxes):
    (x, y, w, h) = (d['left'][i], d['top'][i], d['width'][i], d['height'][i])    
    boxes = cv2.rectangle(boxes, (x, y), (x + w, y + h), (255, 0, 0), 2)
    
plot_rgb(boxes)

#----extract_text------

extracted_text = pytesseract.image_to_string(img)
extracted_rest = pytesseract.image_to_string(rest)
extracted_amount = pytesseract.image_to_string(amount)

#print(extracted_text)
et=extracted_text.replace(' ',"#*#")
results={}

#----regex_results------

def get_company_name(string):
    r = re.compile(r'[A-Za-zA-z ]+')
    return r.findall(string)
name=get_company_name(extracted_rest)
company_name = name[0]
#print(company_name)
results['company_name'] = company_name


def get_ifsc_code(string):
    r = re.compile(r'[A-Z]{4}\d{7}')
    return r.findall(string)
ifsc=get_ifsc_code(extracted_text)
#print(ifsc)
results['ifsc'] = ifsc

def get_gstin(string):
    r = re.compile(r'[A-Z0-9]{15}')
    return r.findall(string)

gstin = get_gstin(extracted_text)
#print(gstin)
results['gstin'] = gstin

def get_mobile_no(string):
    r = re.compile(r'\d{3}[-]\d*|[0-9]{10}\s|\s[0-9]{10}\s')
    return r.findall(string)

phn = get_mobile_no(extracted_text)
#print(phn)
results['phn'] = phn

def get_date_of_invoice(string):
    r = re.compile(r'\d+[-][A-z]+[-]\d+')
    return r.findall(string)

date_of_invoice = get_date_of_invoice(extracted_text)
#print(date_of_invoice)
results['date_of_invoice'] = date_of_invoice

#----store results into json----

result_json = json.dumps(results)
print(result_json)

with open('result2.json', 'w') as f:
    json.dump(results, f)


items={}

#-----regex_item----

def get_item_qty(string):
    r = re.compile(r'\s\d[ .]\d{3}\s|\s\d*\snos|\d*[.]\d+rft|\d*[.]\d+RFT|\d*[.]\d+\sRFT|\d+[.]\d+\srft')
    return r.findall(string)
item_qty=get_item_qty(extracted_text)
#print(item_qty)
items['item_qty'] = item_qty


def get_size(string):
    r = re.compile(r'\d[.]\d\sMm\s|\d[.]\d\smm\s|\d[.]\d\sMM\s|\d*Mm\s|\d*mm\s|\d*MM\s|\d*mm|\d*MM|\d*kg|\d*KG|\d+sqmt|\d+SQMT|\d+\sSQMT|\d+\ssqmt')
    return r.findall(string)
item_size=get_size(extracted_text)
#print(item_size)
items['size'] = item_size


def get_amount(string):
    r = re.compile(r'\d*[,]\d*[.]\d*')
    return r.findall(string)
amount=get_amount(extracted_amount)
#print(amount)
items['amount'] = amount

#----store_item into json------

item_json = json.dumps(items)
print(item_json)

with open('item2.json', 'w') as f:
    json.dump(items, f)

with open('output.txt', 'w') as f:
    f.write(extracted_text)    