# -*- coding: utf-8 -*-
import re


verbose=0
export_gexf=1
export_dot=0

if export_gexf :
	import gexf


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
	#     professions[id]=[name,pid]
	#     professionsGroups[(group,pid)]=[id,lastId]
	
	# filtrage des groups vides
	line=filter(lambda g:not g=="",line)
	
	lastId=-1
	for group in line[0:len(line)-2] :
		if not group=="":
			# using (group,lasrId) as key to disambiguish same group name with different fathers
			if not (group,lastId) in professionGroups.keys() :
				id="g"+str(ak.next())
				professionGroups[(group,lastId)]=[id,lastId]
				#print str(lastId)+" > "+str(id)+" - "+group
			lastId=professionGroups[(group,lastId)][0]
	

	name=line[len(line)-2]
	id=line[len(line)-1]
	professions[id]=[name,lastId]
	
	
	#print str(lastId)+" > "+str(id)+" - "+name


def loadCategory(file):
# load a csv 
# colomun 0 : category name
# column 1	: group1 name
# column 2	: group2 name (optional)
# column 3	: entity name
# column 4	:  ID
# returns dict [id]=["name","group1","group2","group3"] ou ["name","group1","group2"]
	
	cat=""
	group1=group2=""
	nbline=1
	codes={}
	lines = file.readlines()
	professionGroupsByName={}
	professions={}
	for line in lines:
		try :
			# get rid of eol
			line=re.sub("[\r\n]","",line)
			data=line.split(";")
			# get rid of trailing spaces
			data=map(lambda s:s.strip(),data)
			# get rid of accent unicode prb to be solved...
			data=map(supprime_accent,data)
			
			# to professions table with pid calculation
			addProfession(data,professions,professionGroupsByName)
			
			#data.reverse()
			#codes[data[0]]=map(supprime_accent,data[1:])
			
			
			#print str(nbline)+":"+data[0]
#			if not data[0]=="" :
#				cat=data[0]
#			else : 
#				group1=data[1] if not data[1]=="" else group1
#				group2=data[2] if not data[2]=="" else group2
#				id=data[3] if len(data)>=4 else ""
#				if not id=="" :
#					name=re.sub("[\r\n]","",data[4]) if len(data)>=5 else ""
#					codes[id]=[supprime_accent(cat),supprime_accent(group1),supprime_accent(group2),supprime_accent(name),id]


		except Exception as e :
			print "error line "+str(nbline)+" : "+line
			print e
		nbline+=1


	
	# reverse key in dict professionsByName to professionsById
	professionGroupsById=dict([[id,[name,pid]] for (name,pid),[id,pid] in professionGroupsByName.iteritems()])

	return (professions,professionGroupsById)
	
def loadProf(file):
# load a csv 
# columns :
#NOM;DISCIPLINE;AUTO DESCRIPTION;FORMATION1;F2;F3;DIPLOME1;D2;PRO1;T1;PRO2;T2;PRO3;T3;PRO4;T4;PRO5;T5;PRO6;T6;PRO7;T7;EXTRA1;T2;EXTRA2;T2;EXTRA3;T3;EXTRA4;T4;EXTRA5;T5;EXTRA6;T6;;;;;;;;#
# this function will extract :  
# colomun 0 :  name
# (...)
# column 2	: autodescription = profession principale  
# column 3	: formation 
# column 4	: f2
# column 5	: f3
# (...)
# column 8	: profession 
# column 10	: p2
# column 12	: p3
# column 14	: p4
# column 16	: p5
# column 18	: p6
# column 20	: p7
	
	
	profs=[]
	lines = file.readlines()
	nbline=1
	# avoid first line 
	for line in lines[1:]:
		try :
			data=line.split(";")
			
			name=data[0]
			formations=[d for d in data[3:6] if not d in ("999","") ]
			professions=[d for i,d in enumerate(data[8:21]) if not d in ("999","") and i%2==0]
			if len(professions)>0 : #len(formations)>0 or 
				profs.append([supprime_accent(name),map(supprime_accent,formations),map(supprime_accent,professions),nbline])
			else :
				print " no formation or no profession"+name+str(len(formations))+" "+str(len(professions)) 
		except Exception as e:
			print " error line "+str(nbline)+" : "+line
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

def generateProfInstitutionGraph(profs,professionsName,professionsGroup,file_prefix):
	print "graph prof to inst"
	dotString=""
	edgesKeygen=autokey()
	

		
	if export_gexf :
		gexf_file=gexf.Gexf("Paul Girard medialab Sciences Po","Institutions and professers IEP "+file_prefix)
		graph=gexf_file.addGraph("undirected","static")
		idAttType=graph.addNodeAttribute("type","professer","String")
		idAttInstCat=graph.addNodeAttribute("cat2","","String")
		idAttInstCat1=graph.addNodeAttribute("cat1","","String")
		
		
		# CHECK PID DEPENDENCES
		pids=[ p[1] for p in professionsName.itervalues()]+[ p[1] for p in professionsGroup.itervalues()]
		pids=filter(lambda v: not v==-1,pids)
		ids=professionsName.keys()+professionsGroup.keys()
		for pid in pids :
			if not pid == -1 and not pid in ids :
				raise Exception('HIERARCHY ERROR', pid+' not found in ids')
  



		# professions nodes

		# heads of hierarchy first
		for id,[name,pid] in professionsGroup.iteritems() :
			if pid==-1 :
				n=graph.addNode("inst_"+str(id),name)
				n.addAttribute(idAttType,"institution")
		# ohters groups after	
		for id,[name,pid] in professionsGroup.iteritems() :
			if not pid==-1 :
				n=graph.addNode("inst_"+str(id),name,pid="inst_"+pid)
				n.addAttribute(idAttType,"institution")

		
		for id,[name,pid] in professionsName.iteritems() :
			n=graph.addNode("inst_"+str(id),name,pid="inst_"+pid)
			n.addAttribute(idAttType,"institution")
			
			#n.addAttribute(idAttInstCat,group2)
			#n.addAttribute(idAttInstCat1,group1)
				
		
		# professors nodes	
		for name,formations,professions,id in profs :
			n=graph.addNode("prof_"+str(id),name)
			n.addAttribute(idAttType,"professer")
			# professors edges
			for professionID in professions :
				if professionID in ids :
					graph.addEdge(edgesKeygen.next(),"prof_"+str(id),"inst_"+str(professionID))
				else :
					raise Exception('EDGES ERROR', professionID+' not found in profession ids')			
				
	if export_dot :
		for prof in profs :
			# pour toutes les professions du prof 1			for instID in prof[2] :
					profession=professionsName[instID][0] 
					dotString+=getDotLinkString(str(prof[3])+"-"+prof[0],profession,"1","")	
	if export_gexf :
		file=open("outdata/profiep_profToinst_"+file_prefix+"_hierarchy.gexf","w+")
		gexf_file.write(file)
	
	if export_dot :
		file=open("outdata/profiep_profToinst.dot","w+")
		file.write("digrpah output {\n"+dotString+"}")	
	
###########  MAIN	#############
#
#
#################################
 	
			
# load categories

verbose=1
# profession
file=open("indata/code_prof.csv")
professionsName,professionsGroup=loadCategory(file)
#print professions
#if verbose :
#	for id,vals in professionsCat.iteritems() :
#		print id+"|"+"|".join(vals)
if verbose :
	for id,[name,groupID] in professionsName.iteritems() :
		print professionsGroup[groupID][0]+" > "+str(id)+" - "+name
	for id,[name,groupID] in professionsGroup.iteritems() :
		
		print (professionsGroup[groupID][0] if not groupID==-1 else "-1")+" > "+str(id)+" - "+name
#print professionsCat.keys()

# formation

# extra



for year in ("2008",) :
	# load prof
	file=open("indata/"+year+".csv")
	profs=loadProf(file)
	print year+": number profs loaded :"+str(len(profs))
	#print professions
	if verbose :
		for name,formations,professions,id in profs :
			print name+"|"+"|".join([professionsName[p][0] for p in professions])
	# let's gexf this

	key=lambda prof:prof[0]
	profs=sorted(profs, key=key )
	
	
	generateProfInstitutionGraph(profs,professionsName,professionsGroup,year)
	#generateProfToProfGraph(profs,professionsCat,year)
	#generateInstToInstGraph(profs,professionsCat,year)










