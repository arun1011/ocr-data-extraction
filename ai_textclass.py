import ast

def isnumericorfloat(txt):
    for s in range(len(txt)):
        val = 'n'        
        for n in range(10):
            if txt[s] in ['/','.']:val = 'y'
            if txt[s] == str(n):val = 'y'
        if val == 'n':break
    return val


def split_spl_chr(query):
    querylist=[]    
    querylist=query.strip( ).split(' ')
    tempquery=""
    for q in querylist:
        temp=""
        for p in q:
            if p.isdigit() or p.isalpha():
                temp=temp+p
            else:
                temp=temp+" "+p+" "
        tempquery=tempquery+" "+temp
    queryx=tempquery
    return queryx


def word_pattern(txt):
    converted_txt=""
    txt=txt.lower()
    for d in txt:
        if d==" ":
            converted_txt=converted_txt+" "
        elif d.isalpha():
            converted_txt=converted_txt+"a"
        elif d.isdigit():
            converted_txt=converted_txt+"n"
        else:
            converted_txt=converted_txt+"s"
    return converted_txt


def chr_type(chrx):
    if chrx.isalpha()==True:
        return 'a'
    elif chrx.isdigit()==True:
        return 'n'
    else:
        return 's'
        
def word_mix(txt):
    txt=txt.lower().strip()
    if len(txt)==1:
        return chr_type(txt)
    elif len(txt)>1:
        wm=[]
        wmix=""
        for t in txt:
            wm.append(chr_type(t))
        wm=sorted(set(wm))
        for w in wm:
            wmix=wmix+w
        return wmix

def sim(a,b):
    from difflib import SequenceMatcher
    sim_score = SequenceMatcher(None,a,b).ratio()
    return sim_score

    
def split_alpha_numeric(query):
    querylist=[]; #print(query)  
    querylist=query.strip( ).split(' '); #print(querylist)
    queryx = ""
    for x in range(len(querylist)):
        word = querylist[x]
        #alpha-numeric parsing to string & numeric
        tempword = word        
        for s in range(len(word)-1):
            chr1=word[s]
            chr2=word[s+1]
            val1 = isnumericorfloat(chr1)
            val2 = isnumericorfloat(chr2)
            if val1 != val2:
                tempword = tempword.replace(chr1+chr2,chr1+' '+chr2)
        word = tempword
        queryx = queryx+' '+word.strip( )
    return queryx


def ngram_map(txt_list,token_position,token_direction,token_size,break_list):
    #No case change
    ngram_list=[]; ngram=""
    if token_direction==1: s=0; e=token_size; 
    else: s=-token_size; e=0; 
    try:
        for c in range(s,e):
            val=token_position+c
            ngram=txt_list[val]
            if ngram.lower().strip() in break_list:break
            ngram_list.append(ngram.strip())
        l=len(ngram_list)
        
        y=1
        while y<=l:
            for n in range(l):
                c=0; ngram=""
                while c<=y:
                    if n+c==l:break
                    ngram=ngram+ngram_list[n+c]+" "    
                    c=c+1
                if ngram.strip() not in ngram_list:
                    ngram_list.append(ngram.strip())
            y=y+1
    except:
        y=0
    return ngram_list   
    

def ngram_check(ngram):
    cdict={'a':0, 'n':0, 's':0}
    for n in ngram.split():
        if word_mix(n)=='a':cdict['a']=cdict['a']+1
        if word_mix(n)=='n':cdict['n']=cdict['n']+1
        if word_mix(n)=='s':cdict['s']=cdict['s']+1
    return cdict
    
    
def count_spl_chr(ngram):
    conj_b=['/','-','.',',']; spl=[]
    for i in ngram:
        if i in conj_b and i not in spl: spl.append(i)
    return len(spl)
    
    
def alpha_condition(ngram,excep_list):
    for word in ngram.split():
        if word.isalpha() and word.lower() not in excep_list:
            if len(word)<3 or len(word)>9: return 0
    return 1
    
    
def word2list_sim(word,wlist):
    pos=-1
    for w in wlist:
        pos=pos+len(w)
        if sim(word.lower(),w.lower())>0.85: return [1, pos]
    return [0, pos]
    

def list2list_sim(alist,blist):
    t=len(blist); n=0
    if t==0: return 0
    for b in blist:
        b=b.lower()
        for a in alist:
            a=a.lower()
            if a[:2]==b[:2] and a[-2:]==b[-2:]:
                n=n+1; break
    return n/t
    

def rep_txt(txt,starttxt,endtxt,reptxt):
    startpos=0
    while startpos>=0:
        startpos=txt.find(starttxt)
        endpos=txt.find(endtxt)
        substr=txt[startpos:endpos+len(endtxt)]
        txt=txt.replace(substr,reptxt)
    return txt
    
    
def clean_txt(txt):
    txt_list=txt.split()   
    tem_txt=""
    for x in range(len(txt_list)):
        c=txt_list[x]; e=0
        if word_mix(c) in ['s']: e=1
        if c in ['¼']: e=0; c='1/4'
        if c in ['½']: e=0; c='1/2'
        if c in ['¾']: e=0; c='3/4'
        if e==0: tem_txt=tem_txt+" "+c
    return tem_txt.strip()
    
    
def target_pattern(txt):
    p=''
    last_p=''
    for x in txt:
        if x.isdigit() and last_p!='n':
            p=p+'n'; last_p='n'; continue
        if x=='x' and last_p!='x':
            p=p+'x'; last_p='x'; continue
        if x.isalpha() and last_p!='a':
            p=p+'a'; last_p='a'; continue
    return p

    
def remove_accents(input_str):
    import unicodedata
    nfkd_form = unicodedata.normalize('NFKD', input_str)
    only_ascii = nfkd_form.encode('ASCII', 'ignore')
    return only_ascii.decode('ascii')  



def list2text(input_list,addchr):
    temp_text=""
    for word in input_list:
        temp_text=temp_text+word+addchr
    return temp_text.strip()
                
    
def trim_list(source,target):
    for s in source:
        if s.lower() in target:
            source.remove(s)
    return source
   
    
def alpha_list(source):
    for s in source:
        if not s.isalpha():
            source.remove(s)
    return source

    
def manage_space(txt):
    txt=txt.replace(" ","<->")
    txt_list=txt.split("<->")
    temp_list=[]
    for word in txt_list:
        if word !='':
            temp_list.append(word)
    newtxt=list2text(temp_list," ")
    return newtxt
    
    
def manage_sequence(txt, target_list):
    txt_list=txt.split()
    for w in range(len(txt_list)):
        if w==0:continue
        if w==len(txt_list)-1:break
        word=txt_list[w]; pre_word=txt_list[w-1]; nxt_word=txt_list[w+1]
        if word.lower() in target_list:
            if pre_word.isdigit() and nxt_word.isdigit():repstr=" "+word+" "
            if pre_word.isdigit() and not nxt_word.isdigit():repstr=" "+word
            if not pre_word.isdigit() and nxt_word.isdigit():repstr=word+" "
            if not pre_word.isdigit() and not nxt_word.isdigit():repstr=word
            txt=txt.replace(repstr,word.lower())
    txt_list=txt.split()
    for w in range(len(txt_list)):
        if w==len(txt_list)-1:break
        word=txt_list[w]
        for target in target_list:
            if target in word.lower():
                txt=txt.replace(word,word.lower())
    return txt
    
    
def tag_txt(txt):
    #quest; greet; bad; good; accept; reject; urgent; stmt
    txt=split_spl_chr(txt)
    
    tag_dict1=ast.literal_eval(open('b_tags1.txt','r').read())
    for tag_name in tag_dict1:
        for item in tag_dict1[tag_name]:
            if txt.lower().split()[0]==item: return tag_name

    tag_dict2=ast.literal_eval(open('b_tags2.txt','r').read())
    for tag_name in tag_dict2:
        for item in tag_dict2[tag_name]:
            if item in txt.lower().split(): return tag_name
        
    return 'stmt'