#!/usr/bin/python
##
## anonymizerWithCoords <epanet-input-file> <anonymized-output-file> <map-output-file> <baseline-elevation>
##

import os
import sys
import string

if len(sys.argv) != 5:
  print "Usage: anonymizerWithCoords <epanet-input-file> <anonymized-output-file> <map-output-file> <baseline-elevation>"
  sys.exit(1)

# section IDs (programmatic, not EPANET)
# correctness of comments is not guaranteed! nor, for that matter, is the correctness of the program itself!!!
# unknown=0 ; eliminate section contents, spit out a warning
# backdrop=1 ; no labels. 
# controls=2 ; uses link and node ID labels
# coordinates=3 ; uses node ID labels
# curves=4 ; defines curve ID labels
# demands=5 ; uses junction ID labels, demand pattern IDs. 
# emitters=6 ; uses junction ID labels
# energy=7 ; uses pump ID labels
# junctions=8 ; defines junction ID labels, uses demand pattern IDs
# labels=9 ; embeds text labels and possibly associates them with node IDs (eliminate)
# mixing=10 ; uses tank ID labels
# options=11 ; 
# patterns=12 ; defines pattern ID labels
# pipes=13 ; defines pipe ID labels, uses node ID labels
# pumps=14 ; defines pump ID labels, uses node ID labels, uses head ID and pattern ID labels in keyword/value sections
# quality=15 ; uses node ID labels
# reactions=16 ; uses pipe ID labels
# report=17 ; 
# reservoir=18 ; defines reservoir ID labels, uses pump head ID labels
# rules=19 ; 
# sources=20 ; uses node ID labels, optionally uses pattern ID labels
# status=21 ; uses link ID labels
# tags=22 ; uses node and/or link ID labels - text is a security issue, so just replace with a DELETED text string
# tanks=23 ; defines tank ID labels, uses curve ID labels
# times=24 ; defines no labels, uses no labels
# title=25 ; text is a security issue - just replace with "DELETED" text string
# valves=26 ; defines valve ID labels, uses node ID labels
# vertices=27 ; uses link ID labels - probably should replace coordinates with 0.0
# end=28 ; empty - just a keyword

nodeMap = {}     # maps original node IDs to anonymized node IDs
linkMap = {}     # maps original link IDs to anonymized link IDs
curveMap = {}    # maps original curve IDs to anonymized curve IDs 
patternMap = {}  # maps original pattern IDs to anonymized pattern IDs 
ruleMap = {}     # maps original rule IDs to anonymized rule IDs

baselineElevation=eval(sys.argv[4])

print "Baseline elevation="+`baselineElevation`

currentSection=0 

# first pass extracts all labels and maps them to anonymizer labels

epanetFilePass1=open(sys.argv[1],'r')

noop1=0

for line in epanetFilePass1.readlines():
  line=string.strip(line)
  if(len(line)>0):
    if(line[0]==';'):
#      print "Skipping comment - text|  "+line
      noop1=noop1+1
    elif(line[0]=='['):
      if(line=="[BACKDROP]"):
        currentSection=1
      elif(line=="[CONTROLS]"):
        currentSection=2
      elif(line=="[COORDINATES]"):
        currentSection=3
      elif(line=="[CURVES]"):
        currentSection=4
      elif(line=="[DEMANDS]"):
        currentSection=5
      elif(line=="[EMITTERS]"):
        currentSection=6
      elif(line=="[ENERGY]"):
        currentSection=7
      elif(line=="[JUNCTIONS]"):
        currentSection=8
      elif(line=="[LABELS]"):
        currentSection=9
      elif(line=="[MIXING]"):
        currentSection=10
      elif(line=="[OPTIONS]"):
        currentSection=11
      elif(line=="[PATTERNS]"):
        currentSection=12
      elif(line=="[PIPES]"):
        currentSection=13
      elif(line=="[PUMPS]"):
        currentSection=14
      elif(line=="[QUALITY]"):
        currentSection=15
      elif(line=="[REACTIONS]"):
        currentSection=16
      elif(line=="[REPORT]"):
        currentSection=17
      elif(line=="[RESERVOIRS]"):
        currentSection=18
      elif(line=="[RULES]"):
        currentSection=19
      elif(line=="[SOURCES]"):
        currentSection=20
      elif(line=="[STATUS]"):
        currentSection=21
      elif(line=="[TAGS]"):
        currentSection=22
      elif(line=="[TANKS]"):
        currentSection=23
      elif(line=="[TIMES]"):
        currentSection=24
      elif(line=="[TITLE]"):
        currentSection=25
      elif(line=="[VALVES]"):
        currentSection=26
      elif(line=="[VERTICES]"):
        currentSection=27
      elif(line=="[END]"):
        currentSection=28
      else:
	print "***UNKNOWN SECTION ENCOUNTERED - NAME="+line
        currentSection=0
    else:
      pieces=string.split(line)
      if(currentSection==4):
        name=string.strip(pieces[0])
	if(not curveMap.has_key(name)):
	  curveMap[name]="CURVE-"+`len(curveMap)`
#	  print "Mapping curve ID="+name+" to ID="+`curveMap[name]`
      elif(currentSection==8):
	# multiple entries with the same label are not allowed
	name=string.strip(pieces[0])
	nodeMap[name]="JUNCTION-"+`len(nodeMap)`
#	print "Mapping junction ID="+name+" to ID="+`nodeMap[name]`	
      elif(currentSection==12):
	name=string.strip(pieces[0])
	if(not patternMap.has_key(name)):
	  patternMap[name]="PATTERN-"+`len(patternMap)`
#  	  print "Mapping pattern ID="+name+" to ID="+`patternMap[name]`		
      elif(currentSection==13):
	# multiple entries with the same label are not allowed
	name=string.strip(pieces[0])
	linkMap[name]="LINK-"+`len(linkMap)`
#	print "Mapping link ID="+name+" to ID="+`linkMap[name]`		
      elif(currentSection==14):
	# multiple entries with the same label are not allowed
	name=string.strip(pieces[0])
	linkMap[name]="PUMP-"+`len(linkMap)`
#	print "Mapping pump ID="+name+" to ID="+`linkMap[name]`		
      elif(currentSection==18):
	# multiple entries with the same label are not allowed
	name=string.strip(pieces[0])
	nodeMap[name]="RESERVOIR-"+`len(nodeMap)`
#	print "Mapping reservoir ID="+name+" to ID="+`nodeMap[name]`		
      elif(currentSection==19):
	if(string.upper(pieces[0])=="RULE"):
  	  name=string.strip(pieces[1])
	  ruleMap[name]="RULE-"+`len(ruleMap)`
#	  print "Mapping rule ID="+name+" to ID="+`ruleMap[name]`		
      elif(currentSection==23):
	# multiple entries with the same label are not allowed
	name=string.strip(pieces[0])
	nodeMap[name]="TANK-"+`len(nodeMap)`
#	print "Mapping tank ID="+name+" to ID="+`nodeMap[name]`		
      elif(currentSection==26):
	# multiple entries with the same label are not allowed
	name=string.strip(pieces[0])
	linkMap[name]="VALVE-"+`len(linkMap)`
#	print "Mapping valve ID="+name+" to ID="+`linkMap[name]`		

epanetFilePass1.close()

# second pass performs the substitutions 

epanetFilePass2=open(sys.argv[1],'r')
anonymizedOutputFile=open(sys.argv[2],'w')
mapOutputFile=open(sys.argv[3],'w')

mapOutputFile.write("[NODES]\n")
for node in nodeMap:
  mapOutputFile.write(node+" "+nodeMap[node]+"\n")
mapOutputFile.write("\n")
mapOutputFile.write("[LINKS]\n")
for link in linkMap:
  mapOutputFile.write(link+" "+linkMap[link]+"\n")
mapOutputFile.write("\n")
mapOutputFile.write("[CURVES]\n")
for curve in curveMap:
  mapOutputFile.write(curve+" "+curveMap[curve]+"\n")
mapOutputFile.write("\n")
mapOutputFile.write("[PATTERNS]\n")
for pattern in patternMap:
  mapOutputFile.write(pattern+" "+patternMap[pattern]+"\n")
mapOutputFile.write("\n")
mapOutputFile.write("[RULES]\n")
for rule in ruleMap:
  mapOutputFile.write(rule+" "+ruleMap[rule]+"\n")
mapOutputFile.write("\n")
# The COORDINATES section is the only section that is written during the second pass
mapOutputFile.write("[COORDINATES]\n")

noop2=0

for line in epanetFilePass2.readlines():
  line=string.strip(line)
  print "Processing line= "+line
  if(len(line)>0):
    if(line[0]==';'):
#      print "Skipping comment - text|  "+line
      noop2=noop2+1
    elif(line[0]=='['):
      if(line=="[BACKDROP]"):
        currentSection=1
      elif(line=="[CONTROLS]"):
        currentSection=2
      elif(line=="[COORDINATES]"):
        currentSection=3
      elif(line=="[CURVES]"):
        currentSection=4
      elif(line=="[DEMANDS]"):
        currentSection=5
      elif(line=="[EMITTERS]"):
        currentSection=6
      elif(line=="[ENERGY]"):
        currentSection=7
      elif(line=="[JUNCTIONS]"):
        currentSection=8
      elif(line=="[LABELS]"):
        currentSection=9
      elif(line=="[MIXING]"):
        currentSection=10
      elif(line=="[OPTIONS]"):
        currentSection=11
      elif(line=="[PATTERNS]"):
        currentSection=12
      elif(line=="[PIPES]"):
        currentSection=13
      elif(line=="[PUMPS]"):
        currentSection=14
      elif(line=="[QUALITY]"):
        currentSection=15
      elif(line=="[REACTIONS]"):
        currentSection=16
      elif(line=="[REPORT]"):
        currentSection=17
      elif(line=="[RESERVOIRS]"):
        currentSection=18
      elif(line=="[RULES]"):
        currentSection=19
      elif(line=="[SOURCES]"):
        currentSection=20
      elif(line=="[STATUS]"):
        currentSection=21
      elif(line=="[TAGS]"):
        currentSection=22
      elif(line=="[TANKS]"):
        currentSection=23
      elif(line=="[TIMES]"):
        currentSection=24
      elif(line=="[TITLE]"):
        currentSection=25
      elif(line=="[VALVES]"):
        currentSection=26
      elif(line=="[VERTICES]"):
        currentSection=27
      elif(line=="[END]"):
        currentSection=28
      else:
	print "***UNKNOWN SECTION ENCOUNTERED - NAME="+line
        currentSection=0
      if(currentSection!=25):
	anonymizedOutputFile.write("\n")
      pieces=string.split(line)
      anonymizedOutputFile.write(string.strip(pieces[0])+"\n")
    else:
      pieces=string.split(string.split(line,';')[0])
      if(currentSection==1): # BACKDROP
	# all backdrop information is stripped for security reasons
	noop2=noop2+1
      elif(currentSection==2): # CONTROLS
	# anonymize the node and link ids
	if(len(pieces)==8):
  	  anonymizedOutputFile.write(pieces[0]+" "+linkMap[pieces[1]]+" "+pieces[2]+" "+pieces[3]+" "+pieces[4])
	  anonymizedOutputFile.write(" "+nodeMap[pieces[5]]+" "+pieces[6]+" "+pieces[7]+"\n")	
	elif(len(pieces)==6):
  	  anonymizedOutputFile.write(pieces[0]+" "+linkMap[pieces[1]]+" "+pieces[2]+" "+pieces[3]+" "+pieces[4])
	  anonymizedOutputFile.write(" "+pieces[5]+"\n")
	elif(len(pieces)==7):
  	  anonymizedOutputFile.write(pieces[0]+" "+linkMap[pieces[1]]+" "+pieces[2]+" "+pieces[3]+" "+pieces[4])
	  anonymizedOutputFile.write(" "+pieces[5]+" "+pieces[6]+"\n")
	else:
	  print "***Illegally formatted line in CONTROLS section - ignored| "+line
      elif(currentSection==3): # COORDINATES
	# all coordinates are stripped for security reasons
	mapOutputFile.write(nodeMap[pieces[0]]+" "+pieces[1]+" "+pieces[2]+"\n")
	anonymizedOutputFile.write(nodeMap[pieces[0]]+" "+pieces[1]+" "+pieces[2]+"\n")
	noop2=noop2+1
      elif(currentSection==4): # CURVES
	# anonymize the curve id label
	anonymizedOutputFile.write(curveMap[pieces[0]]+" "+pieces[1]+" "+pieces[2]+"\n")
      elif(currentSection==5): # DEMANDS
	# anonymize the junction id label an the optimal demand pattern id label
	# I've assumed that the optional category embedded in the comment field is bogus (and is a security risk anyway)
	anonymizedOutputFile.write(nodeMap[pieces[0]]+" "+pieces[1])
	if(len(pieces)==3):
	  anonymizedOutputFile.write(" "+patternMap[pieces[2]])
	anonymizedOutputFile.write("\n")
      elif(currentSection==6): # EMITTERS
	# anonymize the junction id label
	anonymizedOutputFile.write(nodeMap[pieces[0]]+" "+pieces[1]+"\n")
      elif(currentSection==7): # ENERGY
	# anonymize pattern and pump ids in particular contexts
	if(string.upper(pieces[0])=="GLOBAL"):
	  if(string.upper(pieces[1])=="PATTERN"):
            anonymizedOutputFile.write(pieces[0]+" "+pieces[1]+" "+patternMap[pieces[2]]+"\n")
	  else:
            anonymizedOutputFile.write(pieces[0]+" "+pieces[1]+" "+pieces[2]+"\n")          
	elif(string.upper(pieces[0])=="PUMP"):
	  if(string.upper(pieces[2])=="PATTERN"):
            anonymizedOutputFile.write(pieces[0]+" "+linkMap[pieces[2]]+" "+patternMap[pieces[3]]+"\n")
	  else:
            anonymizedOutputFile.write(pieces[0]+" "+linkMap[pieces[2]]+" "+pieces[3]+"\n")          
	elif(string.upper(pieces[0])=="DEMAND"):
          anonymizedOutputFile.write(pieces[0]+" "+pieces[1]+" "+pieces[2]+"\n")
	else:
	  print "***Illegally formatted line in ENERGY section - ignored| "+line
      elif(currentSection==8): # JUNCTIONS
	# anonymize the junction id label
	anonymizedOutputFile.write(nodeMap[pieces[0]]+" ")
	thisElevation=eval(pieces[1])
	thisElevation=thisElevation+baselineElevation;
	anonymizedOutputFile.write(`thisElevation`)
	if(len(pieces)>=3):
	  anonymizedOutputFile.write(" "+pieces[2])
	if(len(pieces)==4):
	  anonymizedOutputFile.write(" "+patternMap[pieces[3]])
	anonymizedOutputFile.write("\n")
      elif(currentSection==9): # LABELS
	# all labeling information is stripped for security purposes
	noop2=noop2+1
      elif(currentSection==10): # MIXING
	anonymizedOutputFile.write(nodeMap[pieces[0]]+" "+pieces[1])
	if(len(pieces)==3):
	  anonymizedOutputFile.write(" "+pieces[2])
	anonymizedOutputFile.write("\n")
      elif(currentSection==11): # OPTIONS
	# if the option is pattern, replace the pattern id; map files are removed
	if(string.upper(pieces[0])=="PATTERN"):
	  try:
	    mappedPattern=patternMap[pieces[1]]
  	    anonymizedOutputFile.write(pieces[0]+" "+mappedPattern)
          except KeyError:
            print "***WARNING - Undefined pattern "+pieces[1]+" referenced in options section - passed through to anonymized output file"
            anonymizedOutputFile.write(pieces[0]+" "+pieces[1])
	elif(len(pieces)==3 and string.upper(pieces[0])=="QUALITY" and string.upper(pieces[1])=="TRACE"):
	  anonymizedOutputFile.write(pieces[0]+" "+pieces[1]+" "+nodeMap[pieces[2]])
	elif(string.upper(pieces[0])=="MAP"):
	  noop2=noop2+1
	elif(string.upper(pieces[0])=="HYDRAULICS"):
	  noop2=noop2+1
	else:
  	  anonymizedOutputFile.write(pieces[0])
	  for i in range(1,len(pieces)):
	    anonymizedOutputFile.write(" "+pieces[i])	
        anonymizedOutputFile.write("\n")
      elif(currentSection==12): # PATTERNS
	# anonymize the tank id label
	anonymizedOutputFile.write(patternMap[pieces[0]])
	for i in range(1,len(pieces)):
	  anonymizedOutputFile.write(" "+pieces[i])
	anonymizedOutputFile.write("\n")
      elif(currentSection==13): # PIPES
	# anonymize the pipe label, node start, and node end ids
	anonymizedOutputFile.write(linkMap[pieces[0]]+" "+nodeMap[pieces[1]]+" "+nodeMap[pieces[2]])
        for i in range(3,len(pieces)):
          anonymizedOutputFile.write(" "+pieces[i])	
        anonymizedOutputFile.write("\n")
      elif(currentSection==14): # PUMPS
	# anonymize the pump, start node, and end node labels - also the optional head/pattern labels
	anonymizedOutputFile.write(linkMap[pieces[0]]+" "+nodeMap[pieces[1]]+" "+nodeMap[pieces[2]])
	numoptional=(len(pieces)-3)/2
	for i in range(0,numoptional):
	  if(string.upper(pieces[(i*2)+3])=="POWER"):
            anonymizedOutputFile.write(" "+pieces[(i*2)+3]+" "+pieces[(i*2)+4])
	  elif(string.upper(pieces[(i*2)+3])=="HEAD"):
            anonymizedOutputFile.write(" "+pieces[(i*2)+3]+" "+curveMap[pieces[(i*2)+4]])
	  elif(string.upper(pieces[(i*2)+3])=="SPEED"):
            anonymizedOutputFile.write(" "+pieces[(i*2)+3]+" "+pieces[(i*2)+4])      
	  else: # PATTERN
            anonymizedOutputFile.write(" "+pieces[(i*2)+3]+" "+patternMap[pieces[(i*2)+4]])	  
	anonymizedOutputFile.write("\n")
      elif(currentSection==15): # QUALITY
	# anonymize the node id label
	anonymizedOutputFile.write(nodeMap[pieces[0]]+" "+pieces[1]+"\n")
      elif(currentSection==16): # REACTIONS
	if(string.upper(pieces[0])=="TANK"):
	  anonymizedOutputFile.write(pieces[0]+" "+nodeMap[pieces[1]]+" "+pieces[2])	
	elif(string.upper(pieces[0])=="BULK" or string.upper(pieces[0])=="WALL"):
	  anonymizedOutputFile.write(pieces[0]+" "+linkMap[pieces[1]]+" "+pieces[2])	
	else:
	  anonymizedOutputFile.write(pieces[0])
	  for i in range(1,len(pieces)):
  	    anonymizedOutputFile.write(" "+pieces[i])	    
	anonymizedOutputFile.write("\n")
      elif(currentSection==17): # REPORT
	if(string.upper(pieces[0])=="FILE"):
	  anonymizedOutputFile.write(pieces[0]+"DELETED")	
	elif(string.upper(pieces[0])=="NODES" and string.upper(pieces[1])!="NONE" and string.upper(pieces[1])!="ALL"):
	  anonymizedOutputFile.write(pieces[0])
	  for i in range(1,len(pieces)):
  	    anonymizedOutputFile.write(" "+nodeMap[pieces[i]])	    
	elif(string.upper(pieces[0])=="LINKS" and string.upper(pieces[1])!="NONE" and string.upper(pieces[1])!="ALL"):
	  anonymizedOutputFile.write(pieces[0])
	  for i in range(1,len(pieces)):
  	    anonymizedOutputFile.write(" "+linkMap[pieces[i]])	    
	else:
	  anonymizedOutputFile.write(pieces[0])
	  for i in range(1,len(pieces)):
  	    anonymizedOutputFile.write(" "+pieces[i])	    
	anonymizedOutputFile.write("\n")
      elif(currentSection==18): # RESERVOIR
	# anonymize the reservoir id label and the optimal head pattern id
	# the head needs to be offset by the elevation offset
	thisElevation=eval(pieces[1])
	thisElevation=thisElevation+baselineElevation;
	anonymizedOutputFile.write(nodeMap[pieces[0]]+" "+`thisElevation`)
	if(len(pieces)==3):
	  anonymizedOutputFile.write(" "+patternMap[pieces[2]])
	anonymizedOutputFile.write("\n")
      elif(currentSection==19): # RULES
	if(string.upper(pieces[0])=="RULE"):
	  anonymizedOutputFile.write("\n")
	  anonymizedOutputFile.write(pieces[0]+" "+ruleMap[pieces[1]])
	elif(string.upper(pieces[0])=="PRIORITY"):
	  anonymizedOutputFile.write(pieces[0]+" "+pieces[1])
        else:
	  anonymizedOutputFile.write(pieces[0]+" "+pieces[1]+" ")
          if(string.upper(pieces[1])=="NODE" or string.upper(pieces[1])=="JUNCTION" or 
             string.upper(pieces[1])=="RESERVOIR" or string.upper(pieces[1])=="TANK"):
            anonymizedOutputFile.write(nodeMap[pieces[2]])
	  elif(string.upper(pieces[1])=="LINK" or string.upper(pieces[1])=="PIPE" or 
	       string.upper(pieces[1])=="PUMP" or string.upper(pieces[1])=="VALVE"):
            anonymizedOutputFile.write(linkMap[pieces[2]])	
	  else:
            anonymizedOutputFile.write(pieces[2])		
          headConditionEntry=0
          for i in range(3,len(pieces)):
	    if(string.upper(pieces[i])=="HEAD"):
	      headConditionEntry=1
            if((i==(len(pieces)-1)) and (headConditionEntry==1)):
    	      thisElevation=eval(pieces[i])
	      thisElevation=thisElevation+baselineElevation;    
              anonymizedOutputFile.write(" "+`thisElevation`)
	    else:
              anonymizedOutputFile.write(" "+pieces[i])
	anonymizedOutputFile.write("\n")
      elif(currentSection==20): # SOURCES
	# anonymize the node id label and the optional pattern id label
	anonymizedOutputFile.write(nodeMap[pieces[0]]+" "+pieces[1]+" "+pieces[2])
	if(len(pieces)==4):
	  anonymizedOutputFile.write(" "+patternMap[pieces[3]])
	anonymizedOutputFile.write("\n")
      elif(currentSection==21): # STATUS
	# anonymize the link id
	anonymizedOutputFile.write(linkMap[pieces[0]]+" "+pieces[1]+"\n")	
      elif(currentSection==22): # TAGS
	# annotations are eliminated for security reasons
	noop2=noop2+1
      elif(currentSection==23): # TANKS
	# anonymize both the tank id and the optional volume curve id
	thisElevation=eval(pieces[1])
	thisElevation=thisElevation+baselineElevation;
	anonymizedOutputFile.write(nodeMap[pieces[0]]+" "+`thisElevation`+" "+pieces[2]+" "+pieces[3]+" ")
	anonymizedOutputFile.write(pieces[4]+" "+pieces[5]+" "+pieces[6]+" ")
	if(len(pieces)==8):
	  anonymizedOutputFile.write(curveMap[pieces[7]])
	anonymizedOutputFile.write("\n")
      elif(currentSection==24): # TIMES
	# nothing to anonymize - pass through w/o comments
	anonymizedOutputFile.write(pieces[0])
	for i in range(1,len(pieces)):
	  anonymizedOutputFile.write(" "+pieces[i])
	anonymizedOutputFile.write("\n")
      elif(currentSection==25): # TITLE
	# title text is eliminated for security reasons
	noop2=noop2+1
      elif(currentSection==26): # VALVES
	# need to anonymize the valve, start node, and end node labels
	anonymizedOutputFile.write(linkMap[pieces[0]]+" "+nodeMap[pieces[1]]+" "+nodeMap[pieces[2]])	
	anonymizedOutputFile.write(" "+pieces[3]+" "+pieces[4]+" "+pieces[5]+" "+pieces[6]+"\n")
      elif(currentSection==27): # VERTICES
	# coordinate information/annotations are stripped for security purposes
	noop2=noop2+1
      elif(currentSection==28): # END
	anonymizedOutputFile.write("\n")

epanetFilePass2.close()
anonymizedOutputFile.close()
mapOutputFile.close()

