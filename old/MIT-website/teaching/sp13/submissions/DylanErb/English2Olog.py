import pygraphviz as pgv
from topia.termextract import tag
import pdb
import sys

"English2Olog accepts a text file as the first input argument in the form of..."
"Title"
"Sentence 1"
"Sentence 2"
"."
"."
"."
"Sentence N"

"... and translates those sentences to an Olog. This Olog is saved as a .png file in the directory"
"A verbose output can be toggled on or off by inputting the word verbose as the second argument."
"Any other word such as the word standard will toggle off the verbose output."
"This code is a proof of concept"

#Take the system inputs
textfile = sys.argv[1]
verbose = sys.argv[2]

#Initialize the parts of speech tagger
tagger = tag.Tagger()
tagger.initialize()

#Read in the text file, and store the title and sentences
sentences = {}
line_num = 0
f = open(textfile+'.txt', 'r')
for line in f:
	line_num+=1
	if line_num==1:
		title = line
	elif line.strip() != '':
		sentences[line_num] = tagger(line)
	print line_num, line

#Define a function for counting the number of adjectives in a phrase.
def numadj(x):
	
	NF_tag = tagger(x)
	count = 0
	for POS in NF_tag:
		if (POS[1] == 'JJ')|(POS[1] == 'JJR')|(POS[1] == 'JJS'):
			count += 1
	return count

#Define a function for returning a list of only the adjectives in a phrase.
def returnadj(x):
	
	NF_tag = tagger(x)
	adj = []
	for POS in NF_tag:
		if (POS[1] == 'JJ')|(POS[1] == 'JJR')|(POS[1] == 'JJS'):
			adj.append(POS[0])
	return adj

#Read through each sentence (assuming noun phrase, verb phrase, noun phrase form) and find the two noun phrases and the verb phrase.
nodes = []
edges = []
for line in sentences:
	counter = 0
	NF1 = ''
	NF2 = ''
	VF = ''
	for POS in sentences[line]:
		if counter == 0:
			if (POS[1] == 'VBZ')|(POS[1] == 'VB')|(POS[1] =='VBD')|(POS[1] =='VBG')|(POS[1] =='VBP')|(POS[1] =='VBN'):
				counter += 1
			elif NF1 == '':
				NF1 += POS[0].lower()
			else:
				NF1 += ' '+POS[0]
		if counter == 1:
			if (POS[0] == 'a') | (POS[0] == 'an'):
				counter += 1
			elif VF == '':
				VF += POS[0]
			elif POS[1] != 'RB':
				VF += ' '+POS[0]
		if counter == 2:
			if POS[0] == '.':
				counter += 1
			elif NF2 == '':
				NF2 += POS[0]
			else:
				NF2 += ' '+POS[0]
	
	#Add the all the noun phrases as nodes, and all the verb phrases as edges between those nodes.
	nodes.append(NF1)
	nodes.append(NF2)
	edges.append([NF1,NF2,VF])
	
print sentences
#pdb.set_trace()

#Go through the nodes and edges, and try to make inferences about other relationships.
if verbose=='verbose':
	#strip out adverbs after noun phrases
	for NF in nodes:
		SNF = ''
		flag = 0
		nounflag = 0
		NF_tag = tagger(NF)
		for POS in NF_tag:
			if flag == 0:
				if SNF == '':
					SNF += POS[0]
				else:
					if nounflag == 0:
						if POS[1] != 'NN':
							SNF += ' '+POS[0]
						else:
							nounflag = 1
							SNF += ' '+POS[0]
					else:
						if POS[1] != 'RB':
							SNF += ' '+POS[0]
						else:
							flag = 1
		if flag == 1:
			nodes.remove(NF)
			nodes.append(SNF)
			newedge = []
			for edge in edges:
				newedge = edge
				edgeflag = 0
				if edge[0] == NF:
					newedge[0] = SNF
					edgeflag = 1
				if edge[1] == NF:
					newedge[1] = SNF
					edgeflag = 1
				if edgeflag == 1:
						edges.remove(edge)
						edges.append(newedge)
	
	#strip out prepositional phrases, and make more nodes and edges
	for NF in nodes:
		SNF = ''
		flag = 0
		NF_tag = tagger(NF)
		for POS in NF_tag:
			if flag == 0:
				if SNF == '':
					SNF += POS[0]
				else:
					if POS[1] != 'IN':
						SNF += ' '+POS[0]
					else:
						flag = 1
		if flag == 1:
			nodes.append(SNF)
			edges.append([NF,SNF,'is'])
	
	#strip out adjectives one at a time, and throw the result to the end of the list
	for NF in nodes:
		if numadj(NF)>2:
			adjectives = returnadj(NF)
			adjcount = 0
			for adj in adjectives:
				adjcount += 1
				SNF = ''
				NF_tag = tagger(NF)
				for POS in NF_tag:
					if POS[0] != adj:
						if adjcount != numadj(NF):
							if SNF == '':
								SNF += POS[0]
							else:
								SNF += ' '+POS[0]
						elif POS[1] != 'CC':
							if SNF == '':
								SNF += POS[0]
							else:
								SNF += ' '+POS[0]
						
				nodes.append(SNF)
				edges.append([NF,SNF,'is'])
	
	#strip out prepositional phrases, and make more nodes and edges
	for NF in nodes:
		SNF = ''
		flag = 0
		NF_tag = tagger(NF)
		for POS in NF_tag:
			if flag == 0:
				if SNF == '':
					SNF += POS[0]
				else:
					if POS[1] != 'IN':
						SNF += ' '+POS[0]
					else:
						flag = 1
		if flag == 1:
			nodes.append(SNF)
			edges.append([NF,SNF,'is'])
	
	vowels = "aeiuoAEIOU"
	
	#strip out one adverb, and make more nodes and edges
	for NF in nodes:
		SNF = ''
		flag = 0
		NF_tag = tagger(NF)
		if len(NF_tag)>3:
			if (NF_tag[0][1]=='DT')&(NF_tag[1][1]=='RB')&(NF_tag[2][1]=='JJ')&(NF_tag[3][1]=='NN'):
				if NF_tag[2][0][0] in vowels:
					SNF = 'an '+NF_tag[2][0]+' '+NF_tag[3][0]
				else:
					SNF = 'a '+NF_tag[2][0]+' '+NF_tag[3][0]
		if SNF != '':
			nodes.append(SNF)
			edges.append([NF,SNF,'is'])
	
	#strip out one adjective from two adjective phrases, and make more nodes and edges
	for NF in nodes:
		SNF1 = ''
		SNF2 = ''
		flag = 0
		NF_tag = tagger(NF)
		if len(NF_tag)>4:
			if (NF_tag[0][1]=='DT')&((NF_tag[1][1]=='JJ')|(NF_tag[1][1]=='JJR')|(NF_tag[1][1]=='JJS'))&((NF_tag[2][1]=='JJ')|(NF_tag[2][1]=='JJR')|(NF_tag[2][1]=='JJS'))&(NF_tag[3][1]=='CC')&(NF_tag[4][1]=='NN'):
				NF_tag = [NF_tag[0],NF_tag[1],NF_tag[3],NF_tag[2],NF_tag[4]]
				SNF = ''
				for POS in NF_tag:
					if SNF == '':
						SNF += POS[0]
					else:
						SNF += ' '+POS[0]
				#pdb.set_trace()
				nodes.remove(NF)
				nodes.append(SNF)
				newedge = []
				for edge in edges:
					#pdb.set_trace()
					newedge = edge
					edgeflag = 0
					if edge[0] == NF:
						newedge[0] = SNF
						edgeflag = 1
					if edge[1] == NF:
						newedge[1] = SNF
						edgeflag = 1
					if edgeflag == 1:
						edges.remove(edge)
						edges.append(newedge)
				#pdb.set_trace()
				NF = SNF
			if (NF_tag[0][1]=='DT')&((NF_tag[1][1]=='JJ')|(NF_tag[1][1]=='JJR')|(NF_tag[1][1]=='JJS'))&(NF_tag[2][1]=='CC')&((NF_tag[3][1]=='JJ')|(NF_tag[3][1]=='JJR')|(NF_tag[3][1]=='JJS'))&(NF_tag[4][1]=='NN'):
				if NF_tag[1][0][0] in vowels:
					SNF1 = 'an '+NF_tag[1][0] +' '+NF_tag[4][0]
				else:
					SNF1 = 'a '+NF_tag[1][0] +' '+NF_tag[4][0]
				
				if NF_tag[3][0][0] in vowels:
					SNF2 = 'an '+NF_tag[3][0] +' '+NF_tag[4][0]
				else:
					SNF2 = 'a '+NF_tag[3][0] +' '+NF_tag[4][0]
		elif len(NF_tag)>3:
			if (NF_tag[0][1]=='DT')&(NF_tag[1][1]=='JJ')&(NF_tag[2][1]=='JJ')&(NF_tag[3][1]=='NN'):
				if NF_tag[1][0][0] in vowels:
					SNF1 = 'an '+NF_tag[1][0] +' '+NF_tag[3][0]
				else:
					SNF1 = 'a '+NF_tag[1][0] +' '+NF_tag[3][0]
				
				if NF_tag[3][0][0] in vowels:
					SNF2 = 'an '+NF_tag[2][0] +' '+NF_tag[3][0]
				else:
					SNF2 = 'a '+NF_tag[2][0] +' '+NF_tag[3][0]
		if SNF1 != '':
			nodes.append(SNF1)
			nodes.append(SNF2)
			edges.append([NF,SNF1,'is'])
			edges.append([NF,SNF2,'is'])
	
	#strip out one adjective, and make more nodes and edges
	for NF in nodes:
		SNF = ''
		flag = 0
		NF_tag = tagger(NF)
		if len(NF_tag)>2:
			#pdb.set_trace()
			if (NF_tag[0][1]=='DT')&((NF_tag[1][1]=='JJ')|(NF_tag[1][1]=='JJR')|(NF_tag[1][1]=='JJS'))&(NF_tag[2][1]=='NN'):
				if NF_tag[2][0][0] in vowels:
					SNF = 'an '+NF_tag[2][0]
				else:
					SNF = 'a '+NF_tag[2][0] 
		if SNF != '':
			nodes.append(SNF)
			edges.append([NF,SNF,'is'])

#Weed out all non unique edges
unique_edges = []
for x in edges:
	if x not in unique_edges:
		unique_edges.append(x)      

#Weed out all non unique nodes
unique_nodes = []
for x in nodes:
	if x not in unique_nodes:
		unique_nodes.append(x) 
			
print nodes
print edges

#make the pretty graph
G=pgv.AGraph()
G=pgv.AGraph(strict=False,directed=True)

G.add_nodes_from(unique_nodes)

for edge in unique_edges:
	G.add_edge(edge[0],edge[1],label=edge[2])

sorted(G.edges(keys=True))

G.graph_attr['label']=title
G.graph_attr['labelloc']='t'
G.node_attr['shape']='rectangle'

s=G.string()
G.write(textfile+".dot")

G.layout(prog = 'dot')
G.draw(textfile+'.png')