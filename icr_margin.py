import numpy as np

def get_white_ratio(data,row,white_range):
    white=data[row]; white_ratio=0
    if len(white)>0:
        white_line=len(white[white>white_range])
        white_ratio=white_line/len(white); #print(white_ratio)
    return white_ratio

    
def find_blocks(data,last_row_end,white_range,threshold):
    row_count=data.shape[0]; row_start='s'; row_end='e';
    for row in range(last_row_end,row_count):
        if get_white_ratio(data,row,white_range) <= threshold : row_start=row; break
    if row_start=='s': return None
    for row in range(row_start,row_count):
        if get_white_ratio(data,row,white_range) > threshold: row_end=row; break
    if row_end=='e': row_end=row_count
    row_cordinates = [row_start, row_end]; #print(str(row_cordinates))
    return row_cordinates

    
def split_image(data,trans,white_range,threshold):
    row_count=data.shape[0]; row_start=0; row_end=0; row_array=[]
    while row_end < row_count:
        region=find_blocks(data,row_end,white_range,threshold)
        if region is None: break
        row_start=region[0]; row_end=region[1]
        buffer=int((row_end-row_start)*0.2); 
        part_row=data[row_start-buffer:row_end+buffer]        
        converted=[p for p in part_row]
        if len(converted)>0:
            converted=np.array(converted)
            if trans==1: converted=converted.transpose()
            row_array.append(converted)
    return row_array
