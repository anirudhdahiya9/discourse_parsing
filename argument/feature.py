#!/usr/bin/python
# -*- coding: utf-8 -*-
import sys
import codecs
import numpy
import itertools
reload(sys)
sys.setdefaultencoding("utf-8")
from util import *
from letter import *
from tree_api import *


class Feature():
	def __init__(self,word_dictionary_path,tag_path,chunk_path,global_word_list,sentence_list,conn=None):
		self.featureVector=[]
		self.featureList=[]
		self.classLabel=None
		self.globalWordList=global_word_list
		self.sentenceList=sentence_list
		self.description=""
		self.connSpec={}
		self.sampleDescription={}
		if(conn!=None and isinstance(conn[0],int)):
			self.connective=""
			for i in conn:
				self.connective=self.connective+" "+self.globalWordList[i].word
			self.connective=self.connective[1:]
			self.conn=conn
		elif(conn!=None and isinstance(conn[0],list)):
			self.connective=""
			for i in conn:
				for j in i:
					self.connective=self.connective+" "+self.globalWordList[j].word
			self.connective=self.connective[1:]
			self.conn=conn
		FD=codecs.open("./lists/connSpecDependency.list","r")
		currConn=""
		for line in FD.readlines():
			line=line[:-1]
			if(line[:4]=="conn"):
				self.connSpec[line.split(":")[1]]=[]
				currConn=line.split(":")[1]
			else:
				self.connSpec[currConn].append(line)
		self.dependencyFeatureNum=len(self.connSpec[self.connSpec.keys()[0]])
		FD.close()
	def wordFeature(self,wordList,wordList2=[]):
		self.description=self.description+" wordFeature"
		w=""
		for word in wordList:
			word=self.globalWordList[word].word
			w=w+word+" "
		if(len(wordList2)!=0):
			w=w[:-1]+".."
		for word in wordList2:
			word=self.globalWordList[word].word
			w=w+word+" "
		self.featureList.append(("wordFeature",w[:-1]))
	def tagFeature(self,wordList,num=None):
		self.description=self.description+" tagFeature"
		completeTag=""
		for word in wordList:
			word=self.globalWordList[word]
			completeTag=completeTag+" "+word.wordTag
		completeTag=completeTag[1:]
		if(num==None):
			self.featureList.append(("tagFeature",completeTag.replace(" ","-")))
		else:
			self.featureList.append(("tagFeature"+str(num),completeTag.replace(" ","-")))
	def tagNeighbor(self,wordList,offSet):
		self.description=self.description+" tagNeighbor-"+str(offSet)
		tagN=""
		if(offSet<0):
			if(wordList[0]+offSet<0 or self.globalWordList[wordList[0]+offSet].sentenceNum!=self.globalWordList[wordList[0]].sentenceNum):
	#		if(wordList[0]+offSet<0):
				tagN="First"
			else:
				tagN=self.globalWordList[wordList[0]+offSet].wordTag
		else:
			if(wordList[-1]+offSet>=len(self.globalWordList) or self.globalWordList[wordList[-1]+offSet].sentenceNum!=self.globalWordList[wordList[-1] +offSet].sentenceNum):
# This should be the correct line of code but above line giving better results :/ :/
#		if(wordList[-1]+offSet>=len(self.globalWordList) or self.globalWordList[wordList[-1]+offSet].sentenceNum!=self.globalWordList[wordList[-1]].sentenceNum):
				tagN="Last"
			else:
			 	tagN=self.globalWordList[wordList[-1]+offSet].wordTag
		self.featureList.append(("tagNeighbor_"+str(offSet),tagList[0]))

	def chunkFeature(self,wordList,num=None):
		self.description=self.description+" chunkFeature"
		chunkList=[]
		for word in wordList:
			word=self.globalWordList[word]
			chunkList.append(self.getChunkInfo(word,0).chunkTag)
		chunkList=list(set(chunkList))
		if(num==None):
			self.featureList.append(("chunkFeature",chunkList[0]))
		else:
			self.featureList.append(("chunkFeature"+str(num),chunkList[0]))
	def chunkNeighbor(self,wordList,offSet):
		self.description=self.description+" chunkNeighbor-"+str(offSet)
		chunkN=""
		if(offSet<0):
			try:
				chunkN=self.getChunkInfo(self.globalWordList[wordList[0]],offSet).chunkTag
			except AttributeError:
				chunkN="First"
		else:
			try:
				chunkN=self.getChunkInfo(self.globalWordList[wordList[-1]],offSet).chunkTag
			except AttributeError:
				chunkN="Last"
		self.featureList.append(("chunkNeighbor_"+str(offSet),chunkN))
	def getCommonParent(self,node,nodePrev,nodeNext,nodeDict):

		if(nodePrev==None):
			commonParent1="NoCommonParentFirst"
		else:
			commonParent1=getCommonParent(nodePrev,node,nodeDict)
		if(nodeNext==None):
			commonParent2="NoCommonParentLast"
		else:
			commonParent2=getCommonParent(nodeNext,node,nodeDict)
		self.featureList.append(("commonParentPrev",node.getChunkName(commonParent1)))
		self.featureList.append(("commonParentNext",node.getChunkName(commonParent2)))
		return (commonParent1,commonParent2)
	def dependencyPathToRoot(self,node,nodeDict):
		path=getPathToRoot(node,nodeDict)
		fullPath="".join(nodeDict[i].nodeRelation+"//" for i in path)
		shortPath=""
		vgf=0
		for i in range(0,8):
			try:
				if(path[i][:2]=="VG"):
					vgf+=1
				if( i!= len(path)-1 and path[i][:2]==path[i+1][:2]):
					print "skipping"
					continue
				shortPath=shortPath+nodeDict[path[i]].nodeRelation+"\\"
			except:
				break
			if(vgf==2):
				print "deplen broke out"
				break
		self.featureList.append(("dependencyPathToRoot",shortPath))
		
		return (shortPath,fullPath)
	def rightWordLocation(self,conn,node,nodeNext,nodeDict,a="",b=""):
#conn is already last word
	  	if(conn[-1]+1==len(self.globalWordList)-1):
			self.featureList.append(("rightWordLocation","Last"))
			return
	  	word=self.globalWordList[conn[-1]]
	  	wordNext=self.globalWordList[conn[-1]+1]
#same node
		if(word.chunkNum==wordNext.chunkNum):
			self.featureList.append(("rightWordLocation","sameNode"))
			return
	  	if(nodeNext==None):
			print "ERROR"
#same parent i.e commonparent should be connective parent
		if(node.nodeParent==nodeNext.nodeParent):
			self.featureList.append(("rightWordLocation","directParent"))
			return
		commonParent=getCommonParent(node,nodeNext,nodeDict)
# word is in connective tree
		if(commonParent==node.nodeName):
			self.featureList.append(("rightWordLocation","nextPartofConnTree"))
			return
# connective is in word tree
		if(commonParent==nodeNext.nodeName):
			self.featureList.append(("rightWordLocation","connPartofnextTree"))
			return
		if(commonParent==node.nodeParent):
			self.featureList.append(("rightWordLocation","indirectConnParent"))
			return
#		if(commonParent==nodeNext.nodeParent):
#			self.featureList.append(("rightWordLocation","indirectNextParent"))
#			return

# common parent is root but only single VGF tree
#common parent is root but conn has another VG* as tree
		self.featureList.append(("rightWordLocation","NoIdea"))
		print "no idea",a,b
		return
	def leftWordLocation(self,conn,node,nodePrev,nodeDict,a,b):
		checkList=[
		u'\u0914\u0930',#aur
#		u'\u092c\u0932\u094d\u0915\u093f'#balki,
#		u'\u0924\u0925\u093e',#tatha
	#	u'\u0924\u094b',#to
#		u'\u092f\u093e',#ya
	#	u'\u0915\u0947 \u0915\u093e\u0930\u0923',#ke karan
#		u'\u0915\u0940 \u0935\u091c\u0939 \u0938\u0947',#ki vajah se
#		u'\u0915\u0947 \u0932\u093f\u090f',# ke liye
		u'\u0915\u0947 \u092c\u093e\u0926' # ke baad
		]
#		if(getSpan(conn,self.globalWordList) not in checkList):
#			self.featureList.append(("leftWordLocation","None1"))
#			return
#conn is already last word
	  	if(conn[0]==0 or self.globalWordList[conn[0]].sentenceNum!=self.globalWordList[conn[0]-1].sentenceNum):
			self.featureList.append(("leftWordLocation","first1"))
			return
	  	word=self.globalWordList[conn[0]]
	  	wordPrev=self.globalWordList[conn[0]-1]
#same node
		if(word.chunkNum==wordPrev.chunkNum):
			self.featureList.append(("leftWordLocation","sameNode1"))
			return
#		self.featureList.append(("leftWordLocation","Other"))
#		return
	  	if(nodePrev==None):
			print "ERROR"
#same parent i.e commonparent should be connective parent
		if(node.nodeParent==nodePrev.nodeParent):
			self.featureList.append(("leftWordLocation","directParent1"))
			return
		commonParent=getCommonParent(node,nodePrev,nodeDict)
# word is in connective tree
		if(commonParent==node.nodeName):
			self.featureList.append(("leftWordLocation","prevPartofConnTree1"))
			return
# connective is in word tree
		if(commonParent==nodePrev.nodeName):
			self.featureList.append(("leftWordLocation","connPartofPrevTree1"))
			return
		if(commonParent==node.nodeParent):
			self.featureList.append(("leftWordLocation","indirectConnParent1"))
			return
		if(commonParent==nodePrev.nodeParent):
			self.featureList.append(("leftWordLocation","indirectPrevParent1"))
			return

# common parent is root but only single VGF tree
#common parent is root but conn has another VG* as tree
		self.featureList.append(("leftWordLocation","NoIdea"))
		print "no idea",a,b
		return

# arg1 postion specific features ---------------------------------------------------

	def connectivePosInSentence(self,wordList):
		self.description=self.description+" connectivePosinSentence"
		connSentenceNum=self.globalWordList[wordList[0]].sentenceNum
		prevSentenceNum1=self.globalWordList[wordList[0]-1].sentenceNum
#		prevSentenceNum2=self.globalWordList[wordList[0]-2].sentenceNum
		if(connSentenceNum!=prevSentenceNum1): #or connSentenceNum!=prevSentenceNum2):
			self.featureList.append(("connectivePosInSentence","Start"))
			return "start"
		else:
			self.featureList.append(("connectivePosInSentence","Middle"))
			return "middle"
	
	def numberOfChunksBeforeConn(self,wordList):
#		if(getSpan(wordList,self.globalWordList)!=u'\u0906\u0917\u0947'):
#			self.featureList.append(("numberOfChunksBeforeConnAage","0"))
#			return "notaage" 
		chunkNum=0
		pos=wordList[0]-1
		prevChunkNum=self.globalWordList[wordList[0]].chunkNum
		while(pos>0 and self.globalWordList[pos].sentenceNum==self.globalWordList[wordList[0]].sentenceNum):
			if(self.globalWordList[pos].chunkNum!=prevChunkNum):
				chunkNum+=1
			prevChunkNum=self.globalWordList[pos].chunkNum
			pos-=1
		if(chunkNum==1):
			self.featureList.append(("numberOfChunksBeforeConn","1"))
		else:
			self.featureList.append(("numberOfChunksBeforeConn","0"))

		return chunkNum
# arg1 postion specific features ended ---------------------------------------------------

# argument specific features  -------------------------------------------------------------


	def connLeafNode(self,connNode,nodeDict):
		if(isLeafNode(connNode,nodeDict)):
			self.featureList.append(("connLeafNode","False"))
		else:
			self.featureList.append(("connLeafNode","True"))

	def connSubTreeHasVGF(self,connNode,nodeDict):
		
		if(findChild("VGF",connNode,nodeDict,0,10)):
			self.featureList.append(("connSubTreeHasVGF","True"))
		else:
			self.featureList.append(("connSubTreeHasVGF","False"))

	def connHasParentVGF(self,connNode,nodeDict):
		node=nodeDict[connNode]
		nodeParent=node.nodeParent
		if("VGF" in nodeParent):
			self.featureList.append(("connHasParentVGF","True"))
		else:
			self.featureList.append(("connHasParentVGF","False"))

# argument specific features ended -------------------------------------------------------------

# arg2 paritality features ---------------------------------------------------------------------
	def connRelativePosition(self,connNode ,node):
		connChunkNum=connNode.chunkNum
		nodeChunkNum=node.chunkNum
		if(nodeChunkNum< connChunkNum):
			self.featureList.append(("connRelativePostion","Before"))
		elif(nodeChunkNum > connChunkNum):
			self.featureList.append(("connRelativePostion","After"))
		else:
			self.featureList.append(("connRelativePostion","Same"))
	def isConn(self,node,sentenceNum):
		nodeChunkNum=node.chunkNum
		sentence=self.sentenceList[sentenceNum]
		wordNumList=sentence.chunkList[nodeChunkNum].wordNumList
		found=False
		for pos in wordNumList:
			if self.globalWordList[pos].conn:
				found=True
		if(found):
			self.featureList.append(("isConn","True"))
		else:
			self.featureList.append(("isConn","False"))
	def clauseEnd(self,node,sentenceNum):
		nodeChunkNum=node.chunkNum
		sentence=self.sentenceList[sentenceNum]
		wordNumList=sentence.chunkList[nodeChunkNum].wordNumList
		
		comma=False

		for pos in wordNumList:
			if(self.globalWordList[pos].word==","):
				comma=True
		if(comma):
			self.featureList.append(("clauseEnd","True"))
		else:
			self.featureList.append(("clauseEnd","False"))
	def firstArg2(self,connNode,node,first):
		connChunkNum=connNode.chunkNum
		nodeChunkNum=node.chunkNum
		if(connChunkNum<=nodeChunkNum and first):
			self.featureList.append(("firstArg2","True"))
		else:
			self.featureList.append(("firstArg2","False"))

# arg2 paritality features ended ---------------------------------------------------------------	
	
# arg2 extender features begin ----------------------------------------------------------------

	def hasParent(self,connNode,nodeDict):
		try:
			parent=nodeDict[connNode.nodeParent]
		except:
			parent=None
		if(parent==None):
			self.featureList.append(("hasConnParent","No"))
		else:
			self.featureList.append(("hasConnParent","Yes"))
	def hasParentParent(self,connNode,nodeDict):
		try:
			parent=nodeDict[connNode.nodeParent]
		except:
			parent=None
		if(parent==None):
			self.featureList.append(("hasConnParentParent","No"))
			return
		try:
			parentParent=nodeDict[parent.nodeName]
		except:
			parentParent=None
		if(parentParent==None):
			self.featureList.append(("hasConnParentParent","No"))
		else:
			self.featureList.append(("hasConnParentParent","Yes"))
			
	def connRelativePosParentParent(self,connNode,nodeDict):

		try:
			parentParent=nodeDict[nodeDict[connNode.nodeParent].nodeParent]
		except:
			parentParent=None
		if(parentParent==None):
			self.featureList.append(("connRelativePosParentParent","DoesNotExist"))
			return
		
		connChunkNum=connNode.chunkNum
		parentChunkNum=parentParent.chunkNum

		if(parentChunkNum>connChunkNum):
			self.featureList.append(("connRelativePosParentParent","After"))
		else:
			self.featureList.append(("connRelativePosParentParent","Before"))
	def chunkComboName(self,connNode,nodeDict):
		try:
			parentNode=nodeDict[connNode.nodeParent]
			extendNode=nodeDict[parentNode.nodeParent]
		except:
			parentNode=None
			extendNode=None
		if(parentNode==None or extendNode==None):
			self.featureList.append(("chunkComboName","None"))
		else:
			self.featureList.append(("chunkComboName",connNode.getChunkName(parentNode.nodeName),connNode.getChunkName(extendNode.nodeName)))
# arg2 extender features ended ----------------------------------------------------------------

# arg1 same sentence position features beginning ---------------------------------------------------------

	def arg2Position(self,connNode,arg2Presence):
		if(arg2Presence[0] and not arg2Presence[1]): #and not p[1] and not p[2]'''):
			self.featureList.append(("arg2Position","ConnSubTree"))
		elif(not arg2Presence[0] and arg2Presence[1]):
			self.featureList.append(("arg2Position","ParentSubTree"))
		elif(arg2Presence[0] and arg2Presence[1]):
			self.featureList.append(("arg2Position","ConnSubTree"))
		elif(not arg2Presence[0] and not arg2Presence[1] and arg2Presence[2]):
			self.featureList.append(("arg2Position","OtherSubTree"))
		else:
			self.featureList.append(("arg2Position","Other"))

	def connParent(self,connNode,nodeDict):
		connNode=nodeDict[connNode]
		try:
			parent=nodeDict[connNode.nodeParent]
			self.featureList.append(("connParent",connNode.getChunkName(parent.nodeName)))
		except:
			self.featureList.append(("connParent","None"))
	def connParentParent(self,connNode,nodeDict):
		connNode=nodeDict[connNode]
		try:
			parent=nodeDict[connNode.nodeParent]
		except:
			self.featureList.append(("connParentParent","None"))
			return
		try:
			pParent=nodeDict[parent.nodeParent]
			self.featureList.append(("connParentParent",connNode.getChunkName(pParent.nodeName)))
		except:
			self.featureList.append(("connParentParent","None"))
			
	def connTwoClause(self,connNode,nodeDict):
		

		connNode=nodeDict[connNode]
		childVGF=0
		for child in connNode.childList:
			if(findChild("VG",child,nodeDict,0,15)):
				childVGF+=1
		if(childVGF>=2):
			self.featureList.append(("connTwoClause","Yes"))
		else:
			self.featureList.append(("connTwoClause","No"))

# arg1 same sentence position features ended -------------------------------------------------------------

	def hasNodeRelationSpecific(self,conn,connective,nodeRelationList,node,nodeDict,maxLevel):
		self.description=self.description+" hasNodeRelationSpecific-" +getSpan(conn,self.globalWordList)+"-"+str(nodeRelationList)
		if(getSpan(conn,self.globalWordList)!=connective):
			self.featureVector.append(0)
			return [0]
#		print "got ke baad"
		for nodeRelation in nodeRelationList:
			if(not findRelation(nodeRelation,node,nodeDict,0,maxLevel)):
				self.featureVector.append(0)
				return [0]
		self.featureVector.append(1)
		return [1]

	def nodeFeature(self,node_feature,nodeListName):
		self.description=self.description+" nodeFeature-" +str(nodeListName)
	  	print nodeListName,"Feature"
	  	nodeSet=getattr(self,nodeListName)
	  	if(node_feature not in nodeSet):
			print "ERROR !!!!",nodeListName
		self.featureList.append("nodeFeature-"+str(nodeListName),node_feature)
	def hasNodeRelation(self,nodeRelation,node,nodeDict,maxLevel):
		self.description=self.description+" hasNodeRelation-"+str(nodeRelation)
		if(findRelation(nodeRelation,node,nodeDict,0,maxLevel)):
			self.featureVector.append(1)
			self.featureList.append(("hasnodeRelation"+nodeRelation,1))
			print "nodeRelation found"
		else:
			self.featureVector.append(0)
			self.featureList.append(("hasnodeRelation"+nodeRelation,1))
			print "nodeRelation not found"

	def dependencyFeature(self,conn,dependencyList):
		self.description=self.description+" dependency"
		connective=getSpan(conn,self.globalWordList)
		for feature in self.connSpec[connective.encode("utf-8")]:
			if(feature in dependencyList):
				self.featureVector.append(1)
			else:
				self.featureVector.append(0)
	def getChunkInfo(self,word,offSet):
		sentence=self.sentenceList[word.sentenceNum]
		if(word.chunkNum+offSet>=0 and word.chunkNum+offSet<len(sentence.chunkList)):
			chunk=sentence.chunkList[word.chunkNum+offSet]
		else:
			chunk=None
		return chunk
	def getPrevSentenceSpan(self,conn,):
		sentencePrev=[]
		sentenceNum=self.globalWordList[conn[0]].sentenceNum
		pos=conn[0]-1
		while(pos >=0 and self.globalWordList[pos].sentenceNum==sentenceNum):
			sentencePrev.append(pos)
			pos-=1
		sentencePrev.reverse()
		sentencePrevSpan=getSpan(sentencePrev,self.globalWordList)
		return sentencePrevSpan
	def cleanFeature(self,removeList):
		removeList=sorted(removeList,reverse=True)
		for pos in removeList:
			val=self.featureVector.pop(pos)
			if(val==1):
				print "clean ERROR"

	def setClassLabel(self,label):
		self.classLabel=label

class featureDesc():
	def __init__(self,raw_filename,sentence_num,description,class_label,identity):
		self.rawFileName=raw_filename
		self.sentenceNum=sentence_num
		self.description=description
		self.classLabel=class_label
		self.classifiedAs=""
		self.attrList=["rawFileName","sentenceNum","description","classLabel","classifiedAs"]
		self.ID=identity
	def addDescription(self,desc):
		self.description=self.description+"\n"+desc
	def addAttr(self,attr_name,attr_value):
		if(attr_name in self.attrList):
			return
		setattr(self,attr_name,attr_value)
		if(not isinstance(attr_value,list)):
			self.attrList.append(attr_name)
	def printFeatureDesc(self,FD,ignore_print=[]):
#		ignore_print.append("sentenceNum")
#		ignore_print.append("rawFileName")
		ignore_print.append("description")
#		ignore_print.append("Probability")
		for attr in self.attrList:
			if(attr in ignore_print):
				continue
			FD.write(attr+" : "+str(getattr(self,attr))+"\n")
		return

def convertDataSet(featureCollection):
	print "-"*50,"ConvertDataSet"
	data=[]
	labels=[]
	for feature in featureCollection:
		numpyArr=numpy.array(feature.featureVector)
		data.append(numpyArr)
		labels.append(feature.classLabel)
	labels=numpy.array(labels)
	data=numpy.array(data)
	return data,labels
def removeExtraFeatures(featureCollection):
	featureSize=len(featureCollection[0].featureVector)
	featurePresent=[]
	print "featureSize---",featureSize
	for i in featureCollection[0].featureVector:
		featurePresent.append(False)
	for feature in featureCollection:
		vector=feature.featureVector
		for pos in range(0,featureSize):
			if(vector[pos]==1):
				featurePresent[pos]=True
	remove=[]
	for pos in range(0,featureSize):
		if(not featurePresent[pos]):
			remove.append(pos)
	print "useless features",remove
	return remove
