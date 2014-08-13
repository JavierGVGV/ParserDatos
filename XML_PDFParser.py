# -*- coding: utf-8 -*-
"""
Created on Tue Apr 15 16:56:52 2014

@author: Javier
"""

#import requests
#import lxml
#import mechanize
#import urllib2
#import urllib
#from xml.dom.minidom import parse
from pdfminer.pdfdocument import PDFDocument
from pdfminer.pdfparser import PDFParser
from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.pdfdevice import PDFDevice, TagExtractor
from pdfminer.pdfpage import PDFPage
from pdfminer.converter import XMLConverter, HTMLConverter, TextConverter
from pdfminer.cmapdb import CMapDB
from pdfminer.layout import LAParams
from pdfminer.image import ImageWriter
from lxml import etree
import difflib
import keyword
import os
import glob

# Metodo que obtiene las lineas donde encontramos dicha expresion
# puede filtrar por encontrarlo en un determinado grupo
# retorna el numero de linea donde encuentra la coincidencia
def buscar_fichero(fichero,expresion,etiqueta):
    lineas = []
    f = open(fichero,'r')
    continua = 1
    indice = 0

    while(continua):
        linea = f.readline()
                
        if linea == "":
            continua = 0
            
        else:
            
            if etiqueta == "":
                corr = 1
            else:
                corr = 0
                corr = linea.count(etiqueta)
                
            if corr > 0:
                val = linea.count(expresion)
                if val > 0:
                    lineas.append(indice)
                
        indice = indice + 1
        
    f.close()        
        
    return lineas

# Metodo que dado un indice busca el grupo con la etiqueta indicada
# mas pequeño que lo englobe
def obten_grupo_xml(fichero,fichero_salida,indices,etiqueta_a,etiqueta_c):
    f = open(fichero,'r')
    continua = 1
    indice = 0
    inicial = -1
    final = -1
    ap_ci = 0
    
    while(continua):
        linea = f.readline()
        
        if linea == "":
            continua = 0
            
        else:
            # Indica si buscamos la apertura o el cierre de la etiqueta
            corr_a = linea.count(etiqueta_a)
            corr_c = linea.count(etiqueta_c)
            
            # Busco si es la etiqueta incio
            if ap_ci == 0:
                if corr_a > 0:
                    faux = open("auxiliar.txt",'w')
                    inicial = indice
                    ap_ci = (ap_ci + 1)%2
                  
            # Escribo la linea en un fichero temporal
            if inicial > -1:
                faux.write(linea)                    
                    
            # Busco si es la etiqueta final
            if ap_ci == 1:
                if corr_c > 0:
                    final = indice
                    faux.close()
                    if len(indices) > 0:
                        if (indices[0]>inicial) & (indices[0]<final):
                            copia_fichero("auxiliar.txt",fichero_salida)
                                
                    ap_ci = (ap_ci + 1)%2
                    inicial = -1
                    final = -1
            
            # Tras esto borro todos los datos previos al analizando
            if(len(indices)>0):
                continua_b = 0
                if(indices[0]<=inicial):
                    continua_b = 1
                while(continua_b):
                    indices.pop(0)
                    continua_b = 0
                    if (len(indices)>0):
                        if (indices[0]<=inicial):
                            continua_b = 1
            
        indice = indice + 1
        
    return 1
    
    # Metodo que dado un indice busca el grupo con la etiqueta indicada
# mas pequeño que lo englobe
def obten_grupo_xml_multiple(fichero,fichero_salida,indices,etiqueta_a,etiqueta_c):
    f = open(fichero,'r')
    continua = 1
    indice = 0
    inicial = -1
    final = -1
    ap_ci = 0
    
    while(continua):
        linea = f.readline()
        
        if linea == "":
            continua = 0
            
        else:
            
            if len(indices)>0:
                
                if (indices[0]-indice) < 1000:
                    
                    # Indica si buscamos la apertura o el cierre de la etiqueta
                    corr_a = 0
                    corr_c = 0
                    for et1 in etiqueta_a:
                        corr_a = corr_a + linea.count(et1)
                    for et2 in etiqueta_c:
                        corr_c = corr_c + linea.count(et2)
                    
                    # Busco si es la etiqueta incio
                    if ap_ci == 0:
                        if corr_a > 0:
                            faux = open("auxiliar.txt",'w')
                            inicial = indice
                            ap_ci = (ap_ci + 1)%2
                          
                    # Escribo la linea en un fichero temporal
                    if inicial > -1:
                        faux.write(linea)                    
                            
                    # Busco si es la etiqueta final
                    if ap_ci == 1:
                        if corr_c > 0:
                            final = indice
                            faux.close()
                            if len(indices) > 0:
                                if (indices[0]>inicial) & (indices[0]<final):
                                    copia_fichero("auxiliar.txt",fichero_salida)
                                        
                            ap_ci = (ap_ci + 1)%2
                            inicial = -1
                            final = -1
                    
                    # Tras esto borro todos los datos previos al analizando
                    if(len(indices)>0):
                        continua_b = 0
                        if(indices[0]<=inicial):
                            continua_b = 1
                        while(continua_b):
                            indices.pop(0)
                            continua_b = 0
                            if (len(indices)>0):
                                if (indices[0]<=inicial):
                                    continua_b = 1
            
        indice = indice + 1
        
    return 1
    
# Metodo auxiliar que copia un fichero a otro incremental
def copia_fichero(fichero_temp,fichero_incremental):
    fi = open(fichero_incremental,'a')
    ft = open(fichero_temp,'r')
    
    continua = 1
    while(continua):
        linea = ft.readline()
        
        if linea == "":
            continua = 0
            
        else:
            fi.write(linea)
            
    fi.close()
    ft.close()
    return 1

# Metodo que transforma un fichero .pdf en uno .txt y retorna el contenido como
# texto plano
def pdf_to_txt(fichero_pdf,fichero_txt):    

    # Especificamos la configuracion de nuestro pdf
    password = ''
    pagenos = set()
    maxpages = 0

    imagewriter = None
    rotation = 0
    codec = 'utf-8'
    caching = True
    laparams = LAParams()

    # Estrablecemos el gestor
    rsrcmgr = PDFResourceManager(caching=caching)
       
    # Creamos el fichero de salida y lingamos el dispositivo que lo transforma
    outfp = file(fichero_txt, 'w')
    device = TextConverter(rsrcmgr, outfp, codec=codec, laparams=laparams, imagewriter=imagewriter)
    
    # Para cada pagina del fichero pdf vamos interpretandola mediante el dispositivo
    fp = file(fichero_pdf, 'rb')
    interpreter = PDFPageInterpreter(rsrcmgr, device)
    for page in PDFPage.get_pages(fp, pagenos, maxpages=maxpages, password=password, caching=caching, check_extractable=True):
        page.rotate = (page.rotate+rotation) % 360
        interpreter.process_page(page)
        
    # Cerramos los dispositivos abiertos
    fp.close()
    device.close()
    outfp.close()
    
    return 1
    
# Metodo al que se le pasa un fichero ya procesado y retorna un fichero con el formato
# web idoneo para ser subido
def formato_web(fichero_procesado,fichero_salida):
    f = open(fichero_procesado,"r")
    f_s = open(fichero_salida,"w")
    
    titulo = "- **"
    year = 0
    autores = "  *"
    journal = ""
    volume = ""
    pages = ""
    
    f_s.write("<publicaciones>\n")    
    
    for evento,elemento in etree.iterparse(f):
        
        if elemento.getparent() is None:
            break        
        
        print("%5s, %4s, %s" % (evento, elemento.tag, elemento.text))
        
        if elemento.tag == "author":
            autores = autores+elemento.text+", "
        elif elemento.tag == "title":
            titulo = titulo+elemento.text+"**"
        elif elemento.tag == "year":
            year = int(elemento.text)
        elif elemento.tag == "journal":
            journal = elemento.text
        elif (elemento.tag == "volume") | (elemento.tag == "booktitle"):
            volume = elemento.text
        elif elemento.tag == "pages":
            pages = elemento.text
        elif elemento.tag == "article":
            f_s.write("<articulo>\n")
            f_s.write("<fecha>"+str(year)+"</fecha>\n")
            f_s.write("<contenido>")
            f_s.write(titulo+"\n")
            f_s.write("\n")
            autores = autores[0:len(autores)-2]
            f_s.write(autores+"*\n")
            f_s.write("\n")
            f_s.write("  "+journal+". Volume: "+volume+".\n")
            if(pages!=""):
                f_s.write("  Pages: "+pages+".\n")
            f_s.write("\n\n")
            f_s.write("</contenido>\n")
            f_s.write("</articulo>\n")
            titulo = "- ** "
            year = 0
            autores = "* "
            journal = ""
            volume = ""
            pages = ""
            
        elif elemento.tag == "inproceedings":
            
            f_s.write("<procedimiento>\n")
            f_s.write("<fecha>"+str(year)+"</fecha>\n")
            f_s.write("<contenido>")
            f_s.write(titulo+"\n")
            f_s.write("\n")
            autores = autores[0:len(autores)-2]
            f_s.write(autores+"*\n")
            f_s.write("\n")
            f_s.write("  Book Title: "+volume+".\n")
            if(pages!=""):
                f_s.write("  Pages: "+pages+".\n")
            f_s.write("\n\n")
            f_s.write("</contenido>\n")
            f_s.write("</procedimiento>\n")
            titulo = "- ** "
            year = 0
            autores = "* "
            journal = ""
            volume = ""
            pages = ""
            
        elif elemento.tag == "www":
            
            f_s.write("<www>\n")
            f_s.write("<fecha>"+str(year)+"</fecha>\n")
            f_s.write("<contenido>")
            f_s.write(titulo+"\n")
            f_s.write("\n")
            autores = autores[0:len(autores)-2]
            f_s.write(autores+"*\n")
            
            if(pages!=""):
                f_s.write("  Pages: "+pages+".\n")
            f_s.write("\n\n")
            f_s.write("</contenido>\n")
            f_s.write("</www>\n")
            titulo = "- ** "
            year = 0
            autores = "* "
            journal = ""
            volume = ""
            pages = ""
    
    f_s.write("</publicaciones>\n")
    f.close()
    f_s.close()
        
    return 1
 
# Netodo que prepara el fichero para ser proceado por lxml 
def eliminar_simbolos_html(fichero,resultado):
    f = open(fichero,"r")
    f_s = open(resultado,"w")
    texto = f.read()
    texto = texto.replace("&","")
    texto = texto.replace("acute;","")
    f_s.write("<publicaciones>\n")
    f_s.write(texto)
    f_s.write("</publicaciones>\n")
    f.close()
    f_s.close()
    return 1
    
# Fusiona dos ficheros respetando el formato del primero y lo guarda en un tercero
def fusionar_ficheros(fichero_or,fichero_ad,fichero_fin):
    f1 = open(fichero_or,"r")
    f2 = open(fichero_ad,"r")
    f_f = open(fichero_fin,"w")
    
    lineas = f1.readlines()

    indice = -1
    
    for evento, elemento in etree.iterparse(f2):
        
        if elemento.getparent() is None:
            break        
        
        print("%5s, %4s, %s" % (evento, elemento.tag, elemento.text))
        
        if elemento.tag == "fecha":
            indice = -1
            linea = 0
            for l in lineas:
                if l.count(elemento.text+"\n")>0:
                    indice = linea
                linea = linea + 1
                
        elif elemento.tag == "contenido":
            
            if indice > -1:
                lineas_temp = [] 
                lineas_temp.extend(lineas[0:indice+7])
                temp = elemento.text.split("\n")
                for t in temp:
                    lineas_temp.append(t+"\n")
                lineas_temp.extend(lineas[indice+8:-1])
                
                lineas = lineas_temp
            
        for l in lineas:
            f_f.write(str(l))
        
    f1.close()
    f2.close()
    f_f.close()
    return 1

# Metodo al que se le pasa un texto y un documento y retorna las coincidencias
# de que ese documento sea el contenido en el texto    
def buscador_documentos(titulo,documento):
    
    coincidencias = 0
    pre_coincidencias = 0
    total = 0
    f = open(documento,'r')
    texto = f.read()
    palabras_texto_temp = texto.split("\n")
    palabras_titulo_temp = titulo.split("\n")
    palabras_titulo = []
    palabras_texto = []
    
    for p in palabras_texto_temp:
        palabras_texto.extend(p.split(" "))
        
    for p in palabras_titulo_temp:
        palabras_titulo.extend(p.split(" "))
    
    salida = 0
    
    i = 0
    j = 0
    while j < len(palabras_titulo):

        if palabras_texto[i]==palabras_titulo[j]:
            pre_coincidencias = pre_coincidencias + 1
        if (palabras_texto[i]=="") | (palabras_texto[i]=="\n"):
            j = j - 1
            
        i = i + 1
        j = j + 1
        
        
    if pre_coincidencias == len(palabras_titulo):
        salida = 100.0
        
    else:
    
        for p in palabras_titulo:
            proximas = difflib.get_close_matches(p,palabras_texto,n=10)
            
            for prox in proximas:
                i=0
                while(i<min(len(prox),len(p))):
                    if prox[i] == p[i]:
                        coincidencias = coincidencias + 1
                    i = i + 1
                total = total + max(len(prox),len(p))
                
            if len(proximas) < 10:
                
                total = total + (len(p)*(10-len(proximas)))
                
        if coincidencias == 0:
            coincidencias = 1
        
        if total == 0:
            total = 1000
            
        salida = float(coincidencias)/total*100
        
    return salida
    
# Metodo que busca el pdf mas cercano al titulo especificado   
def busca_pdf(titulo):
    indice_cercano = -1
    similitud_maxima = 0
    txts = glob.glob("pdfs/*.txt")

    i = 0
    for txt in txts:

        similitud = buscador_documentos(titulo,txt)
        
        if similitud_maxima < similitud:
            similitud_maxima = similitud
            indice_cercano = i
            
        i = i + 1
        
    fichero = txts[indice_cercano].split(".")[0]+".pdf"
        
    return fichero,similitud_maxima
  
# Transforma todos los pdf del directorio actual a txt  
def pdfs_to_txts():
    pdfs = glob.glob("pdfs/*.pdf")
    for pdf in pdfs:
        nombre = pdf.split(".")
        nombre_txt = nombre[0]+".txt"
        pdf_to_txt(pdf,nombre_txt)
        
    return 1
    
# Metodo que procesa los pdfs en el directorio actual y los empareja con los titulos
# mas cercanos proporcionados
def procesa_titulos_pdfs(fichero_titulos):
    f = open(fichero_titulos,'r')
    fs = open('coincidencias.txt', 'w')
    lineas = f.readlines()
    titulos_pdfs = {}
    titulos_sim = {}
    pdfs_to_txts()
    
    for l in lineas:
        if l.count("**")>0:
            corte = l.split("**")
            pdf,similitud = busca_pdf(corte[1])
            titulos_pdfs[corte[1]] = pdf
            titulos_sim[corte[1]] = str(similitud)
            
    for e in titulos_pdfs.keys():
        fs.write(e)
        fs.write("\n")
        fs.write(titulos_pdfs[e])
        fs.write("\n")
        fs.write(titulos_sim[e])
        fs.write("\n")
        fs.write("\n")

    f.close()
    fs.close()         
            
    return titulos_pdfs, titulos_sim
    
#print procesa_titulos_pdfs("res.txt")
  
#print buscador_documentos("On the linear complexity of the Naor&#8211;Reingold sequence","pdfs/harald_final.txt")          
    


