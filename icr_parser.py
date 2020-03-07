#parse('input','aodl.pdf')
import ocr_core, icr_margin
from difflib import SequenceMatcher
import numpy as np
import os
approot=""
xmark=ocr_core.image_to_data(approot+'img_marks/c3/xmark.jpg'); #print(len(xmark))
premark=['X','x']
postmark=['gen','cap','inc','capiinc','can','ndf']
marklist=[line.strip() for line in open(approot+'marklist.txt','r')]; #print(xmarklist)
mislist=[line.strip() for line in open(approot+'miscase.txt','r')]
miscase={}
for mis in mislist: mix=mis.split(':'); miscase[mix[0]]=mix[1]
#print(miscase);return
c1=[line.strip() for line in open(approot+'c1_fields.cfg.txt')]; #print(c1)
c2=[line.strip() for line in open(approot+'c2_options.cfg.txt')]; #print(optlist)
c3=[line.strip() for line in open(approot+'c3_multioptions.cfg.txt')]


def enhance(data):
    data[data<200]=0
    data[data>=200]=255
    return data

def read_image(inputfolder):
    i=0; j=0; marketfolder=approot+'snippets/market'
    for f in os.listdir(inputfolder+'/temp'):
        if f.lower().endswith('.jpg'):
            img_path=inputfolder+'/temp/'+f
            data=ocr_core.image_to_data(img_path); #data=icr_noise.remove_noise(data)
            row_array=icr_margin.split_image(data,0,230,0.985); #print(len(row_array)); return
            for rows in row_array:
                if len(rows)<10: continue
                if f.lower().endswith('_2.jpg') or f.lower().endswith('_3.jpg'):
                    leftlen=int(len(rows[0])*0.48)
                    left=[part[:leftlen] for part in rows]; left=np.array(left)    
                    ocr_core.data_to_image(left).save(marketfolder+'/left_'+str(i)+'.jpg')
                    right=[part[leftlen:] for part in rows]; right=np.array(right)    
                    ocr_core.data_to_image(right).save(marketfolder+'/right_'+str(i)+'.jpg')                    
                    i=i+1
                if f.lower().endswith('.jpg'):
                    ocr_core.data_to_image(rows).save(approot+'snippets/'+str(j)+'.jpg') 
                    j=j+1
                        

def sim(a,b):
    sim_score = SequenceMatcher(None,a,b).ratio()
    return sim_score
    
#applies only equal length strings
def lsim(a,b):
    a=a.split(); b=b.split()
    lena=len(a); match=0
    for i in range(lena):
        if a[i][:2]==b[i][:2]:
            match=match+0.5
        if a[i][-2:]==b[i][-2:]:
            match=match+0.5
    return match/lena


def exit_condition(word,pos,xlist):
    e=0
    for x in xlist:
        if sim(x.lower(), word.lower())>=0.6: 
            e=1
    return e
    
def clear_folder(folder):
    for f in os.listdir(folder): 
        if f.endswith('.jpg'):
            os.remove(folder+'/'+f)

def do_clear(inputfolder):
    clear_folder(inputfolder+'/'+'temp')
    clear_folder(approot+'snippets')
    clear_folder(approot+'snippets/temp')
    clear_folder(approot+'snippets/market')
    clear_folder(approot+'snippets/market/temp')

    
def icr_mscore(img_path, xmark, pxdif, th, limit, xratio, yratio):
    
    marklen=len(xmark)            
    img_data=ocr_core.image_to_data(img_path)
    imglen=len(img_data)
    if imglen<int(limit*0.8): return 0, (0,)
    iratio=len(img_data[img_data<5])/(imglen*len(img_data[0]))
    if iratio<0.01 or iratio>0.1: return 0,(0,0)
    
    if limit!=None and limit<marklen and limit<imglen:
        dif=int((imglen-limit)/2)
        row=img_data[dif:dif+limit]
        difx=int((marklen-limit)/2)
        xmark=xmark[difx:difx+limit]
    elif imglen>marklen:
        dif=int((imglen-marklen)/2)
        row=img_data[dif:dif+marklen]
        xmark=xmark
    else:
        difx=int((marklen-imglen)/2)
        xmark=xmark[difx:difx+imglen]
        row=img_data
    
    #mfolder=approot+'snippets/match'
    #ocr_core.data_to_image(xmark).save(mfolder+'/markx.jpg'); #return
    xmark=enhance(xmark)
    
    ucl=0; lcl=len(xmark); xmark=xmark[ucl:lcl]
    ms=xmark.shape; msr=ms[0]; msc=ms[1]; t=msr*msc
    mval=len(xmark[xmark<5]); mratio=mval/t
    
    mscore=0; lastscore=0; mwindow=np.array([])
    for c in range(len(row[0])):
        if c+msc>len(row[0]):
            break
        window=[col[c:c+msc-1] for col in row]
        window=np.array(window)
        ewindow=enhance(window)
        if ewindow.shape[0]==0:
            continue
        bval=len(ewindow[ewindow<5])
        bratio=round(bval/t,2)
        if bratio<(mratio*0.8): 
            continue
        if bratio>(mratio*1.2): 
            continue
    
        m=0; rlist=[]
        for u in range(msr):
            r=0; rscore=0
            for v in range(msc):
                try:
                    if abs(int(ewindow[u][v])-int(xmark[u][v]))<=pxdif:
                        m=m+1
                        r=r+1
                except: 
                    m=m+0
            rscore=r/msc
            if rscore>th:rlist.append(rscore)
        x=(len(rlist)/msr)*xratio
        y=(m/t)*yratio
        mscore=round((x+y),2)
        if mscore>th and mscore>lastscore:
            lastscore=mscore
            mwindow=window
            if mscore>=0.8: break
        c=c+msc-1
    return mscore, mwindow

    
            
def ngram_map(txt_list,token_position,token_direction,token_size,break_list):
    #No case change
    ngram_list=[]; ngram=""
    if token_direction==1: s=0; e=token_size; 
    else: s=-token_size; e=0; 
    
    bsts=0; val=0; txtlen=len(txt_list)
    for c in range(s,e):
        if val>=txtlen: break
        for t in range(token_size-1,token_size+2):
            if val>=txtlen: break
            ngram=""
            for n in range(t):
                val=token_position+c+n
                if val>=txtlen: break
                ngram=ngram+" "+txt_list[val]
            ngram=ngram.strip()
            if ngram.lower() in break_list:
                bsts=1
                break
            if ngram not in ngram_list:
                ngram_list.append(ngram)
        if bsts==1: break
    return ngram_list   


# npos aligned with ngram_map logic
def get_match_pos(curpos, ngramlist, tgt):
    lastsim=0; rpos=-1; npos=0; tpos=-1; tgt=tgt.lower(); match=""
    
    tgtlen=len(tgt.split())
    if tgtlen<2: tgtsim=0.8
    if tgtlen<4: tgtsim=0.85
    if tgtlen<6: tgtsim=0.9
    if tgtlen>=6: tgtsim=0.95
    
    for ntxt in ngramlist:
        if npos==3:
            npos=0
        if npos==0:
            tpos=tpos+1
        npos=npos+1
        #print(npos, tpos)
        
        #if abs(len(ntxt.split())-len(tgt.split()))>1:continue
        ntxt=ntxt.lower()
        if ntxt==tgt:
            rpos=curpos+tpos
            match=ntxt
            break
        cursim=sim(ntxt,tgt)
        if cursim>=tgtsim and cursim>lastsim:
            lastsim=cursim
            rpos=curpos+tpos
            match=ntxt
            if cursim==1:break
            if ntxt.split()[0]==tgt.split()[0]: break
    return rpos, match


    
def c2_ocr_parser(fdict,optdict,ocrlist):
    
    olen=len(ocrlist)
    for opt in optdict:
        optlen=len(opt.split())
        if opt not in fdict: fdict[opt]=[]
        for x in range(olen):
            sts=0; nlist=[]
            if ocrlist[x] in marklist:
                select=""; #print(ocrlist[x+1])
                for item in optdict[opt]:
                    ref=""; refx=""; itemlen=len(item.split())
                    if itemlen>1:
                        for n in range(1, itemlen):
                            ref=ref+ocrlist[x+n]+" "
                            refx=ref+ocrlist[x+n+1]+" "
                        ref=ref.strip(); refx=refx.strip()
                        if ref=='':continue
                    else:
                        ref=ocrlist[x+1]; refx=ocrlist[x+1]+ocrlist[x+2]
                    #print(ref, refx)
                    if sim(ref.lower(),item.lower())>=0.8 or sim(refx.lower(),item.lower())>=0.8:
                        select=item; break
                if select!="":
                    nlist=ngram_map(ocrlist, x, -1, optlen+1, [])
                    if nlist!=[]:
                        #print(ocrlist[x]); print(ref); print(nlist)
                        for ntxt in nlist:
                           #if ntxt[:4]=='Full':print(ntxt)
                           if abs(len(ntxt.split())-len(opt.split()))>2:continue
                           if sim(ntxt.lower(), opt.lower())>=0.8:
                               #print(nlist)
                               fdict[opt]=select
                               sts=1
                               break
            if sts==1: break
    return fdict
    
          


def c2_icr_parser(fdict,optdict):
    
    pxdif=25 
    th=0.7
    limit=20 
    xratio=0.3
    yratio=1-xratio
    bm=0.5
    
    optionlist={}
    clear_folder(approot+'snippets/match')
    clear_folder(approot+'snippets/match/temp')
    
    c2folder=approot+'img_marks/c2'
    mfolder=approot+'snippets/match'
    sfolder=approot+'snippets'
    
    fn=0
    for f in os.listdir(sfolder):
        f=str(fn)+'.jpg'; fn=fn+1
        img_path=sfolder+'/'+f
        if not os.path.exists(img_path): continue
        if f.endswith('.jpg'):
            lastscore=0; fmax=""; fwindow=np.array([])
            for fname in  os.listdir(c2folder):
                optionprefix=fname[:-4]
                option=ocr_core.image_to_data(c2folder+'/'+fname)
                if optionprefix not in optionlist: optionlist[optionprefix]={}
                score, window=icr_mscore(img_path, option, pxdif, th, limit, xratio, yratio)
                if score>bm and score>lastscore:
                    lastscore=score
                    fmax=f
                    fwindow=window
                    foption=optionprefix
                    if score>=0.8: break
            print(fmax, foption,'->',lastscore,fwindow.shape)
            if  fmax!="" and fwindow.shape[0]>0:
                optionlist[foption][fmax]=lastscore
                ocr_core.data_to_image(fwindow).save(mfolder+'/'+fmax+'_'+str(score)+'_'+foption+'.jpg')     
    
    print('files detected: ', optionlist)
    
    lastlen=0
    for option in optionlist:
        curlen=len(optionlist[option])
        if curlen>lastlen:
            lastlen=curlen
            decision=option
        if curlen>0 and curlen==lastlen:
            if len(option.strip())==2:
                decision=option
    
    #getting OCR for detected files
    ocrdict={}
    for f in os.listdir(sfolder):
        for option in optionlist:
            if f in optionlist[option]: 
                ocrcur=ocr_core.ocr_extract(sfolder,f,[])
                ocrtxt=ocrcur[0]
                img_data=ocr_core.image_to_data(sfolder+'/'+f); imglen=len(img_data)
                iratio=len(img_data[img_data<5])/(imglen*len(img_data[0]))
                if iratio<0.02:
                    for p in range(-2,0):
                        pre=str(int(f[:-4])+p)+'.jpg'
                        ocrpre=ocr_core.ocr_extract(sfolder,pre,[])
                        ocrtxt=ocrtxt+" "+ocrpre[0]; 
                ocrlist=ocrtxt.split(); ocrdict[f]=ocrlist; #print(ocrlist)
                break
    
    fcount=0
    for opt in optdict:
        if opt not in fdict: fdict[opt]=[]
        optlen=len(opt.split())
        if fdict[opt].strip()!='': continue
        for f in ocrdict:
            ocrlist=ocrdict[f]
            sts=0
            
            for x in range(len(ocrlist)):
                nlist=ngram_map(ocrlist, 0, 1, optlen+1, [])
                if nlist!=[]:
                    #print(nlist)
                    for ntxt in nlist:
                        if sim(ntxt.lower(), opt.lower())>0.8:
                            for option in optionlist:
                                if f in optionlist[option]:
                                    fdict[opt]=option
                                    fcount=fcount+1
                                    sts=1; break
                        if sts==1: break
                if sts==1: break
    
    yesno=[]
    for opt in c2:
        if opt.strip()=="":continue
        a=opt.split('~')
        b=a[1].split(';')
        c=[s.strip() for s in b]
        if 'yes' in c or 'Yes' in c:
            yesno.append(a[0])

    if 'Low_confidence' not in fdict: 
        fdict['Low_confidence']=[]
    for opt in optdict:
        if fdict[opt]=='': 
            fdict['Low_confidence'].append(opt)
            if opt in yesno:
                fdict[opt]=decision
            if len(optdict[opt])==1:
                fdict[opt]=optdict[opt][0]
    return fdict    




                      
def c3_ocr_parser(fdict,optdict,ocrlist):
    
    usedcurrency=[]
    olen=len(ocrlist)
    for opt in optdict:
        #optlen=len(opt.split())
        if opt not in fdict: fdict[opt]=[]
        y=0

        for item in optdict[opt]:
            itemlen0=len(item[0].split())
            if item[0] in fdict[opt]: continue

            for x in range(y, olen):
                sts=0; nlist=[]
                    
                if ocrlist[x].lower() in postmark:
                    nlist=ngram_map(ocrlist, x, -1, itemlen0+1, [])
                   
                elif ocrlist[x].lower() in premark:
                    nlist=ngram_map(ocrlist, x, 1, itemlen0+1, [])
                
                if nlist!=[]:
                    #print(nlist)
                    for ntxt in nlist:
                        if sim(ntxt.lower(), item[0].lower())>=0.9:
                            #print(nlist, item[0], ocrlist[x], ocrlist[x-1])
                            fdict[opt].append(item[0])
                            usedcurrency.append(item[1])
                            y=x+1; sts=1; break
                if sts==1: break
    return fdict

    

def c3_icr_parser(fdict,optdict):
    
    pxdif=25 
    th=0.7
    limit=20 
    xratio=0.3 
    yratio=1-xratio
    bm=0.3
    
    flist={}; 
    clear_folder(approot+'snippets/match')
    
    mfolder=approot+'snippets/match'
    for sfolder in [approot+'snippets', approot+'snippets/market']:  
        for f in os.listdir(sfolder):
            img_path=sfolder+'/'+f
            if not os.path.exists(img_path): continue
            if f.endswith('.jpg'):
                mscore, window=icr_mscore(img_path, xmark, pxdif, th, limit, xratio, yratio)
                if mscore>bm and window.shape[0]>0:
                    flist[f]=mscore
                    ocr_core.data_to_image(window).save(mfolder+'/'+f+'_'+str(mscore)+'_.jpg')
           
    if flist!={}: print('xmax: ', max(flist), flist[max(flist)])
    print('files detected',flist); #return
    
    #getting OCR for detected files
    ocrdict={}
    for sfolder in [approot+'snippets', approot+'snippets/market']:
        for f in os.listdir(sfolder):
            if f not in flist: continue
            ocrsum=ocr_core.ocr_extract(sfolder,f,[])
            ocrtxt=ocrsum[0]; ocrlist=ocrtxt.split()
            ocrdict[f]=ocrlist; #print(ocrlist)
        
    usedcurrency=[]; fcount=0
    for opt in optdict:
        if opt not in fdict: fdict[opt]=[]
        
        for f in ocrdict:
            ocrlist=ocrdict[f]
            sts=0
            
            for item in optdict[opt]:
                if item[0] in fdict[opt]: continue
                #if item[1]=='HKD': print(ocrlist)
                for x in range(len(ocrlist)):
                    itemlen0=len(item[0].split())
                    nlist=ngram_map(ocrlist, 0, 1, itemlen0+1, [])
                    if nlist!=[]:
                        #if item[0]=='Australia':print(nlist)
                        for ntxt in nlist:
                            #if ntxt=='HKD': print(ntxt,item[1])
                            if sim(ntxt.lower(), item[0].lower())>0.8:
                                fdict[opt].append(item[0])
                                usedcurrency.append(item[1])
                                fcount=fcount+1
                                sts=1; break
                    if sts==1: break
                
    mcount=0
    for m in os.listdir(mfolder):
        if m.endswith('.jpg'): mcount=mcount+1

    if mcount>0 and fcount/mcount<0.5:
        if 'Low_confidence' not in fdict: 
            fdict['Low_confidence']=[]
        for opt in optdict:
            fdict['Low_confidence'].append(opt)
    return fdict    


    
def parse(inputfolder, inputfile):
    ocracc=[]
    ocrsts=0
    if ocrsts==1:
        do_clear(inputfolder)                    
        ocrsum=ocr_core.ocr_extract(inputfolder,inputfile,[]);
        ocrtxt=ocrsum[0]; ocracc=ocrsum[1]; #print(ocracc); return
        for m in miscase: ocrtxt=ocrtxt.replace(m,miscase[m])
        with open(approot+'ocrout.txt','w') as f: f.write(ocrtxt)
        read_image(inputfolder); #return
        print('ocr done'); #return
    
    ocrtxt=open(approot+'ocrout.txt','r').read(); #print(ocrtxt)
    ocrlist=ocrtxt.split(); olen=len(ocrlist); #print(ocrlist); return
    
    fdict={}; tdict={}

    for f in c1:
        if f.strip()=="":continue
        fl=f.split('~')
        fdict[fl[0].strip()]=""
        tdict[fl[0].strip()]=[]
        for t in fl[1].split(','):
            tdict[fl[0].strip()].append(t.strip())
    #print(tdict); return        

    print('c1 loading...')
    for f in fdict:
        flen=len(f.split())
        fv=tdict[f]
        for x in range(olen):
            rpos=-1
            nlist=ngram_map(ocrlist, x, 1, flen+1, [])
            if nlist!=[]:
                rpos, match=get_match_pos(x, nlist, f)
                if rpos!=-1:
                    matchlen=len(match.split())
                    y=rpos+matchlen; #print(match) 
                    while True:
                        if (y)>=olen: break
                        if exit_condition(ocrlist[y],y,fv)==1:break
                        fdict[f]=(fdict[f]+" "+ocrlist[y]).strip()
                        y=y+1
                    break    
    print('c1 ocr parsing completed')            
    #print(fdict); return
    

    optdict={}
    for opt in c2:
        if opt.strip()=="":continue
        a=opt.split('~')
        b=a[1].split(';')
        c=[s.strip() for s in b]
        optdict[a[0]]=c
        fdict[a[0]]=""
    #print(optdict);return

    
    #print(len(optdict))
    newdict={}
    for opt in optdict:
        print(opt)
        optlen=len(opt.split())
        sts=0
        for x in range(len(ocrlist)):
            nlist=ngram_map(ocrlist, x, 1, optlen+1, [])
            if nlist!=[]:
                for ntxt in nlist:
                    if abs(len(ntxt.split())-optlen)>1: continue
                    if lsim(ntxt.lower(), opt.lower())>0.5:
                        newdict[opt]=optdict[opt]
                        sts=1
                        x=x+optlen
                        break
            if sts==1: break
    optdict=newdict
    #print(len(optdict))

    print('c2 loading...')
    fdict=c2_ocr_parser(fdict,optdict,ocrlist); print('c2 ocr parsing completed')
    fdict=c2_icr_parser(fdict,optdict); print('c2 icr parsing completed')
    #print(fdict); return
        

    optdict={}
    for opt in c3:
        if opt.strip()=="":continue
        a=opt.split('~')
        b=a[1].split(';')
        c=[s.strip() for s in b]
        optdict[a[0]]=[]
        fdict[a[0]]=[]
        for d in c:
            e=d.split('=')
            optdict[a[0]].append(e)
    #print(optdict); return
    
    print('c3 loading...')
    fdict=c3_ocr_parser(fdict,optdict,ocrlist); print('c3 ocr parsing completed')
    fdict=c3_icr_parser(fdict,optdict); print('c3 icr parsing completed')
    
    fdict['ocr-summary']=ocracc
    print("")
    print("Output:")
    print("")
    for f in fdict: print(f,":",fdict[f])
    #return fdict

          
#parse('input','aodl.pdf')           