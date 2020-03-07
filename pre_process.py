import numpy as np
from PIL import Image as PilImage, ImageFilter, ImageOps
from PythonMagick import _PythonMagick as PythonMagick
from PyPDF2 import PdfFileWriter, PdfFileReader

def get_stream(org_path):
    pdf_stream = PdfFileReader(open(org_path, "rb"))
    return pdf_stream
    
def pdf_to_text(pdf_file):
    pdf_in=PdfFileReader(open(pdf_file, "rb"))
    npage = pdf_in.getNumPages()
    pdf_out = PdfFileWriter()
    for pg_num in range(npage):
        pdf_out.addPage(pdf_in.getPage(pg_num))
    out_stream = open('adhoc/pdfout.txt','wb')
    pdf_out.write(out_stream)
    out_stream.close()
    
        
def write_pdf(pdf_img,pgNo,directory,filename):
    img_obj = pdf_img.getPage(pgNo)
    output = PdfFileWriter()
    output.addPage(img_obj)
    pdf_path=directory+"/temp/"+filename+".pdf"
    with open(pdf_path, "wb") as outputStream:
        output.write(outputStream)
    return pdf_path

    
def pdf_to_jpg(pdf_path,pgNo,directory,filename):
    img_path=directory+"/temp/"+filename+".jpg"
    pmimg = PythonMagick.Image()
    pmimg.density('200')
    pmimg.read(pdf_path)
    pmimg.write(img_path)
    #im = PilImage.open(img_path); print(im.info)
    return img_path
    
    
def remove_hlines(img):
    #img=img.convert('L')
    data = np.array(img)
    row_count=data.shape[0]
    col_count=data.shape[1]
    limit=5
    for row in range(row_count):
        if row>2:
            cur_row=data[row]
            black_len=len(cur_row[cur_row<128])
            black_line=black_len/col_count
            if black_line>0.3:
                for i in range(-limit,limit):
                    data[row+i]=np.repeat([255],col_count)
    rimg = PilImage.fromarray(data)
    return rimg
    
    
def remove_vlines(img):
    #img=img.convert('L')
    data = np.array(img)
    data=data.transpose()
    row_count=data.shape[0]
    col_count=data.shape[1]
    limit=10
    for row in range(row_count):
        if row>2:
            cur_row=data[row]
            black_len=len(cur_row[cur_row<128])
            black_line=black_len/col_count
            if black_line>0.3:
                for i in range(-limit,limit):
                    data[row+i]=np.repeat([255],col_count)
    data=data.transpose()
    rimg = PilImage.fromarray(data)
    return rimg

    
def remove_lines(img):
    img=remove_vlines(img)
    img=remove_hlines(img)
    return img

    
def enhance(data):
    data[data<200]=0
    data[data>=200]=255
    return data
    
    
def img_resize(img, ratio):
    x,y=img.size
    w=int(x*ratio)
    h=int(y*ratio)
    img=img.resize((w,h), PilImage.ANTIALIAS)
    return img
      
    
def pre_process(img_path):
    img = PilImage.open(img_path)
    img = img.convert('L')
    #img = img_resize(img,1)
    img = img.filter(ImageFilter.SHARPEN)
    #img=remove_lines(img)
    #img=ImageOps.invert(img)
    img.save(img_path)
    return img_path

        
        
        
        
        
        
            
            
