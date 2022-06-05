#!/usr/bin/python3
# -*- coding: utf-8 -*-

"""
kwrite - ctrl+shift++ nebo -- zkolabuji procedury

--- Copyright note -------------------------------------------------------------
GNU-GPL PhDr. Mgr. Jeroným Klimeš, Ph.D. 2022-05-19

--- tidy --- varianty ----------------------------------------------------------
tidy -xml -i ctenarsky_denik.xml > ctenarsky_denik_tidy.xml # kdyz nefunguje ukládaní
xmlstarlet format --indent-tab data.xml
cat data.xml | python -c 'import sys;import xml.dom.minidom;s=sys.stdin.read();print(s)' 
--------------------------------------------------------------------------------
"""

import xml.etree.ElementTree as etree 
import datetime
import os
import subprocess
import re
import xml.dom.minidom	# from xml.dom import minidom
import time; # sleep(3)
import zenity

def pokusy():	
	print("procedura na pokusy")
	import html
	print(html.escape("ěščř<>@&!.-+"))
	exit()
	pokusy(); 

#--- CTRL-C handler ------------------------------------------------------------
#https://code-maven.com/catch-control-c-in-python
import signal
#import time # uz bylo importovano
 
def handler(signum, frame):
	global dirty
	if dirty==1:
		print ("\nCTRL-C je blokovano, protoze soubor není uložen.", filename_tmp, end="\n", flush=True)
		tree.write(filename_tmp,encoding='utf-8')
		print ("Soubor provizorne ulozen do:", filename_tmp, end="\n", flush=True)
	else:
		print ("\nSoubor beze změn...\nKončíme!", end="\n", flush=True)
		exit(1)
		
	
""" NEMAZAT, kdyby se chtelo pokracovat...	
import readchar
    msg = "Ctrl-c was pressed. Do you really want to exit? y/n "
    print(msg, end="", flush=True)
    res = readchar.readchar()
    if res == 'y':
        print("")
        exit(1)
    else:
        print("", end="\r", flush=True)
        print(" " * len(msg), end="", flush=True) # clear the printed line
        print("    ", end="\r", flush=True)
""" 

signal.signal(signal.SIGINT, handler)

#--- prikazova radka ----------------------------------------------------------
import sys
from optparse import OptionParser

def help():
	print("""
Čtenářský deník
---------------
	PhDr. Mgr. Jeroným Klimeš, Ph.D. 
	Funkční verze: http://ctenarskydenik.klimes.us
	Kontakty: http://www.klimes.us
	licence GNU-GPL 2022-05-19

Usage:
	ctenarsky_denik.py [-n|--napoveda] [-k|--kniha=4] [-s|--soubor nazev_souboru_bez_pripony]

Program je dělán jednoduše jako dvě smyčky, kde první pracuje s knihami, a druhá vkládá do vybrané knihy nové citace. 
Napřed si tedy založte novou knihu či stránku z Internetu, pak přejděte do smyčky Citace, kde vložíte příslušný text.

Protože program často padá, tak jakmile zadáte novou knihu či citaci, je pro jistotu okamžitě uložena do souboru: "ctenarsky_denik.tmp". Pokud program spadne, ale vy přesto chcete zachovat, co jste zadali, tak tento soubor přejmenujte na: ctenarsky_denik.xml. Větší problémy musíte vyřešit ruční editací XML souboru.

Všechny soubory musejí být v jednom adresáři. Tedy pohromadě musejí být:
ctenarsky_denik.py
ctenarsky_denik.xml
ctenarsky_denik.xsl
""")
	input("Press Enter to continue...")
	print("""
Pokud chcete mít svůj čtenářský deník na svých webových stránkách, musíte si uploadnout soubory s příponami: XML a XSL a dát je do jednoho adresáře. Druhou možností je, že vyexportujete html soubor, viz příkaz níže a ten nahrajete na Internet.

Pokud nejste připojeni k Internetu, můžete si přesto čtenářský deník číst těmito příkazy:

	sudo apt install xsltproc
	xsltproc  ctenarsky_denik.xsl ctenarsky_denik.xml > ctenarsky_denik.htm
	firefox ctenarsky_denik.htm
	
Pokud stále čtete jednu knihu, tak je výhodné ji startovat příkazem:
	ctenarsky_denik.py --kniha=4 # kde číslo označuje ID knihy.

Pokud XML soubor editujete ručně, tak je dobré ho občas učesat:
	tidy -xml -i ctenarsky_denik.xml > ctenarsky_denik_tidy.xml
	Pokud je tidy ok, tak novy soubor soubor přejmenujeme na ctenarsky_denik.xml

Tento program v terminálu je kostra, na kterou by chtělo přidělat nějaký GUI interface, čili dialogová okna v QT, ale na to zatím nemám časochuť. Stojí mi jiná práce...
	
""")
	exit()

op = OptionParser()
op.add_option('-k', '--kniha',
	action='store', type='int', dest='knihy_index',
	help='Nastavte ID knihy')
op.add_option('-s', '--soubor',
	action='store', type='string', dest='soubor',
	help='Soubor čtenářského deníku nez přípony')
op.add_option('-n', '--napoveda',
	action="store_true", help='Nápověda')
#op.add_option('-l', '--length',
	#action='store', type='int', dest='length',
	#help='set maximum length of output')
options, args = op.parse_args(sys.argv[1:])

if (options.knihy_index != None): # takhle se to vola
    knihy_index = options.knihy_index -1
else:
	knihy_index=0 

if (options.soubor != None): 
    filename = options.soubor
else:
	filename="ctenarsky_denik"
filename_xml=filename + '.xml'
filename_tmp=filename + '.tmp'
filename_xsl=filename + '.xsl'

if (options.napoveda != None): # takhle se to vola
    help()

def input_entry(titulek, pokyn, vychozi):                                                        
	vysledek= subprocess.Popen(["zenity", "--entry", "--text", pokyn, "--title", titulek, "--entry-text", vychozi ], stdout=subprocess.PIPE, stderr=subprocess.PIPE, stdin=subprocess.PIPE)
	vysledek.wait()
	exit_code = vysledek.returncode
	return exit_code, re.sub(r'^\s+|\s+$', '', vysledek.stdout.read().decode())
	#print (input_entry("titulek", "hele sem", "co tohle?"))
	#exit()

def input_box(titulek, vychozi):
	prikaz=' echo "'+vychozi+'" | zenity --text-info --editable --title "'+titulek+'"  2> /dev/null'
	#vysledek= subprocess.Popen(["zenity", "--text-info", "--editable", "--title", titulek], stdout=subprocess.PIPE, stderr=subprocess.PIPE, stdin=subprocess.PIPE)
	vysledek= subprocess.Popen(["zenity", "--text-info", "--editable", "--title", titulek], stdout=subprocess.PIPE,  stdin=subprocess.PIPE, stderr=subprocess.PIPE) #,
	#stdout, stderr = vysledek.communicate(input=b'one\ntwo\nthree\nfour\nfive\nsix\n')
	stdout, stderr = vysledek.communicate(input=bytes(vychozi, 'utf-8'))
	vysledek.wait()
	exit_code = vysledek.returncode
	return exit_code, re.sub(r'^\s+|\s+$', '', stdout.decode())

def yes_no_box_varovani(titulek, dotaz):
	vysledek= subprocess.Popen(["zenity", "--question", "--text", dotaz, "--ok-label", "Budiž", "--cancel-label", "Počkáme ještě", "--no-wrap", "--title", titulek], stdout=subprocess.PIPE, stderr=subprocess.PIPE, stdin=subprocess.PIPE)
	vysledek.wait()
	exit_code = vysledek.returncode
	#return exit_code # 1=ne, 0=ano
	return -1*exit_code+1  # 0=ne, 1=ano
#print(yes_no_box_varovani("titulek hore", "zvídavý dotaz"))
#exit()

def ulozit():  #nic lepsiho jsem nevymyslel
	global dirty
	global filename_xml
	#filename_xml="ctenarsky_denik.xml"
	os.rename(filename_xml, (filename+"_"+datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')+".xml"))
	#xmlstr = xml.dom.minidom.parseString(etree.tostring(knihy)).toprettyxml(indent="", newl='') # ZLOBILO TO, encoding="utf-8"
	xmlstr = xml.dom.minidom.parseString(etree.tostring(knihy)).toprettyxml(indent="") # , encoding="utf-8"
	xmlstr = re.sub(r'^\s+\s*\n', '', xmlstr, flags=re.MULTILINE) # smaze prazdne radky
	xmlstr = re.sub(r'^.*\n', '', xmlstr) # toto odstrani prvni radku
	with open(filename_xml, "w") as f:
		f.write('<?xml version="1.0" encoding="UTF-8"?>\n')   
		f.write('<?xml-stylesheet type = "text/xsl" href = "'+filename_xsl+'"?>\n')   
		f.write(xmlstr  )
		f.close()
	dirty=0
	
def ulozit_pokusy_odpad(): 
	global dirty
	global filename_xml
	#filename_xml="ctenarsky_denik.xml"
	print(etree.tostring(knihy, pretty_print=True))
	exit()
	print(xml.dom.minidom.parseString(etree.tostring(knihy)))
	xmlstr = xml.dom.minidom.parseString(etree.tostring(knihy)).toprettyxml(indent="\t") # , encoding="utf-8"
	print(xmlstr)
	print(etree.tostring(knihy, "utf-8"))
	os.rename(filename_xml, (filename+"_"+datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')+".xml"))
#cat data.xml | python -c 'import sys;import xml.dom.minidom;s=sys.stdin.read();print 

	xmlstr = re.sub(r'^\s+\s*$', '', xmlstr, flags=re.MULTILINE).replace('\n\n', '\n')
	with open(filename_xml, "w") as f:
		f.write(xmlstr)
		f.close()
	with open(filename_xml, "r+") as ff:
		lines = ff.readlines()[1:]  # bez prvni radky    
		lines.insert(0, '<?xml-stylesheet type = "text/xsl" href = "'+filename_xsl+'"?>\n')   
		lines.insert(0, '<?xml version="1.0" encoding="UTF-8"?>\n')   
		ff.seek(0)            
		ff.writelines(lines)
		ff.close()
	dirty=0

def nova_kniha():
	global id, autor, nazev, citace, poznamka, url, knihy, dirty, knihy_pocet, citaty_pocet 
	max_id=0
	for i in knihy.findall("kniha"):
		if i.find("id")!=None: # muze existovat kniha bez id
			i_int=int(i.find('id').text)
			if i_int>max_id: max_id=i_int # zjisti max_id pro zalozeni nove knihy
	max_id=str(max_id+1)
	error,_=input_entry("Nové ID", "ID="+max_id+"? ", max_id)
	if error==0: new_id=_
	error,_=input_entry("Autor", "Autor:", "")
	if error==0: new_autor=_
	error,_=input_entry("Název", "Název knihy: ", "")
	if error==0: new_nazev=_
	error,_=input_box("Citace knihy","")
	if error==0: new_citace=_
	error,_=input_box("Poznámka","")
	if error==0: new_poznamka=_
	error,_=input_box("URL","")
	if error==0: new_url=_
		
	print("""\nShrnutí před vložením:\nID: %s\nAutor: %s\nNázev: %s\nCitace: %s\nPoznámka: %s\nURL: %s\n""" %(new_id, new_autor, new_nazev, new_citace, new_poznamka, new_url))
	if (input("\nMají se vložit tyto hodnoty? [a/N] ") == "a"):
		nova_kniha = etree.SubElement(knihy, 'kniha')
		etree.SubElement(nova_kniha, 'id').text = new_id
		etree.SubElement(nova_kniha, 'autor').text = new_autor
		etree.SubElement(nova_kniha, 'nazev').text = new_nazev
		etree.SubElement(nova_kniha, 'citace').text = new_citace
		etree.SubElement(nova_kniha, 'poznamka').text = new_poznamka
		etree.SubElement(nova_kniha, 'url').text = new_url
		knihy_pocet=knihy_pocet+1
		print("\nNova kniha vytvorena.\n")
		dirty=1

def kniha_nacteni():
	global max_id, id, autor, nazev, citace, poznamka, url, dirty, knihy_pocet, citaty_pocet
	id=""
	autor=""
	nazev=""
	citace=""
	poznamka=""
	url=""
	
	citaty=knihy[knihy_index].findall('citat')
	citaty_pocet=len(citaty)

	if (knihy[knihy_index].find("id") != None and knihy[knihy_index].find("id").text != None):
		id=knihy[knihy_index].find("id").text
	if (knihy[knihy_index].find("autor") != None and knihy[knihy_index].find("autor").text != None ):
		autor=knihy[knihy_index].find("autor").text
	if (knihy[knihy_index].find("nazev") != None and knihy[knihy_index].find("nazev").text != None):
		nazev=knihy[knihy_index].find("nazev").text
	if (knihy[knihy_index].find("citace") != None and knihy[knihy_index].find("citace").text != None):
		citace=knihy[knihy_index].find("citace").text
	if (knihy[knihy_index].find("poznamka") != None and knihy[knihy_index].find("poznamka").text != None):
		poznamka=knihy[knihy_index].find("poznamka").text
	if (knihy[knihy_index].find("url") != None and knihy[knihy_index].find("url").text != None):
		url=knihy[knihy_index].find("url").text

def kniha_vypis():
	global id, autor, nazev, citace, url, poznamka, citaty_pocet, knihy_pocet
	print()
	print("ID:		",id)
	print("Autor:		",autor)
	print("Název:		",nazev)
	print("Citace:		",citace)
	print("Url: 		", url)
	print("Poznámka:	", poznamka)
	print("Počet citátů:	",citaty_pocet)
	print()

def kniha_editace():
	global id, autor, nazev, citace, poznamka, url, dirty
	
	kniha_edit=knihy[knihy_index]
	kniha_nacteni()

	error,_=input_entry("Nové ID", "ID ["+id+"]: ", id)
	if (error==0): new_id=_ 

	error,_=input_entry("Nové autor", "Nový autor", autor)
	if (error==0): new_autor=_ 
		
	error,_=input_entry("Název", "Název: ", nazev)
	if (error==0): new_nazev=_ 
	
	error,_=input_box("Citace", citace)
	if (error==0): new_citace=_ 

	error,_=input_box("Poznámka",poznamka)
	if (error==0): new_poznamka=_ 
	
	error,_=input_box("URL",url)
	if (error==0): new_url=_	

	print("""\nShrnutí před vložením:\nID: %s\nAutor: %s\nNázev: %s\nCitace: %s\nPoznámka: %s\nURL: %s\n""" %(new_id, new_autor, new_nazev, new_citace, new_poznamka, new_url))
	if (input("\nMají se vložit tyto hodnoty? [a/N] ") == "a"):
		if (kniha_edit.find("id") != None and kniha_edit.find("id").text != None):
			kniha_edit.find("id").text = new_id
		else:
			etree.SubElement(kniha_edit, 'id').text = new_id

		if (citat_edit.find("nadpis") != None ):
			citat_edit.remove(citat_edit.find("nadpis"))
		citat_edit.append(etree.fromstring("<nadpis>"+citat_nadpis+"</nadpis>"))


		if (kniha_edit.find("autor") != None and kniha_edit.find("autor").text != None):
			kniha_edit.find("autor").text = new_autor
		else:
			etree.SubElement(kniha_edit, 'autor').text = new_autor
			
		if (kniha_edit.find("nazev") != None and kniha_edit.find("nazev").text != None):
			kniha_edit.find("nazev").text = new_nazev
		else:
			etree.SubElement(kniha_edit, 'nazev').text = new_nazev
			
		if (kniha_edit.find("citace") != None and kniha_edit.find("citace").text != None):
			kniha_edit.find("citace").text = new_citace
		else:
			etree.SubElement(kniha_edit, 'citace').text = new_citace
	
		if (kniha_edit.find("url") != None and kniha_edit.find("url").text != None):
			kniha_edit.find("url").text = new_url
		else:
			etree.SubElement(kniha_edit, 'url').text = new_url

		if (kniha_edit.find("poznamka") != None and kniha_edit.find("poznamka").text != None):
			kniha_edit.find("poznamka").text = new_poznamka
		else:
			etree.SubElement(kniha_edit, 'poznamka').text = new_poznamka

		print("\nKniha je upravena.\n")
		dirty=1
	else:
		print("\nŽádné změny v této knize.\n")

def kniha_delete():
	global knihy_index, knihy_pocet, dirty
	temp=input("\nZadejte heslo pro mazání této knihy (ksic): ")
	if temp == "ksic":
		knihy.remove(knihy[knihy_index])
		knihy_pocet=len(knihy)
	else:
		print("Špatné heslo = žádné mazání")
	dirty=1

def citat_novy():
	global dirty, knihy_index, citaty_index
	
	error,_=input_entry("Nadpis", "Nadpis:", "")
	if (error==0): citat_nadpis=_ 
	

	#temp=input("\nMají se sloučit řádky do jednoho odstavce? [a/N] ")
	if (yes_no_box_varovani("Sloučení řádek", "Mají se sloučit řádky do jednoho odstavce?")==1): # ma se text sloucit
		print("Slučujeme řádky...")
		error,_=input_box("Text","")
		if (error==0): 
			citat_text=_.replace('-\n', '').replace('\n', ' ')
			#error,_=input_box("Text","")
			error,citat_text=input_box("Je to takto správně?",citat_text) # dal uz to netestuje
		else:
			citat_text=""
	else:
		#citat_text=input_box("Text","")
		error,_=input_box("Text","")
		if (error==0): citat_text=_
	
	error,_=input_entry("Strana", "Strana", "")
	if (error==0): citat_strana=_

	error,_=input_box("Komentář","")
	if (error==0): citat_komentar=_

	print("""\nShrnutí před vložením:\nNadpis: %s\nText: %s\nStrana: %s\nKomentář: %s\n""" %(citat_nadpis, citat_text, citat_strana, citat_komentar))
	if (input("\nMají se vložit tyto hodnoty? [a/N] ") == "a"):
		citat_novy = etree.SubElement(knihy[knihy_index], 'citat')
		etree.SubElement(citat_novy, 'nadpis').text = citat_nadpis # .replace('-\n', '').replace('\n', ' ')
		citat_novy_text = etree.SubElement(citat_novy, 'text') 
		for odstavec in citat_text.split('\n'):
			try:	
				citat_novy_text.append(etree.fromstring("<p>"+odstavec+"</p>"))
			except:
				citat_novy_text.append(etree.fromstring("<p>"+html.escape(odstavec)+"</p>"))
			print("Odstavec:", odstavec)
		try:	
			citat_novy.append(etree.fromstring("<komentar>"+citat_komentar+"</komentar>"))
		except:
			citat_novy.append(etree.fromstring("<komentar>"+html.escape(citat_komentar)+"</komentar>"))
		etree.SubElement(citat_novy, 'strana').text = citat_strana #temp.replace('-\n', '').replace('\n', ' ')
		etree.SubElement(citat_novy, 'datum').text = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S') 
		dirty=1

def citat_nacteni():
	global citaty_index, knihy_index, citat_edit, citat_nadpis, citat_text, citat_strana, citat_komentar, citat_datum
	citat_nadpis=""
	citat_text=""
	citat_strana=""
	citat_komentar=""
	citat_datum=""	
	
	if (citaty_pocet>0): 
		if (citat_edit.find("nadpis") != None and citat_edit.find("nadpis").text !=None):
			citat_nadpis=etree.tostring(citat_edit.find("nadpis"), encoding="unicode")
			citat_nadpis=re.sub(r'^<nadpis>|<\/nadpis>', '', citat_nadpis)
			citat_nadpis=citat_nadpis.replace('-\n', '').replace('\n', ' ').replace('  ', ' ').replace('   ', ' ')
		if (citat_edit.find("text") != None and citat_edit.find("text").find("p") != None):
			for pecko in citat_edit.find("text").findall("p"):
				temp = etree.tostring(pecko, encoding="unicode")
				temp = re.sub(r'^<p>|<\/p>|<p />', '', temp).replace('-\n', '').replace('\n', ' ').replace('  ', ' ').replace('   ', ' ')
				citat_text += temp + "\n"
		if (citaty[citaty_index].find("strana") != None and citaty[citaty_index].find("strana").text !=None):
			citat_strana=citaty[citaty_index].find("strana").text
		if ( citat_edit.find("komentar") != None and citat_edit.find("komentar").text !=None):
			citat_komentar=etree.tostring(citat_edit.find("komentar"), encoding="unicode")
			citat_komentar=re.sub(r'^<komentar>|<\/komentar>', '', citat_komentar).replace('-\n', '').replace('\n', ' ').replace('   ', ' ').replace('  ', ' ')
	else:
		print("Tato kniha ještě neobsahuje žádné citáty.")

def citat_vypis():
	#musi predchazet citat_nacteni()
	global citaty_index, knihy_index, autor, nazev, citat_nadpis, citat_strana, citat_text, citat_komentar
	print(str(knihy_index+1) + ".", str(autor) + ":", str(nazev))
	if (citaty_pocet>0): 
		if citat_strana =="": 
			print(str(citaty_index+1) + ". citát\nNadpis:",  citat_nadpis) 
			print("Text:\n")
		else:
			print(str(citaty_index+1) + ". citát\nNadpis:",  citat_nadpis)
			print("Text, str.", citat_strana)
		print(citat_text)
		print("Komentář: ", citat_komentar)
	else:
		print("Tato kniha ještě neobsahuje žádné citáty.")

def citat_editace(): 
	#po načtení by měl uz existovat objekt citat_edit, a vsechny promenne s textem: citat_nadpis, citat text ap.
	global id, autor, nazev, citace, poznamka, url, dirty, citat_nadpis, citat_text, citat_strana, citat_komentar
	error,_=input_box("Nadpis", citat_nadpis)
	if (error==0): citat_nadpis=_ 
	error,_=input_box("Text", citat_text)
	if (error==0): citat_text=_ 
	error,_=input_entry("Strana", "Strana", citat_strana)
	if (error==0): citat_strana=_ 
	error,_=input_box("Komentář",citat_komentar)
	if (error==0): citat_komentar=_ 

	print("""\n\nShrnutí před vložením:\nNadpis: %s\nText: %s\nStrana: %s\nKomentář: %s\n""" %(citat_nadpis, citat_text, citat_strana, citat_komentar))
	if (input("\nMají se vložit tyto hodnoty? [a/N] ") == "a"):
		if (citat_edit.find("nadpis") != None ):
			citat_edit.remove(citat_edit.find("nadpis"))
		citat_edit.append(etree.fromstring("<nadpis>"+citat_nadpis+"</nadpis>"))
			
		if (citat_edit.find("text") != None):
			for pecko in citat_edit.find("text").findall('p'): # smaze stare odstavce
				citat_edit.find("text").remove(pecko)

			for odstavec in citat_text.split('\n'): # rozreze do odstavcu a na peckuje do .textu
				citat_edit.find("text").append(etree.fromstring("<p>"+odstavec+"</p>"))
				print("Odstavec:", odstavec) # toto casem smazat - to je jen pro kontrolu
		
		if (citat_edit.find("komentar") != None ):
			citat_edit.remove(citat_edit.find("komentar"))
		citat_edit.append(etree.fromstring("<komentar>"+citat_komentar+"</komentar>"))
		
		if (citat_edit.find("strana") == None ):
			etree.SubElement(citat_edit, 'strana').text = citat_strana
		else:	
			citat_edit.find("strana").text= citat_strana
		print("\nCitát upraven.\n")
		dirty=1
	else:
		print("\nCitát beze změn.\n")
	
def citat_delete():
	global dirty,knihy_index, citaty_index, citat_edit
	#temp=input_box("Zadejte heslo pro mazání citátu (ksic)","")
	temp=input("\nZadejte heslo pro mazání citátu (ksic): ")
	if temp == "ksic":
		knihy[knihy_index].remove(citaty[citaty_index])
	else:
		print("Špatné heslo = žádné mazání")
	dirty=1

def print_seznam_knih():
	print("ID Autor Nazev: ")
	for child in knihy:
		print(child.find("id").text + "	" + str(child.find("autor").text) + "	" + str(child.find("nazev").text))
	print()


#--- Hlavní procedura ----------------------------------------------------------

#if os.path.isfile(filename_xml)==False:
if not os.path.isfile(filename_xml):
	with open(filename_xml, "w") as f:
		f.write('<knihy><kniha><id>1</id><autor>Editujte tento záznam</autor><nazev>Přidejte nové knihy</nazev></kniha></knihy>\n')   
		f.close()
	
tree = etree.parse(filename_xml) 
knihy = tree.getroot()
knihy_pocet=len(knihy)
#Deklarace globalnich promennych
citaty_pocet=1
id=""
autor=""
nazev=""
citace=""
poznamka=""
url=""
citat_nadpis=""
citat_text=""
citat_strana=""
citat_komentar=""
citat_datum=""
dirty=0


print("""
Čtenářský deník
---------------
""")
print("Ve čtenářském deníku "+filename_xml+" je " + str(knihy_pocet) + " knih: ")
print()
print_seznam_knih()

knihy_volba="asdf"
while (knihy_volba!="q"):
	print(">>>>> >>>> >>> >> > K N I H Y < << <<< <<<< <<<<<")
	try:
		temp=int(eval(knihy_volba))
	except:
		temp=0
	if (temp>0):
		knihy_index=temp-1 # index vyberu jde od 0 do (pocetknih-1)
	elif (knihy_volba == "n"):
		nova_kniha()		
		tree.write(filename_tmp,encoding='utf-8')
	elif (knihy_volba == "e"):
		kniha_editace()
		tree.write(filename_tmp,encoding='utf-8')
		#knihy_pocet=knihy_pocet+1
		#print("\nKniha je upravena.\n")
	elif (knihy_volba == "d"):
		kniha_delete()
		tree.write(filename_tmp,encoding='utf-8')
		knihy_index=knihy_index-1 # aktualni je smazana, takze musi jit o knihu zpet
	elif (knihy_volba == "j"):
		knihy_index=knihy_index-1
		#print("j:", str(knihy_index))	
	elif (knihy_volba == "k"):
		knihy_index=knihy_index+1
		#print("k:", str(knihy_index))	
	elif (knihy_volba == "s"):
		print("\n%s je ulozen" % filename_xml)
		ulozit()
	if (knihy_index>(knihy_pocet-1)):
		knihy_index=knihy_pocet-1
	elif (knihy_index<0):
		knihy_index=0

	kniha_nacteni()
	kniha_vypis()

	citaty_volba="asdf"
	citaty_index=0
	while (citaty_volba!="q" and (knihy_volba=="l" or knihy_volba=="")):
		try:
			temp=int(eval(citaty_volba)) # je-li to cislo, tak pracuje s cislem
		except:
			temp=0
		if (temp>0):
			citaty_index=temp-1
		if (citaty_volba == "n"):
			citat_novy()
			tree.write(filename_tmp,encoding='utf-8')
			print("\nNovy citát vytvořen.\n")
		elif (citaty_volba == "e"):
			citat_editace()
			tree.write(filename_tmp,encoding='utf-8')
		elif (citaty_volba == "j"):
			citaty_index=citaty_index-1
			#print("j:", str(citaty_index))	
		elif (citaty_volba == "d"):
			citat_delete()
			tree.write(filename_tmp,encoding='utf-8')
			citaty_index=citaty_index-1
			citaty_pocet=len(citaty)
		elif (citaty_volba == "k"):
			citaty_index=citaty_index+1
			#print("k:", str(citaty_index))	
		elif (citaty_volba == "s"):
			ulozit()
			print("\nSoubor "+filename_xml+" je ulozen.\n")
		if (citaty_index>(citaty_pocet-1)):
			citaty_index=citaty_pocet-1
			#print("horni:", str(citaty_index))	
		elif (citaty_index<0):
			citaty_index=0

		citaty=knihy[knihy_index].findall('citat')
		citaty_pocet=len(citaty)
		if (citaty_pocet>0): citat_edit=citaty[citaty_index] # nacte aktualni citat jako objekt
		if (citaty_pocet>0): citat_nacteni() # tady by to melo nacist hodnoty
		print("CITÁTY - - - C I T Á T Y - - - CITÁTY - - - C I T Á T Y  - - - CITÁTY")
		citat_nacteni()
		citat_vypis()
		print("j - předchozí citát; k - dalsi citat; q - zpět knihy; e - editovat citat; n - nový citat; s - uložit")
		citaty_volba=input("Vyberte citát [" + str(citaty_pocet) + "]: ") 
		os.system('clear')

	if citaty_volba=="q":
		kniha_vypis() # kdyz se vraci z citatu tak to vypise aktualni knihu
		citaty_volba="asdf" # iniciace promenne

			#citaty=knihy[knihy_index].findall('citat')
			#citaty_pocet=len(citaty)
	print("j - předchozí kniha; k - další kniha; q - konec; l - procházet citace; e - editovat knihu; n - nová kniha; s - uložit; d - smazat knihu")
	knihy_volba=input("Vyberte knihu: [" + str(knihy_pocet) + "] ") 
	os.system('clear')

	#print ("dirty: ", dirty)
		
	#knihy_volba=input("Vyberte knihu: [1-" + str(knihy_pocet) + "] ") 
#print ("dirty: ", dirty)	
if dirty==1:
	temp=""
	while temp != "a" and temp != "n":
		temp=input("Chcete ulozit soubor? [a/n] ")
		if temp=="a":
			ulozit()
			print("Soubor", filename_xml, "je uložen.")

print("\nAu réservoir!\n") # U nádrže...
exit()

