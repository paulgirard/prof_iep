# -*- coding: utf-8 -*-
import re


verbose=0
export_gexf=1
export_dot=0

if export_gexf :
	from pygexf.gexf import *


def supprime_accent(ligne):
        """ supprime les accents du texte source """
        accents = { 'a': ['à', 'ã', 'á', 'â'],
                    'e': ['é', 'è', 'ê', 'ë'],
                    'i': ['î', 'ï'],
                    'u': ['ù', 'ü', 'û','Ü'],
                    'o': ['ô', 'ö','Ö'],
                    'c' : ['ç'] }
        for (char, accented_chars) in accents.iteritems():
            for accented_char in accented_chars:
                ligne = ligne.replace(accented_char, char)
        return ligne

def autokey(key=0) :
	while True :
		yield key
		key=key+1
	
ak = autokey()	

def addProfession(line,professions,professionGroups) :
	# input :
	#     line =[group3,group2,group1,name,nameId]
	#     professions[id]=[name,pid,depth]
	#     professionsGroups[(group,pid)]=[id,lastId,depth]
	
	# filtrage des groupes vides
	
	line=filter(lambda g:not g=="",line)
	
	lastId=-1
	depth=0
	for group in line[0:len(line)-2] :
		if not group=="":
			# using (group,lasrId) as key to disambiguish same group name with different fathers
			if not (group,lastId) in professionGroups.keys() :
				id="g"+str(ak.next())
				professionGroups[(group,lastId)]=[id,lastId,depth]
				#print str(lastId)+" > "+str(id)+" - "+group
			lastId=professionGroups[(group,lastId)][0]
			depth+=1
	
	name=line[len(line)-2]
	id=line[len(line)-1]
	professions[id]=[name,lastId,depth]
	
	
	#print str(lastId)+" > "+str(id)+" - "+name


def cleanIndata(data):
	# process the data from CSV with some cleaning
	
	# get rid of eol
	line=re.sub("[\r\n]","",data)
	data=line.split(";")
	# get rid of trailing spaces and "
	data=map(lambda s:s.strip(' "'),data)
	# get rid of accent unicode prb to be solved...
	data=map(supprime_accent,data)
	
	return data


def loadProfessionCode(file):
# load a csv with ; as separator
# colomun 0 : category name
# column 1	: group1 name
# column 2	: group2 name (optional)
# column 3	: entity name
# column 4	:  ID
# returns professions[id]=[name,pid,depth]	
	nbline=1
	professionGroupsByName={}
	professions={}

	for line in file.readlines():
		try :
			if not line=="" :
				
				data=cleanIndata(line)			
				# to professions table with pid calculation
				addProfession(data,professions,professionGroupsByName)


		except Exception as e :
			print "error loadProfession line "+str(nbline)+" : "+line
			print e
			
		nbline+=1


	
	# reverse key in dict professionsByName to professionsById
	professionGroupsById=dict([[id,[name,pid,depth]] for (name,pid),[id,pid,depth] in professionGroupsByName.iteritems()])
	
	# let's merge the two dict :
	professions.update(professionGroupsById)

	return professions
	
def loadDisciplineCode(file):
# load a csv with ; as separator
# colomun 0 : discipline name
# column 1	:  code
# returns discipline[code]=[name]	
	nbline=1
	disciplines={}
	lines=file.readlines()
	# get rid of first line
	for line in lines[1:]:
		try :
			if not line=="" :
				data=cleanIndata(line)		
				disciplines[data[1]]=data[0]
		except Exception as e :
			print "error  loadDiscipline line "+str(nbline)+" : "+line
			print e
		nbline+=1

	return disciplines

def loadProfessionColorCode(file):
# load a csv with ; as separator
# colomun 0 : profession name
# column 1	:  red
# column 2	:  green
# column 3	:  blue
# returns professionColorCord[name]=[r,g,b]	
	nbline=1
	colorCodes={}
	lines=file.readlines()
	# get rid of first line
	for line in lines[1:]:
		try :
			if not line=="" :
				data=cleanIndata(line)		
				colorCodes[data[0]]=data[1:4]
		except Exception as e :
			print "error  loadProfessionColorCode line "+str(nbline)+" : "+line
			print e
		nbline+=1

	return colorCodes
	
def loadProfessors(file):
# load a csv 
# columns :
#NOM;DISCIPLINE;AUTO DESCRIPTION;FORMATION1;F2;F3;DIPLOME1;D2;PRO1;T1;PRO2;T2;PRO3;T3;PRO4;T4;PRO5;T5;PRO6;T6;PRO7;T7;EXTRA1;T2;EXTRA2;T2;EXTRA3;T3;EXTRA4;T4;EXTRA5;T5;EXTRA6;T6;;;;;;;;#
# this function will extract :  
# colomun 0 :  name			OK
# column 1  : discipline	OK
# column 2	: autodescription = profession principale  OK
# column 3	: formation 
# column 4	: f2
# column 5	: f3
# column 6  : DIPLOME 1
# column 7  : DIPLOME 2
# column 8	: profession	OK 
# column 10	: p2			OK
# column 12	: p3			OK
# column 14	: p4			OK
# column 16	: p5			OK
# column 18	: p6			OK
# column 20	: p7			OK
# column 22	: p8			OK
# column 24	: p9			OK
# column 26	: p10			OK
# column 28	: extra	 
# column 30	: e2			
# column 32	: e3			
# column 34	: e4			
# column 36	: e5			
# column 38	: e6			
# column 40	: e7			
# column 42	: e8			
# column 44	: e9			
# column 46	: e10			
	
	
	profs=[]
	lines = file.readlines()
	nbline=1
	# avoid first line 
	for line in lines[1:]:
		try :
			data=line.split(";")
			
			name=data[0]
			if not name=="" : 
				# formation : not used so far
				formations=[d for d in data[3:6] if not d in ("999","") ]
				#discipline
				disciplineCode=data[1] if not data[1]=="" else "999"
				#professions
				professionsCodes=[d for i,d in enumerate(data[8:27]) if not d in ("999","") and i%2==0]
				# add autodescription
				if not data[2] in("999","") :
					professionsCodes.append(data[2])
				else :	
					print "no autodescription "+name+ " at line "+str(nbline)
					
				if len(professions)>0 : #len(formations)>0 or 
					profs.append([supprime_accent(name),disciplineCode,professionsCodes,nbline])
				else :
					print " no formation or no profession"+name+str(len(formations))+" "+str(len(professions))+ " at line "+str(nbline) 
		except Exception as e:
			print " error loadProfessors line "+str(nbline)+" : "+line
			print e
		nbline+=1

	return profs	
	

def getDotLinkString(node1,node2,weight,label) :
	#return '"'+node1+'"->"'+node2+'",weight='+weight+',label="'+label+'";\n'
	return ''+node1+'->'+node2+'&sep;'+weight+'&sep;'+label+'\n'

def generateProfToProfGraph(profs,professionsCat,file_prefix):
	print "graph prof to prof"
	dotString=""
	idEdge=0
	
	if export_gexf :
		gexf_file=gexf.Gexf("Paul Girard medialab Sciences Po","IEP professers linked by common institutions "+file_prefix)
		graph=gexf_file.addGraph("undirected","static")
		
		for name,formations,professions,id in profs :
			graph.addNode(str(id),name)
		
		
	for prof1, prof2 in [(p1,p2) for i,p1 in enumerate(profs) for p2 in profs[i:] if p1!=p2] :		weight=0		labels=[]
		# pour toutes les professions du prof 1		for profID in prof1[2] :
			# si la profession est présente dans celle du prof2
			if profID in prof2[2] :				# on incrémente le poids du lien et on ajoute la profession au label
				weight+=1				labels.append(professionsCat[profID][3] if not professionsCat[profID][3]=="" else professionsCat[profID][2])		# si on a trouvé des professions communes
		if weight>0 :
			# on ajoute un lien
			if export_gexf  :				graph.addEdge(idEdge,str(prof1[3]),str(prof2[3]),weight=str(weight),label=" | ".join(labels))
			if export_dot :
				dotString+=getDotLinkString(str(prof1[3])+"-"+prof1[0],str(prof2[3])+"-"+prof2[0],str(weight)," | ".join(labels))
			idEdge+=1
	
	if export_gexf  :
		file=open("profiep_profToprof_"+file_prefix+".gexf","w+")
		gexf_file.write(file)
	
	if export_dot :
		file=open("profiep_profToprof.dot","w+")
		file.write("digrpah output {\n"+dotString+"}")
		
		
################### INST TO INST #########################
#
#
##########################################################
def generateInstToInstGraph(profs,professionsCat,file_prefix):
	print "graph inst to inst"
	dotString=""
	idEdge=0
	
	if export_gexf :
		gexf_file=gexf.Gexf("Paul Girard medialab Sciences Po","Institutions linked by common IEP professers "+file_prefix)
		graph=gexf_file.addGraph("undirected","static")
		idAttInstCat2=graph.addNodeAttribute("cat2","","String")
		idAttInstCat1=graph.addNodeAttribute("cat1","","String")
		
		for cat,group1,group2,name,id in professionsCat.values() :
			n=graph.addNode(str(id),name if not name=="" else group2)
			n.addAttribute(idAttInstCat2,group2)
			n.addAttribute(idAttInstCat1,group1)
	
	
	for inst1,inst2 in [(inst1,inst2) for i,inst1 in enumerate(professionsCat.values()) for inst2 in professionsCat.values()[i:] if inst1!=inst2] :		weight=0		labels=[]
		idinst1=inst1[4]
		idinst2=inst2[4]
		
		# pour toutes les professions du prof 1
		for prof in profs :			if idinst1 in prof[2] and idinst2 in prof[2] :
			# si inst1 et inst 2 sont présentes dans les professions du prof				# on incrémente le poids du lien et on ajoute le prof au label
				weight+=1				labels.append(prof[0])		# si on a trouvé des professeurs communs
		if weight>0 :
			# on ajoute un lien
			node1=inst1[3] if not inst1[3]=="" else inst1[2]
			node2=inst2[3] if not inst2[3]=="" else inst2[2]

			if export_gexf :				graph.addEdge(idEdge,inst1[4],inst2[4],weight=str(weight),label=" | ".join(labels))
			if export_dot :
				dotString+=getDotLinkString(node1,node2,str(weight)," | ".join(labels))
			idEdge+=1
				
	if export_gexf  :
		file=open("profiep_instToinst_"+file_prefix+".gexf","w+")
		gexf_file.write(file)
	
	if export_dot :
		file=open("profiep_instToinst.dot","w+")
		file.write("digrpah output {\n"+dotString+"}")

################### PROF TO INST #########################
#
#
##########################################################

def generateProfInstitutionGraph(profs,professions,professionsColors,disciplines,year,gexf):
	print "graph prof to inst"
	dotString=""
	edgesKeygen=autokey()
	

		
	if export_gexf :
		
		graph=gexf.addGraph("undirected","static",year)
		idAttType=graph.addNodeAttribute("type","professer","string")
		idAttInstAgreg=graph.addNodeAttribute("agregation","N/A","string")
		labels_agregation=("champs","groupe","institution")
		idAttInstCat1=graph.addNodeAttribute("champs","professors","string")
		idAttDiscipline=graph.addNodeAttribute("discipline","N/A","string")
#		idAttInstCat1=graph.addNodeAttribute("cat1","","String")
		
  

		

		# professions nodes : no gexf hierarchy but a depth attribute				
		for id,[name,pid,depth] in professions.iteritems() :
			n=graph.addNode("inst_"+str(id),name)
			n.addAttribute(idAttType,"institution")
			n.addAttribute(idAttInstAgreg,labels_agregation[int(depth)])
			ppid=pid if not pid==-1 else id
			while not pid==-1:
				ppid=pid
				pid=professions[ppid][1]
			n.addAttribute(idAttInstCat1,professions[ppid][0])
			try :
				(r,g,b)=professionsColors[professions[ppid][0]]
				n.setColor(r,g,b)
			except :
				print "Warning : couldn't find the color for profession cat :"+professions[ppid][0]		
		
		# professors nodes	
		# get prof color
		(r,g,b)=professionsColors["PROF"]
		for name,disciplineCode,profProfessions,id in profs :
			n=graph.addNode("prof_"+str(id),name)
			n.addAttribute(idAttType,"professer")
			n.addAttribute(idAttDiscipline,disciplines[disciplineCode])
			n.setColor(r,g,b)
			# professors edges
			professionLinked=[]
			for professionID in profProfessions :
				# add edges also to higher depth level professions (false hierarchy) 
				while not professionID=="-1":
					# avoid paralell edges
					if not professionID in professionLinked : 
						graph.addEdge(edgesKeygen.next(),"prof_"+str(id),"inst_"+str(professionID))
						professionLinked.append(professionID)
					# jump up a level by using pid
					professionID=str(professions[professionID][1])
					
						
#				else :
#					raise Exception('EDGES ERROR', professionID+' not found in profession ids')			
				
#	if export_dot :
#		for prof in profs :
#			# pour toutes les professions du prof 1#			for instID in prof[2] :
#					profession=professionsName[instID][0] 
#					dotString+=getDotLinkString(str(prof[3])+"-"+prof[0],profession,"1","")	

	
#	if export_dot :
#		file=open("outdata/profiep_profToinst.dot","w+")
#		file.write("digrpah output {\n"+dotString+"}")	
	
###########  MAIN	#############
#
#
#################################
 	
			
# load categories

verbose=0
# profession
file=open("indata/code_prof.csv")
professions=loadProfessionCode(file)
file.close()
file=open("indata/colors_profession_code.csv")
professionsColors=loadProfessionColorCode(file)
file.close()
#print professions
if verbose :
	for id,[name,groupID,depth] in professions.iteritems() :		
		print (professions[groupID][0] if not groupID==-1 else "-1")+" > "+str(id)+" - "+name
		

# extra

# diciplines
file=open("indata/code_discipline.csv")
disciplines=loadDisciplineCode(file)
file.close()


years=("2008","1996","1986","1970")
for year in years :
	# load prof
	gexf=Gexf("medialab Sciences Po - Paul Girard - Marie Scot","Institutions and professers IEP "+year)

	file=open("indata/"+year+".csv")
	profs=loadProfessors(file)
	print year+": number profs loaded :"+str(len(profs))
	#print professions
	if verbose :
		for name,formations,profProfessions,id in profs :
			print name+"|"+"|".join([professions[p][0] for p in profProfessions])
	# let's gexf this

	key=lambda prof:prof[0]
	profs=sorted(profs, key=key )
	
		
	generateProfInstitutionGraph(profs,professions,professionsColors,disciplines,year,gexf)
	#generateProfToProfGraph(profs,professionsCat,year)
	#generateInstToInstGraph(profs,professionsCat,year)

	if export_gexf :
		file=open("outdata/profiep_profToinst_"+year+".gexf","w+")
		gexf.write(file)







