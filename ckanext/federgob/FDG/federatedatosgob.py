#!/usr/bin/python
# -*- coding: utf-8 -*-

#Script by: Jesús Redondo García
#Date: 28-10-2014

#Modified by Filip Radulovic and Idafen Santana Pérez
#Date: 31-03-2016

#Script to generate the whole metadata of the Catalog.

import urllib2
import urllib
import json
import time
from datetime import date, datetime
import re
import sys
import os


base_path = os.path.dirname( os.path.realpath( __file__ ) )

url_catalog = 'URL-CATALOG' #Get info from fields.conf
url_dataset_path = 'URL-DATASET' #Get info from fields.conf
base_filename = os.path.join(base_path,'base_catalog.rdf')
output_filename = os.path.join(base_path,'../public/federator.rdf')
logfile = os.path.join(base_path,'Logs/log_federator')
fields_conf = os.path.join(base_path,'fields.conf')

def fixTags(line,stream) :
	print >>stream, line.replace('<dct:title>','<dct:title xml:lang="es">').replace('<dct:description>','<dct:description xml:lang="es">'),

def load_metadata() :
	global url_catalog, url_dataset_path
	fields_conf_file = open(fields_conf,'r')
	fields_lines = fields_conf_file.readlines()

	for l in fields_lines :
		if '{-URL-CATALOG-} : ' in l : url_catalog = l.replace('{-URL-CATALOG-} : ','').replace('\n','')
		elif '{-URL-DATASET-} : ' in l : url_dataset_path = l.replace('{-URL-DATASET-} : ','').replace('\n','')
	if (url_catalog == 'URL-CATALOG') or (url_dataset_path == 'URL-DATASET') :
		print 'Error, federatedatosgob is not configured. Please run \"python config.py\".'
		sys.exit(0)





load_metadata()

print url_catalog


final_file=open(output_filename, 'w+')


base_file=open(base_filename,'r')
base_strings = base_file.readlines() 

for linea in base_strings:
	print >>final_file, linea.replace("@@SCRIPT-Date-update@@",str(datetime.now()).replace(" ","T")[0:19]),
print >>final_file,"\n"



#Check all distributions of all datasets
#################################################################

# Get datasets in the catalog.
try:
	response = urllib2.urlopen(url_catalog+'/api/3/action/package_list')
except Exception, e:
	print 'The catalog URL is not correct. Can not load CKAN API from:', url_catalog
	print url_catalog+'/api/3/action/package_list','is not accessible.'
	sys.exit(0)

assert response.code == 200




#Parse response
response_dict = json.loads(response.read())


assert response_dict['success'] is True
result = response_dict['result']

for name in result:
	print url_dataset_path+"/"+name+".rdf",

	try:
		pageRDF = urllib2.urlopen(url_dataset_path+"/"+name+".rdf")
	except Exception, e:
		print 'The dataset URL is not correct:', url_dataset_path
		print 'Can not download rdf file:', url_dataset_path+"/"+name+".rdf"
		sys.exit(0)


	print >>final_file,"<dcat:dataset>"

	#Remove header, everything that is before <!--dataset_metadata-->"
	strings_page_RDF = pageRDF.readlines()

	pca_old = "<rdf:value>pc-axis</rdf:value>"
	pca_new = "<rdf:value>text/pc-axis</rdf:value>"
	pcam_old = "<rdfs:label>pc-axis</rdfs:label>"
	pcam_new = "<rdfs:label>PC-Axis</rdfs:label>"
	rdf_old = "<rdf:value>RDF</rdf:value>"
	rdf_new = "<rdf:value>application/rdf+xml</rdf:value>"
	sdmx_old = "<rdf:value>sdmx</rdf:value>"
	sdmx_new = "<rdf:value>application/zip</rdf:value>"
	html_old = "<rdf:value>HTML</rdf:value>"
	html_new = "<rdf:value>text/HTML</rdf:value>"
	xls_old = "<rdf:value>XLS</rdf:value>"
	xls_new = "<rdf:value>application/vnd.ms-excel</rdf:value>"
	json_old = "<rdf:value>JSON</rdf:value>"
	json_new = "<rdf:value>application/json</rdf:value>"
	# dct = "dct:mediaType"
	# dcat = "dcat:mediaType"
	uri = "<dct:identifier>https://www.icane.es/data/"
	strings_page_RDF = [line.replace(pca_old, pca_new) for line in strings_page_RDF]
	strings_page_RDF = [line.replace(pcam_old, pcam_new) for line in strings_page_RDF]
	strings_page_RDF = [line.replace(pcam_old, pcam_new) for line in strings_page_RDF]
	strings_page_RDF = [line.replace(rdf_old, rdf_new) for line in strings_page_RDF]
	strings_page_RDF = [line.replace(sdmx_old, sdmx_new) for line in strings_page_RDF]
	strings_page_RDF = [line.replace(html_old, html_new) for line in strings_page_RDF]
	strings_page_RDF = [line.replace(json_old, json_new) for line in strings_page_RDF]
	strings_page_RDF = [line.replace(xls_old, xls_new) for line in strings_page_RDF]
	lista = []
	excluded = False

	for index, line in enumerate(strings_page_RDF):
		if "application/vnd.pc-axis" in line:
			lista.append(line.replace("application/vnd.pc-axis", "text/pc-axis"))
		else:
			lista.append(line)
			
		if "dct:language" in line:
			if "dcat:distribution" in strings_page_RDF[index+1]:
				pass
			else:
				excluded = True
					
	strings_page_RDF = lista
	strings_page_RDF = [re.sub("<dct:identifier>", uri, line)for line in strings_page_RDF]
	strings_page_RDF = [re.sub("http:", "https:", line)for line in strings_page_RDF]
	strings_page_RDF = [line.replace(dct, dcat) for line in strings_page_RDF]

	strings_page_RDF = lista
	strings_page_RDF = [re.sub("<dct:identifier>", uri, line)for line in strings_page_RDF]
	strings_page_RDF = [re.sub("http:", "https:", line)for line in strings_page_RDF]
	
	header_lines = 0
	while not strings_page_RDF[header_lines].strip().startswith("<dcat:Dataset"):
		header_lines+=1

	while not strings_page_RDF[header_lines].strip().startswith("</rdf:RDF>"):
#	header_lines+=1
#	while header_lines<len(strings_page_RDF)-2:
#		header_lines+=1
		#print >>final_file, fixTags(strings_page_RDF[header_lines]),
		fixTags(strings_page_RDF[header_lines],final_file)
		header_lines+=1

	print pageRDF.read()
	print >>final_file,"</dcat:dataset>\n"
#	print >>final_file,'\n'



#################################################################

#Añadimos las lineas para cerrar los metadatos
print >>final_file, "\t</dcat:Catalog>\n</rdf:RDF>"


#Añadimos la hora en la que se realiza la actualización en el fichero de log

fLog = open(logfile,'a')
print >>fLog, "["+str(datetime.now())+"]Metadata updated"
