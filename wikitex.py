import os, sys
import numpy as np
import re
import tarfile
import urllib2
import pdb

#Note on itemizing:
#To avoid double nesting syntax for subitems (items within items)
#I use the outline package, instead of itemize
#syntax:
#\begin{outline}
#\1 Some text
#\2 Some text -> this will be a subitem of the first item
#\1 Some more text
#\end{outline}

#Note on tags:
#This scripts produces one tex file per wiki page (except for the tables that are contained in separate files)
#Different subsections of each page contain a tag at the beginning and the end of the section, that can be
#used to execute only a part of the tex file in latex.
#this is done with the help of the package catchfilebetweentags
#\usepackage{catchfilebetweentags}
#...
#\ExecuteMetaData[file.tex]{tag}
#where the contents of the external file is surrounded by the "tags":
#%<*tag>
# content
#%</tag>

def mode_page(in_dir, out_dir, files):
    

    for file in files:
        sec_name_0=file.replace(in_dir+'/','')
        sec_name_0='MODE_'+sec_name_0.replace('.txt','')
        f1=open(out_dir+sec_name_0+'.tex', 'w')
       
        with open(file) as f: lines = [line.rstrip('\n') for line in f]

        #Look for positions of ==== (start of sections)
        pos=np.array([-1])
        c1=0
        for line in lines:
            if '====' in line and '=====' not in line:
                pos=np.append(pos,c1)
            c1 +=1
        pos=np.delete(pos,0)
        
        #Find where to end the final section
        n=len(pos)
        c1=0
        for i in range(pos[n-1],len(lines)):
            line=lines[i]
            if '=====' in line:
                       pos=np.append(pos,c1+pos[n-1])
                       break
            c1 +=1
        if len(pos) == n: pos=np.append(pos,c1-1+pos[n-1]) #if there is no other section preceded by ===== after the current one            
        
        for j in range(len(pos)-1):
            #Extract the name of the section
            line=lines[pos[j]]
            tag=line.replace('====','')
            tag=tag.strip()
            if ' ' in tag: tag=tag.replace(' ','')

            #insert tag to start the subsection
            f1.write('%<*'+tag+'>'+"\n")
            
            #Write text into section latex form
            c1=0
            for i in range(pos[j]+1,pos[j+1]):
                line=lines[i]

                ##All lines that don't start with '  *' are not itemized
                if line[:3] != '  *':
                    f1.write(line+"\n")
                    if c1 != 0:
                         f1.write('\\end{outline}'+"\n")
                         c1=0

                else:
                ##Lines starting with '  *' are itemized
                    if c1 == 0: f1.write('\\begin{outline}'+"\n")
                       
                    if line[2] == '*':
                        f1.write('\\1'+"\n")
                        line=line.replace('*','')
                    ##Fix the template names          
                    txt = re.search(r"\|(\w+)\]", line)   #Search for any string between | and ]         
                    if txt:
                        txt=txt.group(1)
                        txt=txt.replace('_','\_')
                        f1.write(txt +"\n")
                    else:    
                        f1.write(line+"\n")
                    c1+=1  
           #insert tag to end the subsection
            f1.write('%</'+tag+'>'+"\n")
    
def template_page(in_dir, out_dir, files):
    
    for file in files:
        sec_name_0=file.replace(in_dir+'/','')
        sec_name_0='TEMPLATE_'+sec_name_0.replace('.txt','')
        f1=open(out_dir+sec_name_0+'.tex', 'w')
                
        with open(file) as f: lines = [line.rstrip('\n') for line in f]

        #Look for positions of ++++ (start of sections)
        pos=np.array([-1])
        c1=0
        for line in lines:
            if '++++' in line:
                pos=np.append(pos,c1)
            c1 +=1
        pos=np.delete(pos,0)
        for j in range(0,len(pos)-1,2):
            #Extract the name of the section
            line=lines[pos[j]+1]
            tag=line.replace('|','')
            tag=tag.strip()
            title=tag
            if ' ' in tag: tag=tag.replace(' ','')
          #  sec_name=sec_name_0+'_'+txt+'.tex'
          #  f1=open(out_dir+sec_name, 'w')
          #  print sec_name

          #insert tag at the start of the subsection
            f1.write('%<*'+tag+'>'+"\n")

            f1.write('\\underline{ '+title+'}'+"\n")
            
            #Write text into latex form
            c1=0
            c2=0
            for i in range(pos[j]+2,pos[j+1]):
                
                line=lines[i]
                ##Some Notes with wiki syntax **Notes:**
                if '**' in line: line=line.replace('**','')
                
                ##All lines that don't start with '  *' are not itemized
                if line[:3] != '  *' and line[:5] !='    *':
                    f1.write(line+"\n")
                    if c1 != 0: #this variable signals that new section of the text has started and we have to finish itemizing
                         f1.write('\\end{outline}'+"\n")
                         c1=0
                         c2=1 #signals that we already put "end itemize"

                else:
                ##Lines starting with '  *' are itemized
                
                    if c1 == 0:
                        f1.write('\\begin{outline}'+"\n")
                        c2=0
                    if line[2] == '*':
                        f1.write('\\1'+"\n")
                        line=line.replace('*','')
                    if line[4] == '*':
                        f1.write('\\2'+"\n")
                        line=line.replace('*','')
                    f1.write(line+"\n")
                    if i == pos[j+1]-1 and c2 == 0: f1.write('\\end{outline}'+"\n") #final end itemize
                    c1+=1  

            #insert tag to end the subsection
            f1.write('%</'+tag+'>'+"\n")
                           

def tables(in_dir,out_dir,files):

    ##Translate parameter tables from wiki to latex syntax for the template manual
    for file in files:
        sec_name=file.replace(in_dir+'/','')
        label=sec_name.replace('.txt','')
        template_name=label.replace('_','\_')
        template_name=template_name.upper()
        if 'ACQ' in template_name: template_name = template_name.replace('ACQ', 'ACQ'.lower())
        if 'OBS' in template_name: template_name = template_name.replace('OBS', 'OBS'.lower())
        sec_name='PARAMTABLE_'+sec_name.replace('.txt','.tex')
        f1=open(out_dir+sec_name, 'w')

        f1.write('\\begin{table*}[htbp]'+"\n")
        f1.write('\\label{tab:'+label+'}'+"\n")
        f1.write('\\caption{Parameters of '+template_name+'}'+"\n")
        f1.write('\\footnotesize'+"\n")
        f1.write('\\begin{tabular}{llll}'+"\n")
        f1.write('\\hline'+"\n")
        f1.write('\\multicolumn{4}{c}{\\bf{'+template_name+'}}\\\\'+"\n")
        f1.write('\\hline'+"\n")
        f1.write('Parameter & Hidden & Range (Default) & Label \\\\'+"\n")
        f1.write('\\hline'+"\n")
        
        with open(file) as f: lines = [line.rstrip('\n') for line in f]

        count=0
        for line in lines:
            if '===Parameters' in line: #Find where the table entry starts
                pos=count
              #  pdb.set_trace()
            count=count+1
      #  print sec_name, pos
        #Loop only for the lines below the table starting position
        for i in range(pos,count):
            line=lines[i]
            if 'HIERARCH ESO' in line: line = line.replace('HIERARCH ESO', '')
            if '|' in line:
                txt = re.split('[|]',line)
                        
                for j in range(0,len(txt)-1):
                    if '_' in txt[j]: 
                        tmp=txt[j].replace('_','\_')
                        txt[j]=tmp

                maxlen=30 #if the line is too long, split into several    
                if len(txt[3]) <= maxlen:
                    f1.write(txt[1] + ' & '+ txt[2] + ' & '+ txt[3]  + ' & '+ txt[4] + '\\\\'+"\n")
                else:
                    tmp=txt[3].rstrip()
                    txt[3]=tmp
                    a=len(txt[3])/maxlen
                    b=len(txt[3])%maxlen
                    
                    for k in range(a):    
                        tmp=txt[3]
                        tmp=tmp[k*maxlen:(k+1)*maxlen]
                        if k == 0: f1.write(txt[1] +  ' & '+ txt[2] + ' & '+ tmp  + ' & '+ txt[4] + '\\\\'+"\n")
                        else: f1.write( ' & '+ ' & '+ tmp  + ' & '+ '\\\\'+"\n")
                    if b !=0:
                        tmp=txt[3]
                        tmp=tmp[a*maxlen:len(txt[3])]
                        f1.write( ' & '+ ' & '+ tmp  + ' & '+ '\\\\'+"\n")
                                            
        f1.write('\\hline'+"\n")
        f1.write('\\end{tabular}'+"\n")        
        f1.write('\\end{table*}'+"\n")        
           


                  
def main():

    #Purpose: Convert the the metis wiki syntax to tex files
    #This is the main program, which calls three other functions:
    #mode_page -> Parses the first page on the wiki for each mode (linked from the CMD table)
    #template_page -> Parses the page of each observing or acquisition template
    #tables -> Creates tables for each template, to be included in the template manual

    
   # url='https://home.strw.leidenuniv.nl/~burtscher/metis_operations/'
   # u = urllib2.urlopen(url)
   # meta = u.info()
   # date=meta.getheaders("Date")
    
    tar = tarfile.open("metis_operations_2019-01-08T11_25_01.tar.gz", "r:gz")
    tar.extractall()

    in_dir="operations"
    out_dir='metis_template_manual/'+in_dir+"_tex/"
    out_dir_2='metis_operational_concepts/'+in_dir+"_tex/"
        
    if not os.path.exists(out_dir):
        os.makedirs(out_dir)
        
    if not os.path.exists(out_dir_2):
        os.makedirs(out_dir_2)

    ##main pages for each mode, output starts with MODE
    files = [os.path.join(in_dir, f) for f in os.listdir(in_dir) if f.endswith('.txt') and
             'discussion' not in f and (f.startswith('img') or f.startswith('ifu') or f.startswith('spec'))]
    mode_page(in_dir, out_dir, files)

    ##pages for each template, output starts with TEMPLATE
    files = [os.path.join(in_dir, f) for f in os.listdir(in_dir) if f.startswith('metis') and f.endswith('.txt')]
    template_page(in_dir, out_dir, files)
    
    ##create tables for template manual, output starts with PARAMTABLE
    files = [os.path.join(in_dir, f) for f in os.listdir(in_dir) if f.startswith('metis') and f.endswith('.txt')]
    tables(in_dir, out_dir, files)

    ##Copy
    os.system('cp -r '+ out_dir +' ' + out_dir_2)
    
if __name__ == "__main__":
    main()
