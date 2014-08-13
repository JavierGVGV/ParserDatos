# -*- coding: utf-8 -*-
"""
Created on Mon Apr 21 11:31:49 2014

@author: Javier
"""

import requests
import urllib2
import urllib

URL = "http://dblp.uni-trier.de/xml/dblp.xml"

# Metodo que permite descargar un fichero de tipo binario
def descargar_fichero(url):
    nombre_fichero = url.split('/')[-1]
    print nombre_fichero
    r = requests.get(url)
    f = open(nombre_fichero, 'wb')
    tam = long(r.headers['content-length'])
    tam = (tam/1024)/1024
    print("Longitud Fichero: %d MB" % tam)
    
    for chunk in r.iter_content(chunk_size=512 * 1024):
        if chunk:
            f.write(chunk)
            
    f.close()
    return 1
    
# Metodo que permite solicitar paginas html sin formularios
def descargar_html(url):
    response = urllib2.urlopen(url)
    html = response.read()
    print html
    return html
    
# Metodo que permite solicitar una web para la que se requieren unos datos 
# a la hora de autentificarse
def descargar_auth(url_auth,url_destino,user,passwd):
    passwd_mgr = urllib2.HTTPPasswordMgrWithDefaultRealm()
    passwd_mgr.add_password(None,url_auth,user,passwd)
    handler = urllib2.HTTPBasicAuthHandler(passwd_mgr)
    opener = urllib2.build_opener(handler)
    urllib2.install_opener(opener)
    response = urllib2.urlopen(url_destino)
    html = response.read()
    print html
    return html

# Metodo que completa un formulario dado con los datos que se le pasan
def completar_formulario(url,url2,data):
    params = urllib.urlencode(form_data)
    response = urllib2.urlopen(url, params)
    html = response.read()
    response = urllib2.urlopen(url2, params)
    html = response.read()
    print html
    return 1
    
#url = "https://campusvirtual.unican.es/Identificacion/IdentificacionFrw.aspx"
#url2 = "https://campusvirtual.unican.es/BienvenidaFrw.aspx"
#form_data = {"ctl00$PhBody$LgUsuarios$UserName": 'jgv03', "ctl00$PhBody$LgUsuarios$Password": '425358', "ctl00$PhBody$RblColectivos": '2', "ctl00$PhBody$ChkCookies": 'checked'}
#completar_formulario(url,url2,form_data)
#descargar_html("https://campusvirtual.unican.es/Identificacion/IdentificacionFrw.aspx")
#descargar_auth("https://campusvirtual.unican.es/Identificacion/IdentificacionFrw.aspx","https://campusvirtual.unican.es/BienvenidaFrw.aspx","jgv03","425358")