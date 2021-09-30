import subprocess
from nltk.tokenize import sent_tokenize
from time import time
import os
import argparse
import json
import csv
import re
import spacy
import nltk
from nltk import ngrams
from nltk.parse import CoreNLPParser
from nltk.corpus import stopwords
from nltk.stem import PorterStemmer
import tbx
import postprocess
stemmer = PorterStemmer()
nlp = spacy.load('es_core_news_sm')


def convertirTxt(fol):
    raiz = os.getcwd()
    folder = os.listdir(raiz+'/'+fol)
    # print(raiz)
    for i in folder:
        # print(i)
        var = "pdf2txt.py -o "+raiz+"/"+fol+"/txt/" + \
            i[:-4]+'.txt'+" "+raiz+"/"+fol+"/"+i+""
        # print(var)
        subprocess.Popen(var, shell=True)

def extraction(document, lang):
    list_terms=tbx.termex(document, lang)
    terms=list()
    for item in list_terms:
        spl=item.split('-')
        term=spl[1].strip(',.:')
        terms.append(term)
        
    return terms

def clean(terms):
    listclean=postprocess.main(terms)
    return(listclean)

def extraction_patrons(document, terms):
    #https://corenlp-tool.lynx-project.eu/
    pos_tagger = CoreNLPParser('https://corenlp.run/', tagtype='pos')
    sentence = document.split('.')
    jsondefs=dict({'definitions':[]})
    lemma_terms=list()
    lemma_doc=list()
    tokensdoc=list()
    tokensterms=list()
    for t in terms:
        analize = nlp(t)
        lemlist = [tok.lemma_ for tok in analize]
        tokensterms = [tok.text for tok in analize]
        lemma_terms.append(' '.join(lemlist))

    for i in range(len(sentence)):
        number_of_sentence = i
        phrase = str()
        phrase2 = str()
        phrase += sentence[i]+'.'
        analize = nlp(phrase)
        lemlist = [tok.lemma_ for tok in analize]
        lemma_doc.append(' '.join(lemlist))

    #print(lemma_doc)
    file_extract=open('definitions_with_tbx.txt', 'w')
    for lem in range(len(lemma_doc)):
        sentence_lem=lemma_doc[lem]
        analize=nlp(sentence_lem)
        tokensdoc = [tok.text for tok in analize]
        if('considerar' in tokensdoc):
            index=tokensdoc.index('considerar')
            #print(tokensdoc[index-3:index], '-', tokensdoc[index:index+3])
            for i in terms:
                splterm=i.split(' ')
                lenterm=len(splterm)
                joi=' '.join(tokensdoc[index+1:index+lenterm+1])
                joi=' '+joi+' '
                if(i in tokensdoc[index+1:index+lenterm+1]):
                    print(i, '-',sentence[lem])
                    file_extract.write(i+'-->'+sentence[lem]+'\n')
        
       
        
def withterms(document, terms):
    sentence = document.split('.')
    filewithterms=open('withterms_copula+term_sobrantes.txt', 'w')
    pos_tagger = CoreNLPParser('https://corenlp.run/', tagtype='pos')
    
    words=list()
    sizes=list()
    for num in range(len(sentence)):
        sent=sentence[num]+'.'
        words.append([])
        sizes.append([])
        for term in terms:
            term=' '+term[:-1]+' '
            if(term in sent):
                
                position=sent.index(term)
                front=sent[position+len(term):]
                back=sent[:position]
                analize = nlp(sent)
                sentlema = [tok.lemma_ for tok in analize]
                tokens = [tok.text for tok in analize]

                analizef = nlp(front)
                sentlemaf = [tok.lemma_ for tok in analizef]
                tokensf = [tok.text for tok in analizef]
                analizeb = nlp(back)
                sentlemab = [tok.lemma_ for tok in analizeb]
                tokensb = [tok.text for tok in analizeb]
                if('comité de empresa es el' in sent):
                    print(term)
                
                #considerar: 
                #cuando encuentra un termino busca tres antes si esta "considerar" si es asi
                if('considerar' in sentlemab[len(sentlemab)-3:]):
                    poscopula=sentlema.index('considerar')
                    sub=sentlemaf[1:4]
                    joi=' '.join(sub)
                    doc = nlp(joi)
                    tokens1 = [tok.text for tok in doc]
                    tagger = pos_tagger.tag(tokens1)
                    tag=str()
                    for t in tagger:
                        tag+=' '+t[1]
                    #condicion 1 para considerar
                    #compula+termino+ ADP+NOUN+VERB toma el termino mas dos palbaras delante
                    #(PARA CORREGIR; TRABAJADOR Y ES TRABAJADOR A TURNOS, ETC...)
                    if(tag==' ADP NOUN VERB' or tag==' ADP NOUN PRON'):
                        term=term+' '+' '.join(tokensf[1:3])
                        sizes[num].append(len(term))
                        words[num].append(term+ '-->'+ sent.strip())
                    #se considera + termino +
                    elif('se' in tokens[poscopula-1]):
                        a= nlp(term)
                        s = [tok.lemma_ for tok in a]
                        tokterm = [tok.text for tok in a]
                        jt=sentlema[poscopula+1:poscopula+1+len(tokterm)-1]
                        
                        sub=sentlema[poscopula+1:poscopula+2]
                       
                        joi=' '.join(sub)
                        doc = nlp(joi)
                        tokens1 = [tok.text for tok in doc]
                        tagger = pos_tagger.tag(tokens1)
                        tag=str()
                        for t in tagger:
                            tag+=' '+t[1]
                        

                        if(jt==s[1:]):
                            sizes[num].append(len(term))
                            words[num].append(term+ '-->'+ sent.strip())
                        
                        elif('como' in tokens[poscopula+1]):
                            jt=sentlema[poscopula+2:poscopula+1+len(s)]
                            if(jt==s[1:]):
                                sizes[num].append(len(term))
                                words[num].append(term+ '-->'+ sent.strip()) 
                        elif(' DET' in tag):
                            sizes[num].append(len(term))
                            words[num].append(term+ '-->'+ sent.strip()) 
                            
                    
                
                if('haber' in sentlemab[len(sentlemab)-3:]):
                    poscopula=sentlema.index('haber')
                    print(sentlemab[len(sentlemab)-3:], term, sentlemaf[0:2])
                    if('cuando' in sentlemaf[1]):
                        sizes[num].append(len(term))
                        words[num].append(term+ '-->'+ sent.strip())
                    elif('siempre' in sentlemaf[1] and 'que' in sentlemaf[2]):
                        sizes[num].append(len(term))
                        words[num].append(term+ '-->'+ sent.strip())
                    elif('si' in sentlemaf[1] or 'Si' in sentlemaf[1]):
                        sizes[num].append(len(term))
                        words[num].append(term+ '-->'+ sent.strip())
                
                if('existir' in sentlemab[len(sentlemab)-3:]):
                    #print(sentlemab, term, sentlemaf[0:2])
                    if('cuando' in sentlemaf[1]):
                        sizes[num].append(len(term))
                        words[num].append(term+ '-->'+ sent.strip())
                    elif('siempre' in sentlemaf[1] and 'que' in sentlemaf[2]):
                        sizes[num].append(len(term))
                        words[num].append(term+ '-->'+ sent.strip())
                    elif('si' in sentlemaf[1] or 'Si' in sentlemaf[1]):
                        sizes[num].append(len(term))
                        words[num].append(term+ '-->'+ sent.strip())
                
                if('ser' in sentlemab[len(sentlemab)-1:] or 'es' in sentlemab[len(sentlemab)-1:]):
                    poscopula=sentlema.index('ser')
                    #ser+tambien+term
                    
                    if(tokens[poscopula+1]=='tambien'):
                        a= nlp(term)
                        s = [tok.lemma_ for tok in a]
                        tokterm = [tok.text for tok in a]
                        jt=' '.join(tokens[poscopula+2:poscopula+2+len(tokterm)-1])
                        
                        if(jt==term):
                            sizes[num].append(len(term))
                            words[num].append(term+ '-->'+ sent.strip())
                    else:
                        a= nlp(term)
                        s = [tok.lemma_ for tok in a]
                        tokterm = [tok.text for tok in a]
                        #det atras
                        sub1=sentlema[poscopula-1:poscopula]
                        joi1=' '.join(sub1)
                        doc1= nlp(joi1)
                        tokens1= [tok.text for tok in doc1]
                        tagger1= pos_tagger.tag(tokens1)
                        tag1=str()
                        for t in tagger1:
                            tag1+=' '+t[1]
                        if(' DET' in tag1 ):
                            sub2=sentlemaf[0:1]
                            joi2=' '.join(sub2)
                            doc2= nlp(joi2)
                            tokens2= [tok.text for tok in doc2]
                            tagger2= pos_tagger.tag(tokens2)
                            tag2=str()
                            for t in tagger2:
                                tag2+=' '+t[1]
                            if(' DET' in tag2):
                                sizes[num].append(len(term))
                                words[num].append(term+ '-->'+ sent.strip())
                        else:
                            #print(num, tag1,  term, tokens[poscopula-1:] )
                            if('como' in tokens[poscopula-1:poscopula+5]):
                                posc=tokens.index('como')
                                term=' '.join(tokens[poscopula+1:posc])+' '+' '.join(tokens[posc+1:posc+1+len(tokterm)])
                                sizes[num].append(len(term))
                                words[num].append(term+ '-->'+ sent.strip())
                                
                        
               
                   
                #DEFINIR: SOLO CONSIDERE EL PATRON DEFINIR COMO PARA ELIMINAR TODA LA BASURA +se
                if(('definir' in sentlemab[len(sentlemab)-3:]) and 'como' in sentlemab[len(sentlemab)-1] ):
                    poscopula=sentlema.index('definir')
                    if('se' in sentlema[poscopula-1]):
                        a= nlp(term)
                        s = [tok.lemma_ for tok in a]
                        tokterm = [tok.text for tok in a]
                        if(sentlema[poscopula+1:poscopula+1+len(tokterm)]==s):
                            sizes[num].append(len(term))
                            words[num].append(term+ '-->'+ sent.strip())
                    else:
                        sizes[num].append(len(term))
                        words[num].append(term+ '-->'+ sent.strip())

                #ENTENDER: REVISE EL ESTATUTO Y NO HABIA ENTNTER COMO NI ENTENDER POR +se
                if(('enteder' in sentlemab[len(sentlemab)-3:] ) ):
                    poscopula=sentlema.index('entender')
                    sub=sentlemaf[1:4]
                    joi=' '.join(sub)
                    doc = nlp(joi)
                    tokens = [tok.text for tok in doc]
                    if('se' in sentlema[poscopula-1] and 'que' in sentlema[poscopula+1]):
                        a= nlp(term)
                        s = [tok.lemma_ for tok in a]
                        tokterm = [tok.text for tok in a]
                        if(sentlema[poscopula+1:poscopula+1+len(tokterm)]==s):
                            sizes[num].append(len(term))
                            words[num].append(term+ '-->'+ sent.strip())

                    tagger = pos_tagger.tag(tokens)
                    tag=str()
                    for t in tagger:
                        tag+=' '+t[1]
                    #LA MISMA REGLA DE CONSIDERAR PERO CON ADP+NOUN+VERB Y ADP+NOUN+PRON
                    if(tag==' ADP NOUN VERB' or tag==' ADP NOUN PRON'):
                        term=term+' '+' '.join(tokensf[1:3])
                        sizes[num].append(len(term))
                        words[num].append(term+ '-->'+ sent.strip())
                    else:
                        sizes[num].append(len(term))
                        words[num].append(term+ '-->'+ sent.strip())
                #DENOMINAR SOLO ES DENOMINAR+TERMINO
                elif( ('denominar' in sentlemab[len(sentlemab)-3:] ) ):
                    sizes[num].append(len(term))
                    words[num].append(term+ '-->'+ sent.strip())
                #DETERMINAL+TERMINO    
                elif( ('determinar' in sentlemab[len(sentlemab)-3:] )):
                    sub=sentlemab[len(sentlemab)-3:]
                    pos=sub.index('determinar')
                    if(len(sub)>pos+1):
                        doc = nlp(sub[pos+1])
                        tokens = [tok.text for tok in doc]
                        tagger = pos_tagger.tag(tokens)
                        
                        for t in tagger:
                            tag=t[1]
                        #SI DESPUES DEL DETEMINAR HAY UN DET NO LO COGE  
                        if(tag!='DET'):
                            sizes[num].append(len(term))
                            words[num].append(term+ '-->'+ sent.strip())

                    
                

    for s in range(len(sizes)):
        if(len(sizes[s])>0):
            max_item = max(sizes[s], key=int)
            ind=sizes[s].index(max_item)
            #print(term, '-->', sent.strip() )
            filewithterms.write(words[s][ind] +'\n') 
            #print(w)

def withterms2(document, terms):
    filewithterms=open('withterms_term+copula.txt', 'w')
    sentence = document.split('.')
    pos_tagger = CoreNLPParser('https://corenlp.run/', tagtype='pos')
    
    words=list()
    sizes=list()
    for num in range(len(sentence)):
        sent=sentence[num]+'.'
        words.append([])
        sizes.append([])
        for term in terms:
            term=term[:-1]
        
            if(' '+term+' ' in sent):
                
                position=sent.index(term)
                front=sent[position+len(term):]
                back=sent[:position]
                analize = nlp(sent)
                sentlema = [tok.lemma_ for tok in analize]
                tokens = [tok.text for tok in analize]
                
                analizef = nlp(front)
                sentlemaf = [tok.lemma_ for tok in analizef]
                tokensf = [tok.text for tok in analizef]
                analizeb = nlp(back)
                sentlemab = [tok.lemma_ for tok in analizeb]
                tokensb = [tok.text for tok in analizeb]
                #if(term=='contrato de trabajo'):
                #    print(term, sent)
                #PARA EL CASO DE TERMINO+COPULA SOLO BUSCA 3 TOKENS DESPUES DEL TERMINO SI HAY UNA COPULA SI ES ASI TOMA EL TERMINO QUE ESTE
                if(('considerar' in sentlemaf[:6])) :
                    poscopula=sentlemaf.index('considerar')
                    #print(term, sentlemaf[:6], sentlemaf[poscopula-1], sentlemaf[poscopula+1], tokensf[poscopula+1])
                    doc = nlp(sentlemaf[poscopula+1])
                    tokens = [tok.text for tok in doc]
                    tagger = pos_tagger.tag(tokens)
                    tag=str()
                    for t in tagger:
                        tag=t[1]
                    if(tag=='ADJ' and tokensf[poscopula+2]=='cuando'):
                        term=term+' '+tokensf[poscopula+1]
                        
                        sizes[num].append(len(term))
                        words[num].append(term+ '-->'+ sent.strip())
                    elif(tokensf[poscopula+1]=='como'):
                        term=term+' '.join(sentlemaf[:poscopula])
                        if(poscopula+8>len(sentlemaf)):
                            if(tokensf[poscopula]=='considerará' and ',' in sentlemaf[poscopula:poscopula+8]):
                                term=' '.join(tokensf[poscopula+2:poscopula+7])
                                
                                sizes[num].append(len(term))
                                words[num].append(term+ '-->'+ sent.strip())
                   
                elif(('definir' in sentlemaf[:3])) :
                    pass
                    #print(num, term, sentlemaf[:3])
                    #sizes[num].append(len(term))
                    #words[num].append(term+ '-->'+ sent.strip())
                    
                elif(('enteder' in sentlemaf[:3]) or ('entederá' in sentlemaf[:3]) ) :
                    print(num, term, sentlemaf[:3])
                    sizes[num].append(len(term))
                    words[num].append(term+ '-->'+ sent.strip())
                    
                elif( ('denominar' in sentlemaf[:3]) ) :
                    sizes[num].append(len(term))
                    words[num].append(term+ '-->'+ sent.strip())
                    
                    '''elif( ('determinar' in sentlemaf[:3]) ):
                    sizes[num].append(len(term))
                    words[num].append(term+ '-->'+ sent.strip())'''
                elif('ser' in sentlemaf[1] ):
                    #print(sentlemab[len(sentlemab)-1], term, sentlemaf)
                    a= nlp(term)
                    s = [tok.lemma_ for tok in a]
                    tokterm = [tok.text for tok in a]
                    #det atras
                    sub1=sentlemab[len(sentlemab)-1]
                    joi1=' '.join(sub1)
                    doc1= nlp(joi1)
                    tokens1= [tok.text for tok in doc1]
                    tagger1= pos_tagger.tag(tokens1)
                    tag1=str()
                    for t in tagger1:
                        tag1=' '+t[1]
                    #print(sub1, tag1)
                    if(' PROPN' in tag1 ):
                        #print(term,'--', tokens)
                        sub2=sentlemaf[2]
                        joi2=''.join(sub2)
                        doc2= nlp(joi2)
                        #print(doc2)
                        tokens2= [tok.text for tok in doc2]
                        tagger2= pos_tagger.tag(tokens2)
                        tag2=str()
                        for t in tagger2:
                            tag2+=' '+t[1]
                        #print(tag2)
                        if(' DET' in tag2):
                            print(term)
                            sizes[num].append(len(term))
                            words[num].append(term+ '-->'+ sent.strip())
                    else:
                        pass
                        #print(num, tag1,  term, tokens[poscopula-1:] )
                        ''' if('como' in tokens[poscopula-1:poscopula+5]):
                            posc=tokens.index('como')
                            term=' '.join(tokens[poscopula+1:posc])+' '+' '.join(tokens[posc+1:posc+1+len(tokterm)])
                            sizes[num].append(len(term))
                            words[num].append(term+ '-->'+ sent.strip())'''

   
                

    for s in range(len(sizes)):
        if(len(sizes[s])>0):
            max_item = max(sizes[s], key=int)
            ind=sizes[s].index(max_item)
        
            filewithterms.write(words[s][ind] +'\n') 
            #print(w)



def copula_funct(document):
    lab = document
    list_definitions = list()
    definiendums = list()
    pos_tagger = CoreNLPParser('https://corenlp.run/', tagtype='pos')
    #pos_tagger = CoreNLPParser('https://corenlp-tool.lynx-project.eu/', tagtype='pos')
            
    # sentence=sent_tokenize(document)
    sentence = document.split('.')
    #print(sentence)

    number_of_defs = int()
    sentence2 = lab.split('.')
    both = list()
    jsondefs=dict({'definitions':[]})

    filedef = open('definitions.txt', 'w')
    patronsfile = open('listpatrons.txt', 'w')
    labels = open('definitions_labels.txt', 'w')
    considerar_file = open('considerar.txt', 'w')
    entender_file = open('entender.txt', 'w')
    denominar_file = open('denominar.txt', 'w')
    ser_file = open('ser.txt', 'w')
    deber_file = open('deber.txt', 'w')
    dospuntos_file = open('dospuntos.txt', 'w')
    new = list()
    patterns_c = list()
    patterns_e = list()
    patterns_d = list()
    patterns_s = list()
    patterns_de = list()
    patterns_p = list()
    phrase3 = str()
    for i in range(len(sentence)):
        number_of_sentence = i
        phrase = str()
        phrase2 = str()
        phrase += sentence[i]+'.'
        phrase2 += sentence2[i]+'.'
        pattern = list()
        patter1 = str()
        postaglist = list()
        wordlist = list()
        patternback = list()
        postaglistback = list()
        wordlistback = list()
        doc = nlp(phrase)
        lemlist = [tok.lemma_ for tok in doc]
        tokens = [tok.text for tok in doc]

        # print(tokens)
        tag = pos_tagger.tag(tokens)
        #print(tag)
        for t in tag:
            pattern.append(t)
            postaglist.append(t[1])
            wordlist.append(t[0])
        joinpos = ' '.join(postaglist)
        joinword = ' '.join(wordlist)
     

        if('considerar' in lemlist):
            #print('considerar')
            cont = lemlist.count('considerar')
            poscopula = lemlist.index('considerar')
            copula = tokens[poscopula]
            posfront = postaglist[poscopula:poscopula+6]
            wordfront = wordlist[poscopula:poscopula+6]
            posback = postaglist[:poscopula]
            wordback = wordlist[:poscopula]
            definiendum = str()
            definien = str()

            listdef = list()
            if(len(definiendum) == 0 and cont < 2):
                band = 0
                if('án' in copula[-2:] or 'an' in copula[-2:]):
                    patrons = [
                        'NOUN ADJ PRON',
                        'DET DET NOUN',
                        'ADJ ADP NOUN',
                        'ADJ ADP NOUN',
                        'NOUN ADJ PUNCT',
                        'NOUN ADV ADJ',
                        'NOUN PUNCT',
                    ]
                    correctpatron=list()
                    for patron in range(len(patrons)):
                        if(band == 0):
                            patron = patrons[patron].split(' ')
                            patron_tag = ' '.join(posfront[:len(patron)])
                            patron_word = ' '.join(wordfront[:len(patron)])
                            listtag=posfront[:len(patron)]
                            listword=wordfront[:len(patron)]
                            if(patron_tag in patrons):
                                band = 1
                                number_of_defs = number_of_defs+1
                                #print('original: ',listtag)
                                if(listtag[0] == 'DET'):
                                    listword.pop(0)
                                    listtag.pop(0)
                                elif(listtag[len(listtag)-1] == 'PRON' or listtag[len(listtag)-1] == 'PUNCT' or listtag[len(listtag)-1] == 'ADP'):
                                    listword.pop(len(listword)-1)
                                    listtag.pop(len(listtag)-1)
                                definiendum = ' '.join(listword)
                                correctpatron=' '.join(listtag)
                                definien = ''.join(phrase)
                    #print(definiendum,'- considerarán',correctpatron)
                    if(len(definiendum) > 0):
                        joinpatron=' '.join(correctpatron)
                        filedef.write('\n-'+definiendum+':'+definien)
                        html = '<span style="background-color: #FDD2C4">'+definien+'</span>'
                        phrase = phrase.replace(definien, html)
                        html = '<a class="over" style="color: #D6400F"><B>'+definiendum + \
                            '</B><span class="tooltip" > '+copula+': '+joinpatron+'</span></a>'
                        phrase = phrase.replace(definiendum, html)
                        jsondefs['definitions'].append({definiendum:definien})
                        patronsfile.write(copula+':->'+joinpatron+'::futuro '+'\n')

                elif('á' in copula[-1:] or 'a' in copula[-1:]):
                    patrons = [
                        'NOUN ADP NOUN',
                        'DET NOUN ADP',
                        'NOUN ADP NOUN',
                        'ADP NOUN ADJ',
                        'VERB DET NOUN',
                        'NOUN DET',
                        'NOUN ADJ',
                        'ADJ NOUN',
                        'VERB ADV',

                    ]
                    for patron in range(len(patrons)):
                        if(band == 0):
                            patron = patrons[patron].split(' ')
                            patron_tag = ' '.join(posfront[:len(patron)])
                            patron_word = ' '.join(wordfront[:len(patron)])
                            listtag=posfront[:len(patron)]
                            listword=wordfront[:len(patron)]
                            if(patron_tag in patrons):
                                band = 1
                                number_of_defs = number_of_defs+1
                                #print('original: ',listtag)
                                if(listtag[0] == 'DET'):
                                    listword.pop(0)
                                    listtag.pop(0)
                                elif(listtag[len(listtag)-1] == 'DET' or listtag[len(listtag)-1] == 'ADP'):
                                    listword.pop(len(listword)-1)
                                    listtag.pop(len(listtag)-1)

                                definiendum = ' '.join(listword)
                                correctpatron=' '.join(listtag)
                                definien = ''.join(phrase)
                                
                    #print(definiendum,'-considerará',correctpatron)
                    if(len(definiendum) > 0):
                        joinpatron=' '.join(correctpatron)
                        filedef.write('\n-'+definiendum+':'+definien)
                        html = '<span style="background-color: #FDD2C4">'+definien+'</span>'
                        phrase = phrase.replace(definien, html)
                        html = '<a class="over" style="color: #D6400F"><B>'+definiendum + \
                            '</B><span class="tooltip" > '+copula+': '+joinpatron+'</span></a>'
                        phrase = phrase.replace(definiendum, html)
                        jsondefs['definitions'].append({definiendum:definien})
                        patronsfile.write(copula+':->'+joinpatron+'::futuro '+'\n')

                elif('do' in copula[-2:]):
                    patrons = [
                        'ADP DET NOUN',

                    ]
                    for patron in range(len(patrons)):
                        if(band == 0):
                            patron = patrons[patron].split(' ')
                            patron_tag = ' '.join(posfront[:len(patron)])
                            patron_word = ' '.join(wordfront[:len(patron)])
                            listtag=posfront[:len(patron)]
                            listword=wordfront[:len(patron)]
                            if(patron_tag in patrons):
                                band = 1
                                number_of_defs = number_of_defs+1
                                definiendum = ' '.join(listword)
                                correctpatron=' '.join(listtag)
                                definien = ''.join(phrase)
                    #print(definiendum,'-considerado',correctpatron)


                    if(len(definiendum) > 0):
                        joinpatron=' '.join(correctpatron)
                        filedef.write('\n-'+definiendum+':'+definien)
                        html = '<span style="background-color: #FDD2C4">'+definien+'</span>'
                        phrase = phrase.replace(definien, html)
                        html = '<a class="over" style="color: #D6400F"><B>'+definiendum + \
                            '</B><span class="tooltip" > '+copula+': '+joinpatron+'</span></a>'
                        phrase = phrase.replace(definiendum, html)
                        jsondefs['definitions'].append({definiendum:definien})
                        patronsfile.write(copula+':->'+joinpatron+'::presente '+'\n')
            #print('--------1', phrase)
            phrase3 += phrase
        elif('entender' in lemlist):
            cont = lemlist.count('entender')
            poscopula = lemlist.index('entender')
            copula = tokens[poscopula]
            posfront = postaglist[poscopula:poscopula+6]
            wordfront = wordlist[poscopula:poscopula+6]
            posback = postaglist[:poscopula]
            wordback = wordlist[:poscopula]
            definiendum = str()
            definien = str()

            listdef = list()
            if(len(definiendum) == 0 and cont < 2):
                band = 0
                patrons = [
                    'ADP PUNCT NOUN ADP NOUN VERB PUNCT',
                    'SCONJ VERB NOUN ADP DET NOUN',
                    'SCONJ PRON VERB ADP DET NOUN',
                    'VERB ADP DET NOUN ADJ',
                    'SCONJ DET NOUN AUX ADJ',
                    'ADV ADJ DET NOUN ADJ',
                    'ADJ ADP NOUN ADJ',
                    'ADJ CONJ ADP NOUN',
                    'SCONJ VERB NOUN ADJ',
                    'ADP NOUN ADP NOUN',
                    'ADP NOUN ADJ',
                    'ADJ ADV',

                ]
                for patron in range(len(patrons)):
                    if(band == 0):
                        patron = patrons[patron].split(' ')
                        patron_tag = ' '.join(posfront[:len(patron)])
                        patron_word = ' '.join(wordfront[:len(patron)])
                        listtag=posfront[:len(patron)]
                        listword=wordfront[:len(patron)]
                        if(patron_tag in patrons):
                            band = 1
                            number_of_defs = number_of_defs+1
                            #print('original: ',listtag)
                            if(listtag[0] == 'ADP' or listtag[0] == 'SCONJ'):
                                listword.pop(0)
                                listtag.pop(0)
                            definiendum = ' '.join(listword)
                            correctpatron=' '.join(listtag)
                            definien = ''.join(phrase)
                #print(definiendum,'-entender',correctpatron)
                
                if(len(definiendum) > 0):
                    joinpatron=' '.join(correctpatron)
                    filedef.write('\n-'+definiendum+':'+definien)
                    html = '<span style="background-color: #FDD2C4">'+definien+'</span>'
                    phrase = phrase.replace(definien, html)
                    html = '<a class="over" style="color: #D6400F"><B>'+definiendum + \
                        '</B><span class="tooltip" > '+copula+': '+joinpatron+'</span></a>'
                    phrase = phrase.replace(definiendum, html)
                    jsondefs['definitions'].append({definiendum:definien})
                    patronsfile.write(copula+':->'+joinpatron+'::n')
            #print('--------2', phrase)
            phrase3 += phrase
        elif('denominar' in lemlist):
            cont = lemlist.count('denominar')
            poscopula = lemlist.index('denominar')
            copula = tokens[poscopula]
            posfront = postaglist[poscopula:poscopula+6]
            wordfront = wordlist[poscopula:poscopula+6]
            posback = postaglist[:poscopula]
            wordback = wordlist[:poscopula]
            definiendum = str()
            definien = str()

            listdef = list()
            if(len(definiendum) == 0 and cont < 2):
                band = 0
                patrons = [
                    'ADJ NOUN CONJ NOUN',
                    'ADJ PROPN ADP PROPN'
                ]
                for patron in range(len(patrons)):
                    if(band == 0):
                        patron = patrons[patron].split(' ')
                        patron_tag = ' '.join(posfront[:len(patron)])
                        patron_word = ' '.join(wordfront[:len(patron)])
                        listtag=posfront[:len(patron)]
                        listword=wordfront[:len(patron)]
                        #print('original: ',listtag)
                        if(patron_tag in patrons):
                            band = 1
                            number_of_defs = number_of_defs+1
                            if(listtag[0] == 'ADJ'):
                                listtag.pop(0)
                                listword.pop(0)
                            definiendum = ' '.join(listword)
                            correctpatron=' '.join(listtag)
                            definien = ''.join(phrase)
                #print(definiendum,'-denominar',correctpatron)
                if(len(definiendum) > 0):
                    joinpatron=' '.join(correctpatron)
                    filedef.write('\n-'+definiendum+':'+definien)
                    html = '<span style="background-color: #FDD2C4">'+definien+'</span>'
                    phrase = phrase.replace(definien, html)
                    html = '<a class="over" style="color: #D6400F"><B>'+definiendum + \
                        '</B><span class="tooltip" > '+copula+': '+joinpatron+'</span></a>'
                    phrase = phrase.replace(definiendum, html)
                    jsondefs['definitions'].append({definiendum:definien})
                    patronsfile.write(copula+':->'+joinpatron+'::n')
            #print('--------3', phrase)
            phrase3 += phrase
        elif('deber' in lemlist):
            cont = lemlist.count('deber')
            poscopula = lemlist.index('deber')
            copula = tokens[poscopula]
            posfront = postaglist[poscopula:poscopula+6]
            wordfront = wordlist[poscopula:poscopula+6]
            posback = postaglist[poscopula-6:poscopula]
            wordback = wordlist[poscopula-6:poscopula]
            definiendum = str()
            definien = str()
            listdef = list()
            # print(copula)
            if(len(definiendum) == 0 and cont < 2):
                band = 0
                if('án' in copula[-2:] or 'an' in copula[-2:] or 'á' in copula[-2:]):
                    patrons = [
                        'NOUN ADP DET NOUN CONJ NOUN',
                        'NOUN ADP NOUN ADJ PRON AUX',
                        'PUNCT DET NOUN CONJ NOUN AUX',
                        'DET ADJ CONJ DET NOUN AUX',
                        'DET NOUN ADJ ADP DET ADJ',
                        'VERB ADP NOUN AUX',
                        'NOUN ADJ VERB',
                        'DET NOUN AUX',
                        'DET NOUN ADP',
                        'ADJ NOUN',
                        'DET NOUN'
                    ]
                    for patron in range(len(patrons)):
                        if(band == 0):
                            patron = patrons[patron].split(' ')
                            patron_tag = ' '.join(posback[len(wordback)-len(patron):])
                            patron_word = ' '.join(wordback[len(wordback)-len(patron):])
                            listtag=posback[len(wordback)-len(patron):]
                            listword=wordback[len(wordback)-len(patron):]
                            
                            if(patron_tag in patrons):
                                band = 1
                                number_of_defs = number_of_defs+1
                                if('PUNCT' in listtag):
                                    punct=listtag.index('PUNCT')
                                    definiendum = ' '.join(listtag[punct:])
                                    correctpatron=' '.join(listtag[punct:])

                                elif(listtag[0] == 'ADJ' or listtag[0] == 'DET' or listtag[0] == 'CONJ' or listtag[0] == 'ADP' or listtag[0] == 'PUNCT'):
                                    listtag.pop(0)
                                    listword.pop(0)
                                elif(( listtag[len(listtag)-2] == 'PRON' and listtag[len(listtag)-1] == 'AUX') ):
                                    listword.pop(len(listword)-1)
                                    listtag.pop(len(listtag)-1)
                                    listword.pop(len(listword)-2)
                                    listtag.pop(len(listtag)-2)
                                elif(listtag[len(listtag)-1] == 'AUX' ):
                                    listword.pop(len(listword)-1)
                                    listtag.pop(len(listtag)-1)
                                
                                definiendum = ' '.join(listword)
                                correctpatron=' '.join(listtag)
                                definien = ''.join(phrase)
                    
                    definiendums=definiendum.split(' ')
                    if(copula in definiendums[len(definiendums)-1]):
                        definiendum=' '.join(definiendums[:len(definiendums)-1])
                        correctpatron=correctpatron[:len(correctpatron)-1]
                    #print(definiendum,'-denominarán', correctpatron)
                    if(len(definiendum) > 0):
                        joinpatron=' '.join(correctpatron)
                        filedef.write('\n'+definiendum+':'+definien)
                        #print('--->', definiendum)
                        definien = ''.join(phrase)
                        html = '<span style="background-color: #FDD2C4">'+definien+'</span>'
                        phrase = phrase.replace(definien, html)
                        html = '<a class="over" style="color: #D6400F"><B>'+definiendum + \
                            '</B><span class="tooltip" > '+copula+': '+joinpatron+'</span></a>'
                        phrase = phrase.replace(definiendum, html)
                        jsondefs['definitions'].append({definiendum:definien})
                        patronsfile.write(copula+':->'+joinpatron+'::futuro '+'\n')
        elif('haber' in lemlist ):     
            cont = lemlist.count('haber')
            poscopula = lemlist.index('haber')
            copula = tokens[poscopula]
            posfront = postaglist[poscopula:poscopula+1]
            wordfront = wordlist[poscopula:poscopula+1]
            posback = postaglist[poscopula-6:poscopula]
            wordback = wordlist[poscopula-6:poscopula]
            #print(wordfront)
            #print(posfront)
            definiendum = str()
            definien = str()

            listdef = list()
            if(len(definiendum) == 0 and cont < 2):
                band = 0
                patrons = [
                    'NOUN'
                ]
                for patron in range(len(patrons)):
                    if(band == 0):
                        patron = patrons[patron].split(' ')
                        patron_tag = ' '.join(posfront[:len(patron)])
                        patron_word = ' '.join(wordfront[:len(patron)])
                        listtag=posfront[:len(patron)]
                        listword=wordfront[:len(patron)]
                        #print('original: ',listtag)
                        if(patron_tag in patrons):
                            band = 1
                            number_of_defs = number_of_defs+1
                            if(listtag[0] == 'ADJ'):
                                listtag.pop(0)
                                listword.pop(0)
                            definiendum = ' '.join(listword)
                            correctpatron=' '.join(listtag)
                            definien = ''.join(phrase)
                #print(definiendum,'-haber',correctpatron)
                if(len(definiendum) > 0):
                    joinpatron=' '.join(correctpatron)
                    #filedef.write('\n no standard-'+definiendum+':'+definien)
                    #print('-->'+definiendum+':'+definien)
                    html = '<span style="background-color: #FDD2C4">'+definien+'</span>'
                    phrase = phrase.replace(definien, html)
                    html = '<a class="over" style="color: #D6400F"><B>'+definiendum + \
                        '</B><span class="tooltip" > '+copula+': '+joinpatron+'</span></a>'
                    phrase = phrase.replace(definiendum, html)
                    jsondefs['definitions'].append({definiendum:definien})
                    patronsfile.write(copula+':->'+joinpatron+'::n')
            #print('--------3', phrase)
            phrase3 += phrase
                
    labels.write(phrase3)
    with open('data.txt', 'w') as outfile:
        json.dump(jsondefs, outfile)
    return(jsondefs)



def envuelveCadenaenHTMLMac(programa, texto):
    import datetime
    from webbrowser import open_new_tab

    ahora = datetime.datetime.today().strftime("%Y%m%d-%H%M%S")
    nombreArchivo = programa + '.html'
    f = open(nombreArchivo, 'w')

    wrapper = """<html><meta charset="utf-8">
    <head>


	<style>
       * { margin: 0; padding:0; border: none;}
	body, html{width: 100%; height: 100%;}

	.over {
		display: inline-block;
		position: relative;
		text-align: left;
	}
	.over span.tooltip {
		display: none; 
        position: relative;
	}

	.over:hover span.tooltip {
		width: auto;
            top: -20px;
            left: 50%;
            transform: translate(-30%, -100%);
            padding: 10px  20px;
            color: #ffffff;
            background-color: #080F16;
            font-weight: normal;
            font-size: 14px;
            border-radius: 8px;
            position: absolute;
            z-index: 99999999;
            box-sizing: border-box;
            box-shadow: 0 1px 8px rgba(0, 0, 0, 0.5);
            display: block;
		
		
		 
        
	}
    </style>
	</head>
	<body><div style="margin-left: 10%; margin-right:10%; text-align: justify;"><font size=4 face="Arial"><h1>Definiciones</h1>"""+texto+"""</div></body>
	</html>"""

    todo = wrapper
    f.write(todo)
    f.close()

    # Cambia la ruta de la variable siguiente para que coincida la localizacion en tu directorio
    nombreArchivo = '/Users/krnlet/Documents/GitHub/Aicol2020definition' + nombreArchivo

    open_new_tab(nombreArchivo)



def main(document):

    '''parser = argparse.ArgumentParser()
    # nombre de archivo a leer
    parser.add_argument("--document", help="File name  ")
    args = parser.parse_args()

    namefile = args.document

    file = open(namefile, 'r', encoding='utf-8')
    document = file.read()


    #terms=extraction(document, 'es')
    #listclean=clean(terms)
    #extraction_patrons(document, listclean)'''
    file = open(document, 'r', encoding='utf-8')
    documento = file.read()
  
    salida=copula_funct(documento)
    sp = open('definitions_labels.txt', 'r')
    spread = sp.readlines()
    cadena = str()
    for i in spread:
        cadena += ' '+i+'<br>'
    envuelveCadenaenHTMLMac('html_definitions', cadena)
    '''
    filet = open('2000_terms_sketch.txt', 'r', encoding='utf-8')
    #terms=csv.reader(filet)
    terms=filet.readlines()
    withterms2(document, terms)
    #withterms(document, terms)
    '''
    return(salida)

        