#!/usr/bin/python
# -*- coding: utf-8 -*-
import sys
import codecs
reload(sys)
sys.setdefaultencoding("utf-8")
from util import *
from extract_relations import *
from ssf_api import *
from letter import *
from merge_annotations import *
from annotated_data import *
from feature import *
from models import *

from tree_api import *

from sys import getsizeof
from memory_profiler import profile

def searchConn(conn,wordList):
	conn=conn.split()
	pos=0
	posList=[]
	while(pos<len(wordList)-len(conn)+1):
		found=True
		for j in range(0,len(conn)):
			if(conn[j]!=wordList[pos+j].word):
				found=False
				break
		if(found):
			posList.append((pos,pos+len(conn)-1))
			pos+=len(conn)
		else:
			pos+=1
	return posList

def searchSplitConn(conn1,conn2,wordList,sentenceList):
	conn1=conn1.split()
	conn2=conn2.split()
	posList=[]
	for sentence in sentenceList:
		p1=[]
		wordPos=sentence.wordNumList[0]
		while(wordPos < sentence.wordNumList[-1]-len(conn1)+2):
			found=True
			for j in range(0,len(conn1)):
				if(conn1[j]!=wordList[wordPos+j].word):
					found=False
					break
			if(found):
				p1.append(wordPos)
				wordPos+=len(conn1)
			else:
			 	wordPos+=1
		if(len(p1)==0):
			continue
		p2=[]
		wordPos=sentence.wordNumList[0]
		while(wordPos < sentence.wordNumList[-1]-len(conn2)+2):
			found=True
			for j in range(0,len(conn2)):
				if(conn2[j]!=wordList[wordPos+j].word):
					found=False
					break
			if(found):
				p2.append(wordPos)
				wordPos+=len(conn2)
			else:
			 	wordPos+=1
		if(len(p2)==0):
			continue
		for i in p1:
		 	for j in p2:
				if(i+len(conn1)<=j):
					posList.append((i,j))
	return posList


def convert_span(i,conn):
	l=[]
	for j in range(i,i+len(conn.split())):
		l.append(j)
	return l
def identifyConnectives(discourseFileInst,connList,connSplitList):
	positiveSetSingle=[]
	negativeSetSingle=[]
	wordList=discourseFileInst.globalWordList
	sentenceList=discourseFileInst.sentenceList
	for conn in connList:
		posList=searchConn(conn,wordList)
		if(len(posList)==0):
			continue
#		print "found ",conn,len(posList)
		for i in posList:
#			for j in range(i,i+len(conn.split())):
#				print wordList[j].chunkNum,
#			print "\n"
	#		if(wordList[i[0]].conn and (i[0]==0 or not wordList[i[0]-1].conn)  and (i[1]==len(wordList)-1 or not wordList[i[1]+1].conn)):
			if(wordList[i[0]].conn and (i[0]==0 or not wordList[i[0]-1].conn)):
#					print "lol error",conn
				if(i[1]!=len(wordList)-1 and wordList[i[1]+1].conn):
					print "lol error",conn
				positiveSetSingle.append(convert_span(i[0],conn))
#				print "Yes",wordList[i].sense
			else:
				negativeSetSingle.append(convert_span(i[0],conn))
#			 	print "No"
	positiveSetSplit=[]
	negativeSetSplit=[]
	for conn in connSplitList:
		conn1,conn2=conn[0],conn[1]
		posList=searchSplitConn(conn1,conn2,wordList,sentenceList)
		if(len(posList)==0):
			continue
		for i,j in posList:
		 	if(not (wordList[i].splitConn and wordList[j].splitConn)):
				negativeSetSplit.append((convert_span(i,conn1),convert_span(j,conn2)))
			elif(i!=len(wordList)-1 and wordList[i+1].splitConn):
				print "Split",len(positiveSetSplit),len(negativeSetSplit)
				negativeSetSplit.append((convert_span(i,conn1),convert_span(j,conn2)))
			else:
				positiveSetSplit.append((convert_span(i,conn1),convert_span(j,conn2)))

	return (positiveSetSingle,negativeSetSingle,positiveSetSplit,negativeSetSplit)
def genFeatureSingleConn(conn,label,discourseFile):
		sentenceList=discourseFile.sentenceList
		wordList=discourseFile.globalWordList
		chunk=getChunk(conn[0],wordList,sentenceList)
		prevChunk=sentenceList[chunk.sentenceNum].chunkList[chunk.chunkNum-1]
		nxtChunk=sentenceList[chunk.sentenceNum].chunkList[chunk.chunkNum+1]
		print "hh",prevChunk.nodeName,nxtChunk.nodeName
		node=sentenceList[chunk.sentenceNum].nodeDict[chunk.nodeName]
		nodeDict=sentenceList[chunk.sentenceNum].nodeDict
		prevNode=sentenceList[prevChunk.sentenceNum].nodeDict[prevChunk.nodeName]
		nxtNode=sentenceList[nxtChunk.sentenceNum].nodeDict[nxtChunk.nodeName]
		if(getSpan(conn,wordList)==u'\u0924\u094b'):
			print discourseFile.rawFileName,wordList[conn[0]].sentenceNum
			print "get to",label
			print node.nodeRelation
			print node.getChunkName(node.nodeParent)
			for child in node.childList:
				print node.getChunkName(child),nodeDict[child].nodeRelation,
			if(len(node.childList)==0):
				print "None"
			else:
				print ""
		print "single conn","-"*30,node.getChunkName(nxtNode.nodeRelation),label
		for p in conn:
			print discourseFile.globalWordList[p].word,
		print "\n"
		feature=Feature("lists/compConnectiveList.list","lists/tagSet.list","lists/chunkSet.list",discourseFile,discourseFile.globalWordList,discourseFile.sentenceList,conn)
		feature.wordFeature(conn)
		feature.tagFeature(conn)
#		feature.nodeFeature(node.nodeRelation,"nodeRelationSet")
#		feature.nodeFeature(node.getChunkName(node.nodeParent),"nodeParentSet")
#		feature.nodeFeature(prevNode.nodeRelation,"nodeRelationSetPrev")
#		feature.nodeFeature(nxtNode.nodeRelation,"nodeRelationSetNext")
#		feature.nodeFeature(node.getChunkName(prevNode.nodeParent),"nodeParentSetPrev")
#		feature.nodeFeature(node.getChunkName(nxtNode.nodeParent),"nodeParentSetNext")
		feature.tagNeighbor(conn,-1)
		feature.tagNeighbor(conn,1)
#		feature.tagNeighbor(conn,-2)
#		feature.tagNeighbor(conn,2)
#		feature.tagCombo(conn,0,-1)
		feature.chunkFeature(conn)
#		feature.hasNodeRelation("k1",node.nodeName,nodeDict,10)
#		feature.hasNodeRelation("k2",node.nodeName,nodeDict,10)
#		feature.hasNodeRelation("k3",node.nodeName,nodeDict,10)
#		feature.hasNodeRelation("k4",node.nodeName,nodeDict,10)
#		feature.hasNodeRelation("k5",node.nodeName,nodeDict,10)
#		feature.hasNodeRelation("k7t",node.nodeName,nodeDict,10)
#		feature.hasNodeRelation("r6",node.nodeName,nodeDict,10)
	#	feature.hasNodeRelation("r6-k1",node.nodeName,nodeDict,10)
#		feature.hasNodeRelation("k7p",node.nodeName,nodeDict,10)
#		feature.hasNodeRelation("k7",node.nodeName,nodeDict,10)
#		feature.hasNodeRelationSpecific(conn,u'\u0915\u0947 \u092c\u093e\u0926',["k2","k7t"],node.nodeName,nodeDict,10)
#		feature.hasNodeRelationSpecific(conn,u'\u0915\u0947 \u092c\u093e\u0926',["k1"],node.nodeName,nodeDict,10)
#		feature.hasNodeRelationSpecific(conn,u'\u0915\u0947 \u092c\u093e\u0926',["k7t"],node.nodeName,nodeDict,10)
#		feature.hasNodeRelationSpecific(conn,u'\u0915\u0947 \u092c\u093e\u0926',["r6"],node.nodeName,nodeDict,10)
#		feature.chunkCombo(conn,0,-1)
#		feature.chunkCombo(conn,0,1)
#		feature.chunkCombo(conn,-1,1)
#		feature.chunkCombo(conn,0,-2)
		feature.chunkNeighbor(conn,1)
		feature.chunkNeighbor(conn,-1)
#		feature.chunkNeighbor(conn,2)
#		feature.chunkNeighbor(conn,-2)
		feature.setClassLabel(label)
		feature.aurFeature2(conn,node.nodeName,nodeDict,wordList[conn[0]].conn,discourseFile.rawFileName,wordList[conn[0]].sentenceNum)
#		feature.aurFeature(conn)
		feature.parFeature(conn)
		l1=feature.toRootFeature(conn,node,nodeDict)
		l2=feature.tok7tFeature(conn,node,nodeDict)
		feature.featureVector.extend(l1)
		feature.featureVector.extend(l2)

		d={}
		for f in feature.featureList:
			d[f[0]]=f[1]
		
			
		return feature
			
			
		li2=[
		("wordFeature","tagNeighbor_1"),
		("wordFeature","tagNeighbor_-1"),
		("wordFeature","chunkNeighbor_1"),
		("wordFeature","chunkNeighbor_-1"),
		("tagNeighbor_1","tagNeighbor_-1"),
		("tagNeighbor_1","chunkNeighbor_-1"),
		("tagNeighbor_-1","chunkNeighbor_1"),
		("chunkNeighbor_1","chunkNeighbor_-1"),
		]
		for i in li2:
			feature.featureList.append((i[0]+"--"+i[1],str(d[i[0]])+"__"+str(d[i[1]])))

#		li=["wordFeature","chunkFeature","tagFeature","tagNeighbor_1","tagNeighbor_-1","chunkNeighbor_1","chunkNeighbor_-1","tagNeighbor_2","tagNeighbor_-2","chunkNeighbor_2","chunkNeighbor_-2"]
#		li=["wordFeature","chunkFeature","tagFeature","tagNeighbor_1","tagNeighbor_-1","chunkNeighbor_1","chunkNeighbor_-1","chunkNeighbor_2"]
		li=["wordFeature","chunkFeature","tagFeature","tagNeighbor_1","tagNeighbor_-1","chunkNeighbor_1","chunkNeighbor_-1"]
		
		for i in li:
			feature.featureList.append(("Connective--"+i,d["wordFeature"]+"__"+str(d[i])))
		
		sz=len(li)
		for x in range(0,sz):
			for y in range(x+1,sz):
				i=li[x]
				j=li[y]
				feature.featureList.append((i+"--"+j,str(d[i])+"__"+str(d[j])))


#		feature.kebaadFeature(conn,node,nodeDict,label)
#		feature.keliyeFeature(conn,node,nodeDict,label)
#		feature.aageFeature(conn,node,nodeDict,discourseFile.rawFileName,wordList[conn[0]].sentenceNum,label)
#		feature.lekinFeature(conn)
#		feature.tathaFeature(conn,node,nodeDict,wordList[conn[0]].conn,discourseFile.rawFileName,wordList[conn[0]].sentenceNum)
#		feature.halankiFeature(conn)
		

# study of feature distribution 
#		dependencyList=genDependencyList(node,nodeDict,feature)
#		if(node.nodeParent!="None"):
#			parent=nodeDict[node.nodeParent]
#			dependencyList.extend(genDependencyList(parent,nodeDict,feature,"Parent--"))
#		write_dependency(conn,wordList,dependencyList,label)


#		if(getSpan(conn,wordList)==u'\u0915\u0947 \u092c\u093e\u0926'): #ke baad
#			f1=feature.featureVector[:len(feature.wordDictionary)]
#			l=len(feature.featureVector)
#			feature.featureVector=f1
#			extra=[0]*(l-len(f1))
#			f1.extend(extra)
#			feature.featureVector=f1
#			feature.dependencyFeature(conn,dependencyList)
#		else:
#			for i in range(0,feature.dependencyFeatureNum):
#				feature.featureVector.append(0)

#		print feature.featureVector
#		return feature
#		markDependency(feature,dependencyList)
#		write_conn_info(conn,discourseFile,label)
		return feature

#		if(getSpan(conn,wordList)==u'\u0915\u0947 \u092c\u093e\u0926'): #ke baad
#		if(getSpan(conn,wordList)==u'\u0914\u0930'): # aur
#		if(getSpan(conn,wordList)==u'\u0932\u0947\u0915\u093f\u0928'): # lekin
#		if(getSpan(conn,wordList)==u'\u0924\u094b'): 
#			print "Speckebaad"
#			feature.dependencyFeature(conn,dependencyList)
#		else:
#			feature.featureVector.extend([0,0,0,0,0,0,0,0,0])
#		if(getSpan(conn,wordList)==u'\u0915\u0947 \u092c\u093e\u0926'):
#			print "ke baad",label
#			print label,node.getChunkName(node.nodeName)
#			print label,node.nodeRelation,node.getChunkName(node.nodeParent)
#			print label,len(node.childList)
#			for child in node.childList:
#				print node.getChunkName(child),"-",nodeDict[child].nodeRelation,
#			print ""
#		if(getSpan(conn,wordList)==u'\u0914\u0930'):
#			print "aur--",label
#			print discourseFile.rawFileName,wordList[conn[0]].sentenceNum
#			print label,"number of children",len(node.childList)
#			print label,"noderelation and parent",node.nodeRelation,node.getChunkName(node.nodeParent)
#			try:
#				print label,nodeDict[node.nodeParent].nodeRelation,node.getChunkName(nodeDict[node.nodeParent].nodeParent)
#			except:
#				print label,"root"
#			vgnum=0
#			for child in node.childList:
#				if(child[:2]=="VG"):
#					vgnum+=1
#			print label,"vgnum",vgnum
		return feature

def genDependencyList(node,nodeDict,feature,extraLabel=""):
		dependencyList=[]
		for relation in feature.nodeRelationSet:
			dependencyList.append(extraLabel+relation+":"+str(hasChildRelation(node.nodeName,nodeDict,relation)))
		dependencyList.append(extraLabel+"ParentRelation:"+node.nodeRelation)
		dependencyList.append(extraLabel+"Parent:"+node.getChunkName(node.nodeParent))
		dependencyList.append(extraLabel+"childlen:"+str(len(node.childList)))
		dependencyList.append(extraLabel+"VGchildren:"+str(findChild("VG",node.nodeName,nodeDict,0,10)))
		for tag in feature.tagSet:
			dependencyList.append(extraLabel+"Tag-"+tag+":"+str(hasChild(node.nodeName,nodeDict,False)))
		return dependencyList

def markDependency(feature,dependencyList):
	done=False
	for connective in feature.wordDictionary:
		if(getSpan(conn,wordList)==connective):
			feature.dependencyFeature(conn,dependencyList)
			done=True
		else:
			for i in range(0,feature.dependencyFeatureNum):
				feature.featureVector.append(0)
	if(not done):
		print "ERROR",getSpan(conn,wordList)

def write_dependency(conn,wordList,dependencyList,label):
		createDirectory("./featureDist/")
		FD=codecs.open("featureDist/"+getSpan(conn,wordList),"a")
		FD.write("Label:"+label+"\n")
		for line in dependencyList:
			FD.write(line+"\n")
		FD.close()
def write_conn_info(conn,discourseFile,label):
	connective=getSpan(conn,discourseFile.globalWordList)
	createDirectory("./connInfo/")
	FD=codecs.open("./connInfo/"+connective,"a")
	FD.write("label:"+label+"\n")
	FD.write("FileName:"+discourseFile.rawFileName+"\n")
	FD.write("sentenceNum:"+str(discourseFile.globalWordList[conn[0]].sentenceNum)+"\n")
	FD.close()

def genFeatureSplitConn(conn,label,discourseFile):
		print "conn","-"*30,
		for p in conn[0]:
			print discourseFile.globalWordList[p].word,
		print "---",
		for p in conn[1]:
			print discourseFile.globalWordList[p].word,
		print ""
#		c=conn[0]
#		c.extend(conn[1])
#		print c
		feature=Feature("lists/splitConnectiveList.list","lists/tagSet.list","lists/chunkSet.list",discourseFile,discourseFile.globalWordList,discourseFile.sentenceList,conn)
		feature.wordFeature(conn[0],conn[1])
		feature.tagFeature(conn[0])
		feature.tagFeature(conn[1])
#		feature.tagNeighbor(conn[0],-1)
#		feature.tagNeighbor(conn[0],1)
#		feature.tagNeighbor(conn[1],-1)
#		feature.tagNeighbor(conn[1],1)
		feature.chunkFeature(conn[0])
		feature.chunkFeature(conn[1])
#		feature.chunkNeighbor(conn[0],1)
#		feature.chunkNeighbor(conn[0],-1)
#		feature.chunkNeighbor(conn[1],1)
#		feature.chunkNeighbor(conn[1],-1)
#		feature.chunkNeighbor(conn[0],2)
#		feature.chunkNeighbor(conn[1],-1)
#		feature.chunkNeighbor(conn[1],-2)
#		feature.chunkNeighbor(conn[1],1)
		feature.setClassLabel(label)
		c=[]
		for p in conn[0]:
			c.append(p)
		for p in conn[1]:
			c.append(p)
#		write_conn_info(c,discourseFile,label)
		return feature

	
connList=loadConnList("lists/compConnectiveList.list")
connSplitList=loadConnList("lists/splitConnectiveList.list",True)




#discourseFileCollection=loadModel("processedData/annotatedData")
#print len(discourseFileCollection)
positiveSet=[]
negativeSet=[]
positiveSetSplit=[]
negativeSetSplit=[]
fileNum=0
featureCollectionSingle=[]
featureCollectionSplit=[]
featureCollectionDescSingle=[]
featureCollectionDescSplit=[]

from os import listdir
from os.path import isfile, join
discourseFileCollection= [ "./processedData/collection/"+str(f) for f in listdir("./processedData/collection/") if isfile(join("./processedData/collection",f)) ]
discourseFileCollection=folderWalk("./processedData/collection/")

for discourseFileLocation in discourseFileCollection:
	discourseFile=loadModel(discourseFileLocation)
	wordList=discourseFile.globalWordList
	pSet,nSet,pSetSplit,nSetSplit=identifyConnectives(discourseFile,connList,connSplitList)
	for conn in pSet:
		featureCollectionSingle.append(genFeatureSingleConn(conn,"Yes",discourseFile))
		featureDescInst=featureDesc(discourseFile.rawFileName,wordList[conn[0]].sentenceNum,"Single connective identification","Yes",len(featureCollectionDescSingle))
		featureDescInst.addAttr("Single connective",getSpan(conn,wordList))
		featureDescInst.addAttr("Arg1",getSpan(wordList[conn[0]].arg1Span,wordList))
		featureDescInst.addAttr("Arg1num",wordList[wordList[conn[0]].arg1Span[0]].sentenceNum)
		featureDescInst.addAttr("Arg2",getSpan(wordList[conn[0]].arg2Span,wordList))
		featureDescInst.addAttr("Arg2num",wordList[wordList[conn[0]].arg2Span[0]].sentenceNum)
		featureDescInst.addAttr("connSpan",conn)
		featureDescInst.addAttr("remove",False)
		try:
			featureDescInst.addAttr("Single connective neighborhood",wordList[conn[0]-1].word)
		except:
			featureDescInst.addAttr("Single connective neighborhood","First")
		featureCollectionDescSingle.append(featureDescInst)
	for conn in nSet:
		featureCollectionSingle.append(genFeatureSingleConn(conn,"No",discourseFile))
		featureDescInst=featureDesc(discourseFile.rawFileName,wordList[conn[0]].sentenceNum,"Single connective identification","No",len(featureCollectionDescSingle))
		featureDescInst.addAttr("Single connective",getSpan(conn,wordList))
		featureDescInst.addAttr("Arg1","None")
		featureDescInst.addAttr("Arg1num","None")
		featureDescInst.addAttr("Arg2","None")
		featureDescInst.addAttr("Arg2num","None")
		featureDescInst.addAttr("connSpan",conn)
		featureDescInst.addAttr("remove",False)
		try:
			featureDescInst.addAttr("Single connective neighborhood",wordList[conn[0]-1].word)
		except:
			featureDescInst.addAttr("Single connective neighborhood","First")
		featureCollectionDescSingle.append(featureDescInst)
	for conn in pSetSplit:
		featureCollectionSplit.append(genFeatureSplitConn(conn,"Yes",discourseFile))
		featureDescInst=featureDesc(discourseFile.rawFileName,wordList[conn[0][0]].sentenceNum,"Split connective identification","Yes",len(featureCollectionDescSplit))
		featureDescInst.addAttr("connective",getSpan(conn[0],wordList)+"-"+getSpan(conn[1],wordList))
		featureDescInst.addAttr("connSpan",conn)
		featureDescInst.addAttr("remove",False)
		featureCollectionDescSplit.append(featureDescInst)
	for conn in nSetSplit:
		featureCollectionSplit.append(genFeatureSplitConn(conn,"No",discourseFile))
		featureDescInst=featureDesc(discourseFile.rawFileName,wordList[conn[0][0]].sentenceNum,"Split connective identification","No",len(featureCollectionDescSplit))
		featureDescInst.addAttr("connective",getSpan(conn[0],wordList)+"-"+getSpan(conn[1],wordList))
		featureDescInst.addAttr("connSpan",conn)
		featureDescInst.addAttr("remove",False)
		featureCollectionDescSplit.append(featureDescInst)
	positiveSet.extend(pSet)
	negativeSet.extend(nSet)
	positiveSetSplit.extend(pSetSplit)
	negativeSetSplit.extend(nSetSplit)
	fileNum+=1
print len(positiveSetSplit),len(negativeSetSplit)
print len(positiveSet),len(negativeSet)
print len(featureCollectionSingle)


#extraFeatureList=removeExtraFeatures(featureCollectionSingle)
#for featureNum in range(0,len(featureCollectionSingle)):
#	featureCollectionSingle[featureNum].cleanFeature(extraFeatureList)

print "featureSize",len(featureCollectionSingle[0].featureVector)






#FD=codecs.open("to","w")
#for featureDesc in featureCollectionDescSingle:
#	print featureDesc.attrList
#	if(getattr(featureDesc,"Single connective")==u'\u0924\u094b'):
#		featureDesc.printFeatureDesc(FD)
#FD.close()

#exit()

classList=[]
for feature in featureCollectionSingle:
	classList.append(feature.classLabel)
classList=list(set(classList))
print classList
max_acc=-1
min_acc=100
max_precision=-1
min_precision=100
avg_accuracy=0.0
time=20

if(len(sys.argv)<2):
	print "enter number of iterations"
	exit()
time =int(sys.argv[1])



x,y,z,err,corr,extra=runModel(featureCollectionSplit,featureCollectionDescSplit,classList,"connective_split_identification",6,1,1)






remove=[]
for c in corr:
	connSpan=getattr(c,"connSpan")
	sentenceNum=getattr(c,"sentenceNum")
	rawFileName=getattr(c,"rawFileName")
	ss=getattr(c,"connSpan")
	splitSpan=ss[0]
	splitSpan.extend(ss[1])
	print "comparing",getattr(c,"connective"),splitSpan,rawFileName,sentenceNum
	num=0
	for f in featureCollectionDescSingle:
#		if(getattr(f,"Single connective")==u'\u0932\u0947\u0915\u093f\u0928'):
#			print "\tlekin",getattr(f,"rawFileName"),getattr(f,"sentenceNum"),getattr(f,"rawFileName")==rawFileName,getattr(f,"sentenceNum")==sentenceNum
		if(getattr(f,"rawFileName")!=rawFileName or getattr(f,"sentenceNum")!=sentenceNum):
			num+=1
			continue
		cspan=getattr(f,"connSpan")
		print "\t",getattr(f,"Single connective"),cspan,f.classLabel
		rem=True
		for pos in cspan:
			if(pos not  in splitSpan):
				rem=False
				break
		if(rem):
			remove.append(num)
			setattr(f,"remove",True)
			if(f.classLabel=="Yes"):
				print "removing this"
				f.classLabel="No"
			else:
				print "moving from no to yes ??"
		num+=1
print remove
remove=list(set(remove))
remove.sort(reverse=True)
print remove
print "removal size",len(remove)
FD=codecs.open("removed instances due to split conn",'w')
for i in remove:
	f=featureCollectionSingle.pop(i)
	f=featureCollectionDescSingle.pop(i)
	f.printFeatureDesc(FD)
	if(not getattr(f,"remove")):
		print "useless fellow :/"
		print getattr(f,"Single connective")
FD.close()




fcollec=[]

for fs in featureCollectionSingle:
	print "f1",fs.featureList
	fcollec.append((fs.featureList,fs.classLabel))
exportModel("./fList",fcollec)


if(time==0):
	exit()


errorCollection=[]
err=[]
for i in range(0,time):
	print "running"
	#x,y,z,err=runModel(featureCollectionSplit,featureCollectionDescSplit,classList,"connective_split_identification",6,1,1)
	x,y,z,err,corr,extra=runModel(featureCollectionSingle,featureCollectionDescSingle,classList,"connective_identification",15,1,1)
	errorCollection.extend(err)
	avg_accuracy+=z["Yes"]
	max_acc=max(max_acc,z["Yes"])
	min_acc=min(min_acc,z["Yes"])
	print "Information--",extra[0],extra[1],extra[2]
print "Accuracy",round(min_acc*100,2),"-",round(max_acc*100,2),"-",round(avg_accuracy*100.0/time,2)
FD=open("accuracy_results","a")
FD.write(featureCollectionSingle[0].description+"\n")
FD.write("Accuracy "+str(round(min_acc*100,2))+"-"+str(round(max_acc*100,2))+"-"+str(round(avg_accuracy*100.0/time,2))+"\n")
FD.close()
basicAnalysis(err,"connective_identification")
#basicAnalysis(errorCollection,"conn_all_runs")
