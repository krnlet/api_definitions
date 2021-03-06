import os
import json
import csv
import re
import requests
import spacy
import nltk
from nltk.parse import CoreNLPParser
from nltk.corpus import stopwords
from nltk.stem import PorterStemmer
stemmer = PorterStemmer()
from time import time
nlp = spacy.load('es_core_news_sm')
#import #conts_log


# 0 clean punctuation and stopwords
def clean_terms(termlist):
    start_time=time()
    stop=stopwords.words('spanish')
    file=open('../data/stop-esp.txt', 'r', encoding='utf-8')
    mystop=file.readlines()

    filew=open('../data/stop-esp_all.txt', 'w', encoding='utf-8')
    
    clean_list = []
    cont=0
    for i in mystop:
        stop.append(i.strip())

    for i in stop:
    	filew.write(i+'\n')
    deletes=[]
    for i in termlist:
        k=i.strip(',.:')
        if ((k.lower() in stop) or (k in stop)):
        	deletes.append(k)
        elif ((k.lower() not in stop) or (k not in stop)):
            clean_list.append(k.replace(',', '').replace('-', ''))
       

    cont=len(termlist)-len(clean_list)
    elapsed_time=time()-start_time

    txt='CLEAN_TERMS, DELETE ('+str(cont)+') NEW LIST SIZE: ('+str(len(clean_list))+') TIME: ('+str(elapsed_time)+')'
    joind=', '.join(deletes)
    #conts_log.information(txt, 'TERMS REMOVED: '+joind)
    print('CLEAN_TERMS, DELETE', cont, len(clean_list), elapsed_time )
    
    
    return(clean_list)


# 1 añotador
def annotate_timex(text, date, lang):
    start_time=time()
    url = 'https://annotador.oeg.fi.upm.es/annotate' 
    params = {'inputText':text, 'inputDate':"", 'domain': "standard", 'lan': lang}
    response=requests.post(url, data=params)
    print(response)
    textanotador=response.text
    print(textanotador)
    code=response.status_code
    list_anotador=textanotador.split('|')
    deletes=[]
    cont=0
    for i in list_anotador:
        if('<' in i ):
            cont=cont+1
            deletes.append(i)
            ind=list_anotador.index(i)
            list_anotador.pop(ind)
    for i in list_anotador:
        if('<' in i ):
            cont=cont+1
            deletes.append(i)
            ind=list_anotador.index(i)
            list_anotador.pop(ind)
    
    
    anotador=[]
    for i in list_anotador:
        anotador.append(i.strip().replace(',', ''))
    
    for i in deletes:
        ind=i.index('>')
        ind1=i.index('</')
        term=i[ind+1:ind1]
        ind2=deletes.index(i)
        deletes[ind2]=term

    if(code!=200):
	    print('WARNING: Annotador is down. Temporal expressions could not be removed.' )
	    anotador=text.split('| ')
	    #conts_log.error('Annotador is down. Temporal expressions could not be removed.', code)
    else:
	    elapsed_time=time()-start_time
	    txt='AÑOTADOR, DELETE ('+str(cont)+') NEW LIST SIZE: ('+str(len(anotador))+') TIME: ('+str(elapsed_time)+')'
	    joind=', '.join(deletes)
	    print('AÑOTADOR DELETE', cont, len(anotador), elapsed_time )
	    #conts_log.information(txt, 'TERMS REMOVED: '+joind)
    
    return(anotador)





def infinitive(verb):
	
	if(verb[-2:]=='ar' or verb[-2:]=='er' or verb[-2:]=='ir'):
		verb=verb
	else:
		if(verb[-2:]=='rá' ):
			#print('---',verb,'-',verb[:-1])
			verb=verb[:-1]
		if(verb[-2:]=='án'):
			#print('---',verb,'-',verb[:-2])
			verb=verb[:-2]
		if(verb[-2:]=='ré'):
			#print('---',verb,'-',verb[:-1])
			verb=verb[:-1]
	return (verb)


# 2 patrones
def delate_pattern_2(anotador):
	total=0
	deletes=[]
	start_time=time()
	lemmas_list=[]
	cont=0
	cont_inf=0
	cont_post=0
	for i in anotador:
		#print( i, i.split(' ') )
		#pos_tagger = CoreNLPParser('http://localhost:9003', tagtype='pos')
		#https://corenlp.run/
		#https://corenlp-tool.lynx-project.eu/
		pos_tagger = CoreNLPParser('https://corenlp.run/', tagtype='pos')
		tag=pos_tagger.tag(i.split(' '))
		total=total+1
		joini=i
		list_pos=[]
		spl=joini.split(' ')
		if(joini!=''):
			join_tag=''
			for t in tag:
				if(t[1] == 'AUX' ):
					doc=nlp(t[0])
					lemlist=[tok.lemma_ for tok in doc]
					lem=''.join(lemlist)
					lemmas_list.append(lem)
					if(lem==i):
						lem=t[0]
					list_pos.append('aux--'+str(lem))
					if(len(spl)==1):
						ind=anotador.index(str(i))
						anotador[ind]=str(lem)
				if(t[1] ==  'NOUN'):
					list_pos.append('noun-'+str(t[0]))
				if(t[1] ==  'VERB'):
					cont_inf=cont_inf+1
					doc=nlp(t[0])
					for tok in doc:
						l=tok.lemma_
						if(l!=t[0]):
							cont_post=cont_post+1
					lemlist=[tok.lemma_ for tok in doc]
					lem=''.join(lemlist)
					lemmas_list.append(lem)
					if(lem==i):
						lem=t[0]
					list_pos.append('verb-'+str(lem))
					if(len(spl)==1):
						ind=anotador.index(str(i))
						anotador[ind]=str(lem)
				if(t[1] ==  'ADV'):
					list_pos.append('adv--'+str(t[0]))
				if(t[1] ==  'ADJ'):
					list_pos.append('adj--'+str(t[0]))
				if(t[1] ==  'SCONJ'):
					list_pos.append('sconj'+str(t[0]))
			
			spl_i=joini.split(' ')
			
			if(len(list_pos)==1):
				pos1=list_pos[0]
				if(pos1[0:4]=='adv-' ):
					term=pos1[5:]
					deletes.append(joini)
					ind=anotador.index(joini)
					#anotador.pop(ind)
					cont=cont+1

			elif(len(list_pos)==2 and len(spl_i)==2):
				pos1=list_pos[0]
				pos2=list_pos[1]
				term=''
				if(pos1[0:4]=='aux-' and pos2[0:4]=='verb'):
					term=pos1[5:]+' '+pos2[5:]
					deletes.append(joini)
					ind=anotador.index(joini)
					#anotador.pop(ind)
					cont=cont+1
				if(pos1[0:4]=='verb' and pos2[0:4]=='aux-'):
					term=pos1[5:]+' '+pos2[5:]
					deletes.append(joini)
					ind=anotador.index(joini)
					#anotador.pop(ind)
					cont=cont+1
				if(pos1[0:4]=='verb' and pos2[0:4]=='verb'):
					term=pos1[5:]+' '+pos2[5:]
					deletes.append(joini)
					ind=anotador.index(joini)
					#anotador.pop(ind)
					cont=cont+1
				if(pos1[0:4]=='noun' and pos2[0:4]=='verb'):
					term=pos1[5:]+' '+pos2[5:]
					deletes.append(joini)
					ind=anotador.index(joini)
					#anotador.pop(ind)
					cont=cont+1
				if(pos1[0:4]=='noun' and pos2[0:4]=='aux-'):
					term=pos1[5:]+' '+pos2[5:]
					deletes.append(joini)
					ind=anotador.index(joini)
					#anotador.pop(ind)
					cont=cont+1
				if(pos1[0:4]=='adv-' and pos2[0:4]=='adj-'):
					term=pos1[5:]+' '+pos2[5:]
					deletes.append(joini)
					ind=anotador.index(joini)
					#anotador.pop(ind)
					cont=cont+1
				if(pos1[0:4]=='adj-' and pos2[0:4]=='adv-'):
					term=pos1[5:]+' '+pos2[5:]
					deletes.append(joini)
					ind=anotador.index(joini)
					#anotador.pop(ind)
					cont=cont+1
				if(pos1[0:4]=='adv-' and pos2[0:4]=='aux-'):
					term=pos1[5:]+' '+pos2[5:]
					deletes.append(joini)
					ind=anotador.index(joini)
					#anotador.pop(ind)
					cont=cont+1
				if(pos1[0:4]=='aux-' and pos2[0:4]=='adv-'):
					term=pos1[5:]+' '+pos2[5:]
					deletes.append(joini)
					ind=anotador.index(joini)
					#anotador.pop(ind)
					cont=cont+1
				if(pos1[0:4]=='adv-' and pos2[0:4]=='verb'):
					term=pos1[5:]+' '+pos2[5:]
					deletes.append(joini)
					ind=anotador.index(joini)
					#anotador.pop(ind)
					cont=cont+1
				if(pos1[0:4]=='verb' and pos2[0:4]=='aux-'):
					term=pos1[5:]+' '+pos2[5:]
					deletes.append(joini)
					ind=anotador.index(joini)
					#anotador.pop(ind)
					cont=cont+1
				if(pos1[0:4]=='noun' and pos2[0:4]=='adv-'):
					term=pos1[5:]+' '+pos2[5:]
					deletes.append(joini)
					ind=anotador.index(joini)
					#anotador.pop(ind)
					cont=cont+1
				if(pos1[0:4]=='adv-' and pos2[0:4]=='noun'):
					term=pos1[5:]+' '+pos2[5:]
					deletes.append(joini)
					ind=anotador.index(joini)
					#anotador.pop(ind)
					cont=cont+1
				if(pos1[0:4]=='verb' and pos2[0:4]=='adv-'):
					term=pos1[5:]+' '+pos2[5:]
					deletes.append(joini)
					ind=anotador.index(joini)
					#anotador.pop(ind)
					cont=cont+1
				if(pos1[0:4]=='verb' and pos2[0:4]=='noun'):
					term=pos1[5:]+' '+pos2[5:]
					deletes.append(joini)
					ind=anotador.index(joini)
					#anotador.pop(ind)
					cont=cont+1
				if(pos1[0:4]=='aux-' and pos2[0:4]=='noun'):
					term=pos1[5:]+' '+pos2[5:]
					deletes.append(joini)
					ind=anotador.index(joini)
					#anotador.pop(ind)
					cont=cont+1
				if(pos1[0:4]=='adj-' and pos2[0:4]=='noun'):
					term=pos1[5:]+' '+pos2[5:]
					deletes.append(joini)
					ind=anotador.index(joini)
					#anotador.pop(ind)
					cont=cont+1

			elif(len(list_pos)==3 and len(spl_i)==3):
				#print(list_pos, spl_i,'-', len(list_pos), len(spl_i))
				pos1=list_pos[0]
				pos2=list_pos[1]
				pos3=list_pos[2]
				term=''
				if(pos1[0:4]=='noun' and pos2[0:4]=='verb' and pos3[0:4]=='verb'):
					term=pos1[5:]+' '+pos2[5:]+' '+pos3[5:]
					deletes.append(joini)
					ind=anotador.index(joini)
					#anotador.pop(ind)
					cont=cont+1
				if(pos1[0:4]=='noun' and pos2[0:4]=='aux-' and pos3[0:4]=='verb'):
					term=pos1[5:]+' '+pos2[5:]+' '+pos3[5:]
					deletes.append(joini)
					ind=anotador.index(joini)
					#anotador.pop(ind)
					cont=cont+1
				if(pos1[0:4]=='noun' and pos2[0:4]=='aux-' and pos3[0:4]=='aux-'):
					term=pos1[5:]+' '+pos2[5:]+' '+pos3[5:]
					deletes.append(joini)
					ind=anotador.index(joini)
					#anotador.pop(ind)
					cont=cont+1
				if(pos1[0:4]=='noun' and pos2[0:4]=='verb' and pos3[0:4]=='aux-'):
					term=pos1[5:]+' '+pos2[5:]+' '+pos3[5:]
					deletes.append(joini)
					ind=anotador.index(joini)
					#anotador.pop(ind)
					cont=cont+1
				
				if(pos1[0:4]=='noun' and pos2[0:4]=='verb' and pos3[0:4]=='noun'):
					term=pos1[5:]+' '+pos2[5:]+' '+pos3[5:]
					deletes.append(joini)
					ind=anotador.index(joini)
					#anotador.pop(ind)
					cont=cont+1
				if(pos1[0:4]=='noun' and pos2[0:4]=='aux-' and pos3[0:4]=='noun'):
					term=pos1[5:]+' '+pos2[5:]+' '+pos3[5:]
					deletes.append(joini)
					ind=anotador.index(joini)
					#anotador.pop(ind)
					cont=cont+1
				if(pos1[0:4]=='verb' and pos2[0:4]=='noun' and pos3[0:4]=='noun'):
					term=pos1[5:]+' '+pos2[5:]+' '+pos3[5:]
					deletes.append(joini)
					ind=anotador.index(joini)
					#anotador.pop(ind)
					cont=cont+1
				if(pos1[0:4]=='noun' and pos2[0:4]=='noun' and pos3[0:4]=='verb'):
					term=pos1[5:]+' '+pos2[5:]+' '+pos3[5:]
					deletes.append(joini)
					ind=anotador.index(joini)
					#anotador.pop(ind)
					cont=cont+1
				if(pos1[0:4]=='aux-' and pos2[0:4]=='noun' and pos3[0:4]=='noun'):
					term=pos1[5:]+' '+pos2[5:]+' '+pos3[5:]
					deletes.append(joini)
					ind=anotador.index(joini)
					#anotador.pop(ind)
					cont=cont+1
				if(pos1[0:4]=='noun' and pos2[0:4]=='noun' and pos3[0:4]=='aux-'):
					term=pos1[5:]+' '+pos2[5:]+' '+pos3[5:]
					deletes.append(joini)
					ind=anotador.index(joini)
					#anotador.pop(ind)
					cont=cont+1
				if(pos1[0:4]=='aux-' and pos2[0:4]=='verb' and pos3[0:4]=='noun'):
					term=pos1[5:]+' '+pos2[5:]+' '+pos3[5:]
					deletes.append(joini)
					ind=anotador.index(joini)
					#anotador.pop(ind)
					cont=cont+1
				if(pos1[0:4]=='noun' and pos2[0:4]=='verb' and pos3[0:4]=='adj-'):
					term=pos1[5:]+' '+pos2[5:]+' '+pos3[5:]
					deletes.append(joini)
					ind=anotador.index(joini)
					#anotador.pop(ind)
					cont=cont+1
				if(pos1[0:4]=='noun' and pos2[0:4]=='verb' and pos3[0:4]=='noun' and joini in anotador):
					term=pos1[5:]+' '+pos2[5:]+' '+pos3[5:]
					deletes.append(joini)
					ind=anotador.index(joini)
					#anotador.pop(ind)
					cont=cont+1
				if(pos1[0:4]=='verb' and pos2[0:4]=='noun' and pos3[0:4]=='adj-' and joini in anotador):
					term=pos1[5:]+' '+pos2[5:]+' '+pos3[5:]
					deletes.append(joini)
					ind=anotador.index(joini)
					#anotador.pop(ind)
					cont=cont+1
				if(pos1[0:4]=='noun' and pos2[0:4]=='aux-' and pos3[0:4]=='adj-' and joini in anotador):
					term=pos1[5:]+' '+pos2[5:]+' '+pos3[5:]
					deletes.append(joini)
					ind=anotador.index(joini)
					#anotador.pop(ind)
					cont=cont+1
				if(pos1[0:4]=='noun' and pos2[0:4]=='adv-' and pos3[0:4]=='adj-' and joini in anotador):
					term=pos1[5:]+' '+pos2[5:]+' '+pos3[5:]
					deletes.append(joini)
					ind=anotador.index(joini)
					#anotador.pop(ind)
					cont=cont+1
				if(pos1[0:4]=='adj-' and pos2[0:4]=='adv-' and pos3[0:4]=='adj-' and joini in anotador):
					term=pos1[5:]+' '+pos2[5:]+' '+pos3[5:]
					deletes.append(joini)
					ind=anotador.index(joini)
					#anotador.pop(ind)
					cont=cont+1
				if(pos1[0:4]=='noun' and pos2[0:4]=='adv-' and pos3[0:4]=='scon' and joini in anotador):
					term=pos1[5:]+' '+pos2[5:]+' '+pos3[5:]
					deletes.append(joini)
					ind=anotador.index(joini)
					#anotador.pop(ind)
					cont=cont+1
				if(pos1[0:4]=='adj-' and pos2[0:4]=='scon' and pos3[0:4]=='adv-' and joini in anotador):
					term=pos1[5:]+' '+pos2[5:]+' '+pos3[5:]
					deletes.append(joini)
					ind=anotador.index(joini)
					#anotador.pop(ind)
					cont=cont+1
				if(pos1[0:4]=='aux-' and pos2[0:4]=='noun' and pos3[0:4]=='adj-' and joini in anotador):
					term=pos1[5:]+' '+pos2[5:]+' '+pos3[5:]
					deletes.append(joini)
					ind=anotador.index(joini)
					#anotador.pop(ind)
					cont=cont+1
				if(pos1[0:4]=='verb' and pos2[0:4]=='verb' and pos3[0:4]=='verb' and joini in anotador):
					term=pos1[5:]+' '+pos2[5:]+' '+pos3[5:]
					deletes.append(joini)
					ind=anotador.index(joini)
					#anotador.pop(ind)
					cont=cont+1
				if(pos1[0:4]=='adj-' and pos2[0:4]=='noun' and pos3[0:4]=='adj-' and joini in anotador):
					term=pos1[5:]+' '+pos2[5:]+' '+pos3[5:]
					deletes.append(joini)
					ind=anotador.index(joini)
					#anotador.pop(ind)
					cont=cont+1

	for i in deletes:
		if(i in anotador):
			ind=anotador.index(i)
			anotador.pop(ind)
			
	
	elapsed_time=time()-start_time
	txt='PATRONES, DELETE'+' ('+str(cont)+') NEW LIST SIZE: ('+str(len(anotador))+') TIME: ('+str(elapsed_time)+')'
	joind=', '.join(deletes)
	print('PATRONES DELETE', cont, len(anotador), elapsed_time)
	#conts_log.information(txt, 'TERMS REMOVED: '+joind)
	return(anotador)


# 3 plurales
def quit_plural(valuelist):
	start_time=time()
	file=open('../data/numberlist_es', 'r', encoding='utf-8')
	read=file.readlines()
	plural=[]
	cont=0
	for i in valuelist:
		ind=valuelist.index(i)
		term=i.replace(',', '').replace('-', ' ')
		valuelist[ind]=term
		plu=''
		if('es' in term[-2:] or 's'  in term[-1:]):
			slp=term.split(' ')

			for n in read:
				if(n[:-1] in slp):
					plu=i

			if not len(plu):
				for j in slp:
					if( ('es' in j[-2:] ) and 't' not in j[-3:-2] and 'l' not in j[-3:-2] or  ('les' in j[-3:] )   ):
						plu+=' '+j[:-2]
						
						if('on' in plu[-2:]):
							plu=' '+plu[:-2]+'ón'
						if('v' in plu[-1:]):
							plu=' '+plu+'e'
						if('bl' in plu[-2:]):
							plu=' '+plu+'e'
						if('br' in plu[-2:]):
							plu=' '+plu+'e'

					elif(('s' in j[-1:]) ):
						plu+=' '+j[:-1]
						pos=slp.index(j)
						
						if(pos>0):
							bef=slp[0]
							if('n' in bef[-1:] and 'ón' not in bef[-2:]):
								
								splb=plu.split(' ')
								
								firts=splb[1]
								
								if('n' not in firts[-1:]):
									pass
								else:
									plu0=firts[:-1]
									join1=' '.join(splb[2:])
									
									plu=plu0+' '+join1
								
							

					else:
						plu+=' '+j

			ind=valuelist.index(term)
			valuelist[ind]=plu.strip()			
			cont=cont+1
	quit_plu=[]
	nuevalista=set(valuelist)
	for i in nuevalista:
		quit_plu.append(i)	

	deletes = []
	new=[]
	for i in valuelist:
	    if i not in new:
	        new.append(i)
	    else:
	    	deletes.append(i)

	elapsed_time=time()-start_time
	txt='PLURAL, DELETE'+' ('+str(len(valuelist)-len(quit_plu))+') NEW LIST SIZE: ('+str(len(quit_plu))+') TIME: ('+str(elapsed_time)+')'
	joind=', '.join(deletes)
	print('PLURALES DELETE', len(valuelist)-len(quit_plu), len(quit_plu), elapsed_time)
	#conts_log.information(txt, 'TERMS REMOVED: '+joind)
	return(quit_plu)

# 4 numeros
def delete_numbers(list_):
	start_time=time()
	file=open('../data/numberlist_es', 'r', encoding='utf-8')
	read=file.readlines()
	cont=0
	deletes=[]
	for i in read:
		if(i[-1:]=='\n'):
			i=i[:-1]
			for j in list_:
				if(' '+i+' ' in ' '+j+' ' ):
					deletes.append(j)
					ind=list_.index(j)
					cont=cont+1
					list_.pop(ind)
	list_.sort()
	elapsed_time=time()-start_time
	txt='NUMBERS, DELETE'+' ('+str(cont)+') NEW LIST SIZE: ('+str(len(list_))+') TIME: ('+str(elapsed_time)+')'
	joind=', '.join(deletes)
	print('NUMEROS DELETE', cont, len(list_), elapsed_time)
	#conts_log.information(txt, 'TERMS REMOVED: '+joind)
	return(list_)


# 5 leer archivo 
def readFile(read):
	start_time=time()
	text=''
	for i in read:
		if(i[-1:]=='\n'):
			spl=i[:-1].split('\t')
		else:
			spl=i.split('\t')
		term=spl[1].replace('-', '').replace(',', '').replace(';', '')
		spl2=term.split(' ')
		text+='| '+spl[1]
	elapsed_time=time()-start_time
	return text

#elimina tildes
def quit_tilds(s):
    replacements = (
        ("á", "a"),
        ("é", "e"),
        ("í", "i"),
        ("ó", "o"),
        ("ú", "u"),
    )
    for a, b in replacements:
        s = s.replace(a, b)
    return s

def acentos(last):
	start_time=time()
	til=[]
	list_acentos=[]
	for i in last:
		acento=re.search("[áéíóúÁÉÍÓÚ]+", i)
		if(acento!=None):
			sin=quit_tilds(i)
			list_acentos.append(i)
			til.append(sin)
		else:
			til.append(i)

	til2 = []
	delete=[]
	for i in til:
		if i not in til2:
			til2.append(i)
		else:
			delete.append(i)

	indices=[]
	delete2=[]
	for i in last:
		if(i in delete and i not in indices):
			indices.append(i)
			delete2.append(i)
	for i in delete2:
		ind=last.index(i)
		last.pop(ind)

	last.sort()
	elapsed_time=time()-start_time
	
	return(last)


#-------MAIN-------#
def main(read):
	start_time=time()
	text=read
	date='2020-06-03'
	lang='ES'
	clean_text=clean_terms(text)
	join_clean_text='| '.join(clean_text).replace('-', '').replace(',', '').replace(';', '')
	#print(join_clean_text)
	#anotador=annotate_timex(join_clean_text, date, lang)
	#anotador.sort()
	pattern=delate_pattern_2(clean_text)
	plural=quit_plural(pattern)
	numbers=delete_numbers(plural)
	tildes=acentos(numbers)
	stop2=clean_terms(tildes)
	new=open('clean_terms_freq4.txt', 'w')#se imprime lo que se queda

	for i in stop2:
	    new.write(i+'\n')
	new.close()
	elapsed_time=time()-start_time
	return(stop2)


#file=open('../data/estatuto_es.txt', 'r', encoding='utf-8')
#read=file.readlines()
#main(read)

