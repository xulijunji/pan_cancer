## A script for finding every cox coefficient and pvalue for every mRNA in BRCA Tier 3 data downloaded Feb. 2015


## Load necessary modules
from rpy2 import robjects as ro
import numpy as np
import os
ro.r('library(survival)')


##This call will only work if you are running python from the command line.
##If you are not running from the command line manually type in your paths.
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))



## There were three clinical files with nonredundant data.  V4.0 was found to be most up to date.
## V2.1 was more up to date than V1.5.   All three files are loaded with the more up to date file getting preference.


f=open(os.path.join(BASE_DIR,'tcga_data','BRCA','clinical','nationwidechildrens.org_clinical_follow_up_v4.0_brca.txt'))
f.readline()
f.readline()
f.readline()
data=[i.split('\t') for i in f]
## A patient can be listed multiple times in the file. The most recent listing (furthest down in the file), contains the most recent
## follow up data.  This code checks if the patient has already been loaded into the list, and if so, takes the more recent data.
## This required an empty value in the list initialization.
## Data is: [[Patient ID, time(days), Vital status],[Patient ID, time(days), Vital status],...]
clinical3=[['','','']]
for i in data:
    if clinical3[-1][0]==i[0]:
        if i[8]=='Alive':
            clinical3[-1]=[i[0],int(i[9]),'Alive']
        elif i[8]=='Dead':
            try:
                clinical3[-1]=[i[0],int(i[10]),'Dead']
            except:
                pass
        else:
            pass
    else:
        if i[8]=='Alive':
            clinical3.append([i[0],int(i[9]),'Alive'])
        elif i[8]=='Dead':
            try:
                clinical3.append([i[0],int(i[10]),'Dead'])
            except:
                pass
        else:
            pass


## Removing the empty value.
clinical=clinical3[1:]





f=open(os.path.join(BASE_DIR,'tcga_data','BRCA','clinical','nationwidechildrens.org_clinical_follow_up_v2.1_brca.txt'))
f.readline()
f.readline()
f.readline()
data=[i.split('\t') for i in f]
clinical1=[['','','']]
for i in data:
    if i[0] not in [j[0] for j in clinical]:
        if clinical1[-1][0]==i[0]:
            if i[6]=='Alive':
                clinical1[-1]=[i[0],int(i[7]),'Alive']
            elif i[6]=='Dead':
                try:
                    clinical1[-1]=[i[0],int(i[8]),'Dead']
                except:
                    pass
            else:
                pass
        else:
            if i[6]=='Alive':
                clinical1.append([i[0],int(i[7]),'Alive'])
            elif i[6]=='Dead':
                try:
                    clinical1.append([i[0],int(i[8]),'Dead'])
                except:
                    pass
            else:
                pass

##merging data and removing the empty value
clinical+=clinical1[1:]


f=open(os.path.join(BASE_DIR,'tcga_data','BRCA','clinical','nationwidechildrens.org_clinical_follow_up_v1.5_brca.txt'))
f.readline()
f.readline()
f.readline()
data=[i.split('\t') for i in f]
clinical2=[['','','']]
for i in data:
    if i[0] not in [j[0] for j in clinical]:
        if clinical2[-1][0]==i[0]:
            try:
                if i[6]=='Alive':
                    clinical2[-1]=[i[0],int(i[7]),'Alive']
                elif i[6]=='Dead':
                    try:
                        clinical2[-1]=[i[0],int(i[8]),'Dead']
                    except:
                        pass
                else:
                    pass
            except:
                pass
        else:
            try:
                if i[6]=='Alive':
                    clinical2.append([i[0],int(i[7]),'Alive'])
                elif i[6]=='Dead':
                    try:
                        clinical2.append([i[0],int(i[8]),'Dead'])
                    except:
                        pass
                else:
                    pass
            except:
                pass


##merging data and removing the empty value
clinical+=clinical2[1:]



## Grade, sex, and age information were taken from the "clinical_patient" file.  A dictionary was created for sex and grade.
more_clinical={}
grade_dict={}
grade_dict['Infiltrating Ductal Carcinoma']=1
grade_dict['Metaplastic Carcinoma']=3
grade_dict['Mucinous Carcinoma']=4
grade_dict['Medullary Carcinoma']=5
grade_dict['Infiltrating Lobular Carcinoma']=6




sex_dict={}
sex_dict['MALE']=0
sex_dict['FEMALE']=1

## The "clinical_patient" file can also contain patients not listed in the follow_up files.
## In these cases the clinical data for these patients gets appended to a new clinical list.

f=open(os.path.join(BASE_DIR,'tcga_data','BRCA','clinical','nationwidechildrens.org_clinical_patient_brca.txt'))
f.readline()
f.readline()
f.readline()
data=[i.split('\t') for i in f]
clinical4=[]
for i in data:
    try:
        more_clinical[i[0]]=[grade_dict[i[-11]],sex_dict[i[6]],int(i[20])]
    except:
        pass
    if i[13]=='Alive':
        clinical4.append([i[0],int(i[14]),'Alive'])
    elif i[13]=='Dead':
        try:
            clinical4.append([i[0],int(i[15]),'Dead'])
        except:
            pass
    else:
        pass


new_clinical=[]

##It is possible that the clinical data in the clinical_patient file is more up to date than the follow_up files
##All the clinical data is merged checking which data is the most up to date

for i in clinical4:
    if i[0] not in [j[0] for j in clinical]:
        new_clinical.append(i)
    else:
        if i[1]<=clinical[[j[0] for j in clinical].index(i[0])][1]:
            new_clinical.append(clinical[[j[0] for j in clinical].index(i[0])])
        else:
            new_clinical.append(i)


##also do the reverse since clinical can contain patients not included in clinical4
for i in clinical:
    if i[0] not in [j[0] for j in new_clinical]:
        new_clinical.append(i)


## only patients who had a follow up time greater than 0 days are included in the analysis
clinical=[i for i in new_clinical if i[1]>0]

final_clinical=[]

## A new list containing both follow up times and grade, sex, and age is constructed.
## Only patients with grade, sex, and age information are included.
## Data is [[Patient ID, time (days), vital status, grade, sex, age at diagnosis],...]

for i in clinical:
    if i[0] in more_clinical:
        final_clinical.append(i+more_clinical[i[0]])



## Need to map the mRNA files to the correct patients
## The necessary information is included in the FILE_SAMPLE_MAP.txt file
f=open(os.path.join(BASE_DIR,'tcga_data','BRCA','FILE_SAMPLE_MAP.txt'))
f.readline()
data=[i.strip().split() for i in f if i!='\n']

## 01 indicates a primary tumor, and only primary tumors are included in this analysis
TCGA_to_mrna={}
for i in data:
    ## The normalized data files are used
    if 'genes.normalized_results' in i[0]:
        if i[1].split('-')[3][:-1]=='01':
            x=''.join([k+j for k,j in zip(['','-','-'],i[1].split('-')[:3])])
            TCGA_to_mrna[x]=TCGA_to_mrna.get(x,[])+[i[0]]



clinical_and_files=[]
## We only care about patients that contained complete clinical information
for i in final_clinical:
    if TCGA_to_mrna.has_key(i[0]):
        ## The mRNA files are added to the clinical list
        ## Data structure: [[Patient ID, time (days), vital status, grade, sex, age at diagnosis,[mRNA files]],...]
        clinical_and_files.append(i+[TCGA_to_mrna[i[0]]])
    else:
        pass



## A list of lists of genes is constructed, the order of gene lists is same as the clinical_and_files data
## Data structure: [[genes for patient 1], [genes for patient 2], ....]
genes=[]
for i in clinical_and_files:
    temp=[]
    for j in i[-1]:
        f=open(os.path.join(BASE_DIR,'tcga_data','BRCA','mrna',j))
        f.readline()
        temp.append([[i.split('|')[1].split()[0],float(i.strip().split()[-1])] for i in f])
    ## In the case that the patient only contained 1 primary tumor mRNA file.
    if len(temp)==1:
        genes.append(temp[0])
    ## If the patient contained more than 1 primary tumor mRNA file
    ## this list comprehension will average the files for any number of files.
    else:
        values=[]
        for k in temp:
            values.append([kk[1] for kk in k])
        genes.append(zip([z[0] for z in temp[0]],list(sum([np.array(kkk) for kkk in values])/float(len(temp)))))




## Only want genes that meet an expression cutoff
## A cutoff of 1 RSEM and no more than a fourth of the patients containing no expression was chosen
final_genes=[[]]*len(genes)
for i in range(len(genes[0])):
    temp=[]
    for j in genes:
        temp.append(j[i])
    count=0
    for k in temp:
        if k[1]==0:
            count+=1
    median=np.median([ii[1] for ii in temp])
    if count<len(genes)/4 and median>1:
        for index, kk in enumerate(temp):
            final_genes[index]=final_genes[index]+[kk]


## This will write the final genes to a large (100-300 MB file) which could be useful for further analyses, this step can be skipped.
##f=open(os.path.join(BASE_DIR,'cox_regression','BRCA','final_genes.txt'),'w')
##for i in final_genes:
##    f.write(str(i))
##    f.write('\n')
##f.close()

##Performing Cox regression on all of the genes in final_genes

death_dic={}
death_dic['Alive']=0
death_dic['Dead']=1



coeffs=[]
pvalues=[]
genes=[]  ##This list tracks the gene names
for i in range(len(final_genes[0])):
    kaplan=[]
    genes.append(final_genes[0][i][0])
    for k,j in zip(clinical_and_files,final_genes):  ## These lists contain the clinical information and mRNA data in the same order.
        kaplan.append([k[1],k[2],k[3],k[4],k[5],j[i][1]])
    data=[ii[-1] for ii in kaplan]  ## Grabbing all the gene values for the current gene being analyzed
    ro.globalenv['expression']=ro.FloatVector(data)
    res=ro.r('round(qnorm((rank(expression, na.last="keep")-0.5)/sum(!is.na(expression))), digit=5)') ## Perform inverse normal transformation
    inverse_norm=list(res)  ## Convert robject to python list
    ## Prepare the variables for rpy2
    ro.globalenv['gene']=ro.FloatVector(inverse_norm)
    ro.globalenv['times']=ro.IntVector([ii[0] for ii in kaplan])
    ro.globalenv['died']=ro.IntVector([death_dic[ii[1]] for ii in kaplan])
            
    ##ductal
    ductal=[]
    for ii in kaplan:
        if ii[2]==1:
            ductal.append(1)
        else:
            ductal.append(0)
            
    ##metaplastic
    metaplastic=[]
    for ii in kaplan:
        if ii[2]==3:
            metaplastic.append(1)
        else:
            metaplastic.append(0)


    ##mucinous
    mucinous=[]
    for ii in kaplan:
        if ii[2]==4:
            mucinous.append(1)
        else:
            mucinous.append(0)


    ##medullary
    medullary=[]
    for ii in kaplan:
        if ii[2]==5:
            medullary.append(1)
        else:
            medullary.append(0)

    ##lobular
    lobular=[]
    for ii in kaplan:
        if ii[2]==6:
            lobular.append(1)
        else:
            lobular.append(0)


    
    ro.globalenv['ductal']=ro.IntVector(ductal)
    ro.globalenv['metaplastic']=ro.IntVector(metaplastic)
    ro.globalenv['mucinous']=ro.IntVector(mucinous)
    ro.globalenv['medullary']=ro.IntVector(medullary)
    ro.globalenv['lobular']=ro.IntVector(lobular)
    ro.globalenv['sex']=ro.IntVector([ii[3] for ii in kaplan])
    ro.globalenv['age']=ro.IntVector([ii[4] for ii in kaplan])
    res=ro.r('coxph(Surv(times,died) ~ gene + ductal + metaplastic + mucinous + medullary + lobular + sex + age)') ## Perform Cox regression
    ## Parse the string of the result with python for the gene coefficient and pvalue
    for entry in str(res).split('\n'):
        try:
            if entry.split()[0]=='gene':
                coeff=entry.split()[1]
                pvalue=entry.split()[-1]
                break
        except:
            pass
    coeffs.append(coeff)
    pvalues.append(pvalue)


## This will write the results to a tab delimited file with gene name, cox coefficient, and pvalue.
f=open(os.path.join(BASE_DIR,'cox_regression','BRCA','coeffs_pvalues.txt'),'w')
for i,j,k in zip(genes,coeffs,pvalues):
    f.write(i)
    f.write('\t')
    f.write(j)
    f.write('\t')
    f.write(k)
    f.write('\n')
f.close()



