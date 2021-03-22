from TBXTools import *
from os import path
import io

def termex(corpus, lang_in):
    
    with io.open(corpus,'w',encoding='utf8') as f:      
        f.write(corpus)
    
    print ("File exists:"+str(path.exists('stop-esp.txt')))
    print ("File exists:" + str(path.exists('exclusion-regexps.txt'))) 
    sw_spanish="stop-esp.txt"
    sw_english="stop-eng.txt"
	
    inner_spanish="inner-stop-esp.txt"
    inner_english="inner-stop-eng.txt"
    if(lang_in=="es"):
        lang=lang_in+"p"
    elif(lang_in=="en"):
        lang=lang_in+"g"
    #print(lang)
    extractor=TBXTools()
    extractor.create_project("statistical8.sqlite",lang,overwrite=True)
    extractor.load_sl_corpus(corpus)
    extractor.ngram_calculation(nmin=1,nmax=3,minfreq=3)
    if(lang=="esp"):
        extractor.load_sl_stopwords(sw_spanish)
        extractor.load_sl_inner_stopwords(inner_spanish)
    elif(lang=="eng"):
        extractor.load_sl_stopwords(sw_english)
        extractor.load_sl_inner_stopwords(inner_english)


    extractor.statistical_term_extraction(minfreq=4)
	# aquí junta los términos que son iguales pero están en mayus y en minus
    extractor.case_normalization(verbose=True)
	# esto no sé muy bien lo que hace pero saca menos términos que si no se pone, lo cual es mejor, creo que quita basurilla
    extractor.nest_normalization(verbose=True)
    extractor.regexp_exclusion(verbose=True)
    extractor.load_sl_exclusion_regexps("exclusion-regexps.txt")
    extractor.regexp_exclusion(verbose=True)
	#para extraer unigramas, descomenta esto
	#extractor.select_unigrams("unigrams.txt",position=-1)
    out=extractor.save_term_candidates("estatutoterms2.txt")
    newout=[]
    for i in out:
        t=i.replace("\t", "-")
        newout.append(t)
    return(newout)