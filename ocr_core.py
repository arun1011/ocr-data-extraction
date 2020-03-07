import builtins
import pytesseract
from PIL import Image as PilImage
import os
from pre_process import get_stream, write_pdf, pdf_to_jpg, pre_process
import numpy as np

#stop=[word.strip() for word in open('keywords.txt')]; #print(stop)

original_open = open
def bin_open(filename, mode='rb'): # note, the default mode now opens in binary
    return original_open(filename, mode)

# tesseract location must be changed in pytesseract     
def tes_ocr(img):
    pytesseract.pytesseract.tesseract_cmd='C:\\Program Files\\Tesseract-OCR\\tesseract.exe'
    try:
        builtins.open = bin_open
        bts = pytesseract.image_to_string(img)
    finally:
        builtins.open = original_open
    ocr_txt=(str(bts, 'cp1252', 'ignore'))
    return ocr_txt

    
def check_extract(extract,min_threshold):
    use=[]
    for word in extract:
        for letter in word:
            if letter.isalpha() or letter.isdigit():
                use.append(word)
        if len(use) > min_threshold:break
    return use

    
def ful_ocr(img_path):
    angle=0
    min_threshold=5
    while True:
        if angle<-360:
            ocr_txt=""
            break
        img=PilImage.open(img_path)
        ocr_txt = tes_ocr(img)
        extract=ocr_txt.split()
        use=check_extract(extract,min_threshold)
        if len(use) > min_threshold:
            img.save(img_path)
            break
        else:
           angle=angle-90
           img=img.rotate(angle, expand=True)
           img.save(img_path)
    return ocr_txt

    
def change_angle(img_path,angle):
    img=PilImage.open(img_path)
    img=img.rotate(angle)
    img.save(img_path)
           
def image_to_data(img_path):
    img = PilImage.open(img_path); img = img.convert('L')
    data = np.array(img); return data
    
def data_to_image(data):
    img = PilImage.fromarray(data)
    return img


def get_region(img_path,coordinates):
    data=image_to_data(img_path); d=data.shape
    sr=int(coordinates[0][0]*d[0]); er=int(coordinates[0][1]*d[0])
    rows=data[sr:er]; #print(sr,er)
    sc=int(coordinates[1][0]*d[1]); ec=int(coordinates[1][1]*d[1])
    region=[row[sc:ec] for row in rows]; #print(sc,ec)
    region=np.array(region); #print(region.shape)
    rimg=data_to_image(region)
    rimg=rimg.rotate(coordinates[2], expand=True)
    rimg.save(img_path)
    
   
def ocr_accuracy(txt):
    n=0
    if len(txt)==0: return 0
    for l in txt:
        if l.isalpha() or l.isdigit():
            n=n+1
    v=n/len(txt); v=v+0.15
    if v>1: v=1
    return round(v,2)
    

#cordinates in % ratio of rows and columns
def ocr_extract(directory,filename,coordinates):
    ocr_txt=""; org_path=directory+'/'+filename
    acculist={}
    if not os.path.exists(directory+"/temp"):
        os.makedirs(directory+"/temp")
    print('OCR Running...')   
    if filename[-4:].lower() in ['.jpg','.png']:
        img = PilImage.open(org_path); #print(img.size)
        img_path=directory+"/temp/"+filename
        img.save(img_path)
        if coordinates!=[]: get_region(img_path,coordinates)
        #img_path=pre_process(img_path);
        ocr_txt=ful_ocr(img_path)
        #os.remove(img_path)
    
    if filename.lower().endswith(".pdf"):
        prefix = filename[:-4]
        pdf_stream=get_stream(org_path)
        npage = pdf_stream.getNumPages()
        for pgNo in range(npage):
            print('Pg'+str(pgNo))
            filenamex=prefix+'_'+str(pgNo)
            pdf_path=write_pdf(pdf_stream,pgNo,directory,filenamex)
            img_path=pdf_to_jpg(pdf_path,pgNo,directory,filenamex)
            #print(image_to_data(img_path).shape)
            os.remove(pdf_path); #return
            if coordinates!=[]: get_region(img_path,coordinates)
            img_path=pre_process(img_path)
            txt=ful_ocr(img_path)
            acculist['pg'+str(pgNo+1)]=ocr_accuracy(txt)
            ocr_txt=ocr_txt+txt+'\n'
            #os.remove(img_path)
            #break
            
    if filename.lower().endswith(".tif"):
        prefix = filename[:-4]
        im = PilImage.open(org_path)
        pgcount=im.n_frames
        for pgNo in range(pgcount):
            img_path = directory+"/temp/"+prefix+"_"+str(pgNo)+".jpg"
            if pgcount>1:
                img=im.seek(pgNo)
            else:
                img=im
            img.save(img_path)
            if coordinates!=[]: get_region(img_path,coordinates)
            img_path=pre_process(img_path)
            txt=ful_ocr(img_path)
            acculist['pg'+str(pgNo+1)]=ocr_accuracy(txt)
            ocr_txt=ocr_txt+txt+'\n'
            #os.remove(img_path)
            #break
    #with open('ocr_out.txt','w') as f: f.write(ocr_txt)
    return [ocr_txt, acculist]

#img = PilImage.open('adhoc/temp/f.jpg'); print(img.size)
#cordinates=[[0.575,0.594],[0.517,0.853],0]
#txt=ocr_extract('adhoc/temp','f.jpg',cordinates).split('\n')
#for t in txt:
#    t=t.strip()
#    if t!="": print(t)