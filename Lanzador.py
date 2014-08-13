# -*- coding: utf-8 -*-
"""
Created on Wed Apr 23 01:09:10 2014

@author: Javier
"""

from Interfaz import Ui_MainWindow
from PyQt4 import QtCore, QtGui
import sys
import XML_PDFParser
import URLInteract
import threading
import time
import argparse
import os

THREADS = []

FIN_DESCARGA = 0

class Interfaz_Usuario(QtGui.QMainWindow):
    
    # Definicion del constructor de la clase
    def __init__(self):
        
        # Inicializar el lanzamiento de ventanas
        self.app = QtGui.QApplication(sys.argv)        
        
        QtGui.QMainWindow.__init__(self)

        # Crear ventana de Registro
        self.ventana = Ui_MainWindow()
        self.ventana.setupUi(self)
        
        # Ocultar ventana de login
        self.ventana.webView.hide()
        
        # Activar conectores y señales de los botones
        self.connect(self.ventana.ButtonCancelar, QtCore.SIGNAL('clicked()'), self.cierra_ventana)
        self.connect(self.ventana.ButtonProcesar, QtCore.SIGNAL('clicked()'), self.arrancar_procesado)
        self.connect(self.ventana.ButtonDescargar, QtCore.SIGNAL('clicked()'), self.descargar)
        self.ventana.ComboBoxDestino.activated.connect(self.cambia_interfaz)
        
        # Añadir valores a la combo box para ser seleccionados
        self.ventana.ComboBoxOrigen.addItems(['DBLP Computer Science Bibliography'])
        self.ventana.ComboBoxDestino.addItems(['Copia Local','DBLP Computer Science Bibliography','Universidad de Cantabria'])
        
        # Mostrar y ejecutar la ventana        
        self.show()
        self.app.exec_()        
        
    # Metodo que modifica la interfaz a medida que es necesario
    def cambia_interfaz(self): 
        destino = self.ventana.ComboBoxDestino.currentIndex()
        if destino == 0:
            self.ventana.label_8.show()
            self.ventana.NombreFichero.show()
            self.ventana.resize_window(self,480,509)
            self.ventana.webView.hide()
        elif destino == 1:
            self.ventana.label_8.hide()
            self.ventana.NombreFichero.hide()
            self.ventana.resize_window(self,480,509)
            self.ventana.webView.hide()
        elif destino == 2:
            self.ventana.resize_window(self,966,509)
            self.ventana.webView.show()
            
        return 1
        
    # Metodo que cierra la ventana y no permite la apertura de mas
    def cierra_ventana(self):
        global THREADS
        for t in THREADS:
            t._Thread__stop()
        self.app.quit()        
        
    # Metodo que arranca un nuevo thread para procesar los datos solicitados
    def arrancar_procesado(self):
        
        destino = self.ventana.ComboBoxDestino.currentIndex()    
        
        if destino == 0:
        
            global THREADS
            t=threading.Thread(target=self.procesar_dblp_local)
            t.start()
            THREADS.append(t)
            
        elif destino == 2:
            
            url = "https://campusvirtual.unican.es/BienvenidaFrw.aspx"
            url_obj = QtCore.QUrl(url)
            self.ventana.webView.load(url_obj)
            
        return 1
        
    # Funcion que procesa la peticion concreta
    def procesar_dblp_local(self):
        
        self.ventana.progressBar_2.setValue(0)        
        
        # Obtenemos los valores de el origen y destino de los datos
        origen = self.ventana.ComboBoxOrigen.currentIndex()
        destino = self.ventana.ComboBoxDestino.currentIndex()
        
        # Obtenemos el termino por el cual filtrar nuestros datos
        termino_busqueda = str(self.ventana.TerminoBusqueda.toPlainText())
        
        indices = []
        fichero_origen = "dblp.xml"
        # Origen es la plataforma DBLP Computer Science Bibliography
        if origen == 0: 
            
            if destino == 0:
                fich_nom = self.ventana.NombreFichero.toPlainText()
                fichero_destino = fich_nom+".xml"
                print fichero_destino
                if self.ventana.CheckBoxAutor.isChecked():
                    print("Calculo Indices de Autor")
                    indices.extend(XML_PDFParser.buscar_fichero(fichero_origen,termino_busqueda,"<author"))
                    self.ventana.progressBar_2.setValue(5)
                    print indices
                if self.ventana.CheckBoxEditor.isChecked():
                    print("Calculo Indices de Editor")
                    indices.extend(XML_PDFParser.buscar_fichero(fichero_origen,termino_busqueda,"<editor"))
                    self.ventana.progressBar_2.setValue(10)
                    print indices
                if self.ventana.CheckBoxPublicador.isChecked():
                    print("Calculo Indices de Publicador")
                    indices.extend(XML_PDFParser.buscar_fichero(fichero_origen,termino_busqueda,"<publisher"))
                    self.ventana.progressBar_2.setValue(15)
                    print indices
                if self.ventana.CheckBoxTitulo.isChecked():
                    print("Calculo Indices de Titulo")
                    indices.extend(XML_PDFParser.buscar_fichero(fichero_origen,termino_busqueda,"<title"))
                    self.ventana.progressBar_2.setValue(20)
                    print indices

                indices.sort()                    
                
                if self.ventana.RadioButtonArticulo.isChecked():
                    XML_PDFParser.obten_grupo_xml(fichero_origen,fichero_destino,indices,"<article","</article")
                    self.ventana.progressBar_2.setValue(40)
                elif self.ventana.RadioButtonColeccion.isChecked():
                    XML_PDFParser.obten_grupo_xml(fichero_origen,fichero_destino,indices,"<incollection","</incollection")
                    self.ventana.progressBar_2.setValue(60)
                elif self.ventana.RadioButtonDebate.isChecked():
                    XML_PDFParser.obten_grupo_xml(fichero_origen,fichero_destino,indices,"<proceedings","</proceedings")
                    self.ventana.progressBar_2.setValue(70)
                elif self.ventana.RadioButtonTesis.isChecked():
                    XML_PDFParser.obten_grupo_xml(fichero_origen,fichero_destino,indices,"<phdthesis","</phdthesis")
                    XML_PDFParser.obten_grupo_xml(fichero_origen,fichero_destino,indices,"<mastersthesis","</mastersthesis")
                    self.ventana.progressBar_2.setValue(90)
                elif self.ventana.RadioButtonLibro.isChecked():
                    XML_PDFParser.obten_grupo_xml(fichero_origen,fichero_destino,indices,"<book","</book")
                    self.ventana.progressBar_2.setValue(95)
                elif self.ventana.RadioButtonOtros.isChecked():
                    XML_PDFParser.obten_grupo_xml(fichero_origen,fichero_destino,indices,"<www","</www")
                    XML_PDFParser.obten_grupo_xml(fichero_origen,fichero_destino,indices,"<inproceedings","</www")
                    self.ventana.progressBar_2.setValue(100)
                    
                print("PROCESADO FINALIZADO")
                self.ventana.progressBar_2.setValue(100)
            
            
        return 1
        
    # Metodo que arranca un nuevo thread para descargar los ficheros solicitados
    def descargar(self):
        global FIN_DESCARGA
        global THREADS
        FIN_DESCARGA = 0
        t1=threading.Thread(target=self.descargar_dblp)
        t2=threading.Thread(target=self.actualiza_bar)
        t1.start()
        t2.start()
        THREADS.append(t1)
        THREADS.append(t2)
            
        return 1
      
    # Metodo que descarga los datos probenientes del dblp
    def descargar_dblp(self):
        global FIN_DESCARGA
        URL = "http://dblp.uni-trier.de/xml/dblp.xml"
        URLInteract.descargar_fichero(URL)
        FIN_DESCARGA = 1
        return 1
        
    # Metodo que mantiene informado al usuario de cuanto vamos de progreso
    def actualiza_bar(self):
        i = 0
        while(FIN_DESCARGA==0):
            self.ventana.progressBar.setValue(i)
            i = i + 1
            i = i % 100
            
        self.ventana.progressBar.setValue(100)        
        
        return 1
        
# Ejecutamos por teclado y le pasamos los argumentos necesarios   
parser = argparse.ArgumentParser()
parser.add_argument(dest='origen_datos', type=str, nargs='?',help='Seleccion entre origenes de datos disponibles(dblp)')
parser.add_argument(dest='termino_busqueda', type=str, nargs='?',help='Terminos de busqueda del fichero.')
parser.add_argument(dest='fichero_destino', type=str, nargs='?',help='Fichero en el que se guardaran los datos.')
parser.add_argument(dest='fichero_fusion', type=str, nargs='?', help='Fichero con el cual se desea unir el proceado.')
parser.add_argument(dest='fichero_titulos', type=str, nargs='?', help='Fichero que contine los titulos a buscar.')
parser.add_argument('-I', dest='interfaz_activa',action='store_const',const=1,default=0,help='Especifica si se quiere ejecutar con interfaz.')
parser.add_argument('-D', dest='descarga_activa',action='store_const',const=1,default=0,help='Especifica si se quieren descargar los datos.')
parser.add_argument('-P', dest='procesar_activa',action='store_const',const=1,default=0,help='Especifica si se quieren procesar los datos.')
parser.add_argument('-F', dest='fusionar_activa',action='store_const',const=1,default=0,help='Especifica si se quieren fusionar ficheros.')
parser.add_argument('-S', dest='busqueda_activa',action='store_const',const=1,default=0,help='Especifica si se quiere buscar pdfs para dichos titulos.')
args = parser.parse_args()


if args.interfaz_activa == 1:
    Interfaz_Usuario()
    
elif args.descarga_activa == 1:
    
    # Descargamos los datos si es que es necesario
    URL = "http://dblp.uni-trier.de/xml/dblp.xml"
    URLInteract.descargar_fichero(URL)  
    
    # Comprobamos si se quieren procesar y lo hacemos
    if args.procesar_activa == 1:
    
        if args.origen_datos == "dblp":
        
            indices = XML_PDFParser.buscar_fichero("dblp.xml",args.termino_busqueda,"")
            
            etiquetas_apertura = ["<article","<incollection","<proceedings","<phdthesis","<mastersthesis","<book","<www","<inproceedings"]
            etiquetas_cierre = ["</article>","</incollection>","</proceedings>","</phdthesis>","</mastersthesis>","</book>","</www>","</inproceedings>"]            
            
            print indices            
            
            XML_PDFParser.obten_grupo_xml_multiple("dblp.xml",args.fichero_destino+"_temp.txt",indices,etiquetas_apertura,etiquetas_cierre)

            XML_PDFParser.eliminar_simbolos_html(args.fichero_destino+"_temp.txt",args.fichero_destino+"_temp2.txt")

            XML_PDFParser.formato_web(args.fichero_destino+"_temp2.txt",args.fichero_destino+".txt")
            
            if args.fusionar_activa == 1:
                
                XML_PDFParser.fusionar_ficheros(args.fichero_fusion,args.fichero_destino+".txt",args.fichero_destino+"_fusionado.txt")
                
            os.remove(args.fichero_destino+"_temp.txt")
            os.remove(args.fichero_destino+"_temp2.txt")
            
else:
    
    if args.procesar_activa == 1:
        
        if args.origen_datos == "dblp":
        
            indices = XML_PDFParser.buscar_fichero("dblp.xml",args.termino_busqueda,"")
            
            etiquetas_apertura = ["<article","<incollection","<proceedings","<phdthesis","<mastersthesis","<book","<www","<inproceedings"]
            etiquetas_cierre = ["</article>","</incollection>","</proceedings>","</phdthesis>","</mastersthesis>","</book>","</www>","</inproceedings>"]
            
            print indices
            
            XML_PDFParser.obten_grupo_xml_multiple("dblp.xml",args.fichero_destino+"_temp.txt",indices,etiquetas_apertura,etiquetas_cierre)

            XML_PDFParser.eliminar_simbolos_html(args.fichero_destino+"_temp.txt",args.fichero_destino+"_temp2.txt")

            XML_PDFParser.formato_web(args.fichero_destino+"_temp2.txt",args.fichero_destino+".txt")
            
            if args.fusionar_activa == 1:
                
                XML_PDFParser.fusionar_ficheros(args.fichero_fusion,args.fichero_destino+".txt",args.fichero_destino+"_fusionado.txt")
        
            os.remove(args.fichero_destino+"_temp.txt")
            os.remove(args.fichero_destino+"_temp2.txt")
            
if args.busqueda_activa == 1:
    
    XML_PDFParser.procesa_titulos_pdfs(args.fichero_titulos)