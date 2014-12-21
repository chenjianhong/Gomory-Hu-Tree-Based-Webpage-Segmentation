# -*- coding: UTF-8 -*-

from VertexObject import *
import urllib2
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import simplejson
import json
from PIL import Image, ImageDraw
from itertools import groupby
from operator import itemgetter
from sets import Set
from igraph import *
import Levenshtein
from HTMLParser import HTMLParser
from lxml import etree
import lxml.html
import lxml.etree
import lxml.builder
from lxml.etree import tostring
from lxml.builder import E
import requests
import re
import codecs
from django.utils.encoding import smart_str, smart_unicode
from django.utils.html import escape
import difflib
import time
import datetime



contentList=['div','table', 'ul','ol']
toBeIgnoredList=['script','noscript','style','area','head','meta','frame','frameset','br','hr']
segment_tags = { "head", "table", "center", "body", "section", "ul", "li"}
initialNodes=Set()
initialnodes=Set()
myNodes=[]
mynodes=[]
toBeRemoved=Set()
verID=int(0)
t=str(datetime.datetime.now()).split('.')[0]

JS_SCRIPT_GET_TEXT_NODES  =  "function trim(str){return str.replace(/^\s+|\s+$/g,'');}"+"function extractText(element) {var text = '';for ( var i = 0; i < element.childNodes.length; i++) {if (element.childNodes[i].nodeType === Node.TEXT_NODE && element.childNodes[i].textContent!='') {nodeText = trim(element.childNodes[i].textContent);if (nodeText) {text += element.childNodes[i].textContent + ' ';}}}return trim(text);}"+"function selectElementsHavingTextByXPath(expression) {result = document.evaluate(\".\" + expression, document.body, null,XPathResult.ANY_TYPE, null);var nodesWithText = new Array();var node = result.iterateNext();while (node) { if (extractText(node)) {  nodesWithText.push(node) } node = result.iterateNext();} return nodesWithText;  } return selectElementsHavingTextByXPath(arguments[0]);"
GET_PARENTS = "var vertex = [];function startSegmentation(win,elem){contentWindow = win;contentDocument = contentWindow.document;var root = contentDocument.getElementsByTagName('BODY')[0];createVertexObject(root,undefined,elem);return JSON.stringify(vertex);}function createVertexObject(georoot,parent,elem){var tagPath=georoot.tagName+'-';for(var i=0;i<georoot.childNodes.length;i++){var child=georoot.childNodes[i];createVertexObjectNode(child,georoot,tagPath,elem);}}function createVertexObjectNode(root,parent,tagPath,elem){ if(root == elem) {var h =root.offsetHeight;var w =root.offsetWidth;var x =root.offsetLeft;var y =root.offsetTop;var typeOfNode=root.nodeName;var outerhtml=root.outerHTML;var childTagPath=tagPath+root.tagName;var vertexObj = {'tagPath': childTagPath,'h': h ,'w': w ,'x': x ,'y': y , 'contentType':typeOfNode, 'outerHTML': outerhtml };vertex.push(vertexObj);}for (var i=0; i<root.childNodes.length; i++){var childTagPath=tagPath+root.tagName+'-';createVertexObjectNode(root.childNodes[i],root,childTagPath,elem);}}return startSegmentation(window,arguments[0]);"
VIEWPORT_SCRIPT = "var body = document.body;html = document.documentElement;var y = Math.max( body.scrollHeight, body.offsetHeight, html.clientHeight, html.scrollHeight, html.offsetHeight );var x = Math.max( body.scrollWidth, body.offsetWidth, html.clientWidth, html.scrollWidth, html.offsetWidth );return {'x':x,'y':y}"
try : 
  #initiating webdriver
    print "Initialting WebDriver . . . . "
    driver = webdriver.Firefox()
    webURL=str(sys.argv[1])
    print "Fetching Webpage . . . . "
    driver.get(webURL)
    driver.maximize_window()
    driver.implicitly_wait(450)
   
    
   #gettting the dimensions of webpage
    pageDim=driver.execute_script(VIEWPORT_SCRIPT)
    current_directory=os.getcwd()
    
    
#--------------------------------ROUND 1 : getting initial nodes-------------------------------
    print "ROUND 1 : getting initial nodes . . . . "
   #Creating new image with webpage dimensions
    im = Image.new('RGB', (pageDim['x']+100,pageDim['y']+100), (255,255,255))
    dr = ImageDraw.Draw(im)
    node_text=[]
    #Getting all text nodes and filter those vertices having no width & height
    print "Getting all text nodes , filter duplicate parent nodes and filter those vertices having no width & height . . . . "
    text_nodes=driver.execute_script(JS_SCRIPT_GET_TEXT_NODES, "//*")
    
    for i in text_nodes:
      if i.is_displayed and i.tag_name not in toBeIgnoredList and  not(i.size['width']<1 or i.size['height']<1) and (i.size['width']*i.size['height']>=50):
	p = i.find_element_by_xpath('..')
	text = p.text.strip() 
	#--------------add the immediate Layout nodes of elementary text nodes to get bigger blocks as vertices-----------------#
	if p.is_displayed and len(text) > 0 and text not in node_text and i.tag_name not in contentList and p not in initialNodes and (p.size['width']*p.size['height']>=50) and p.tag_name  in contentList:
	  initialNodes.add(p)
	  node_text.append(text)
	  dr.rectangle(((p.location["x"],p.location["y"]),(p.location["x"]+i.size["width"],p.location["y"]+p.size["height"])), outline = "blue")
	else :
	  initialNodes.add(i)
	  node_text.append(i.text.strip())
	  dr.rectangle(((i.location["x"],i.location["y"]),(i.location["x"]+i.size["width"],i.location["y"]+i.size["height"])), outline = "blue")
    print "Getting all Images . . . . "
    list_links = driver.find_elements_by_tag_name('img')
    
    for i in list_links:
      if i.is_displayed and i not in initialNodes and  not(i.size['width']<1 or i.size['height']<1) and (i.size['width']*i.size['height']>=50):
	  initialNodes.add(i)
	  dr.rectangle(((i.location["x"],i.location["y"]),(i.location["x"]+i.size["width"],i.location["y"]+i.size["height"])), outline = "blue")
    print "Getting all Inputs . . . . "
    
    list_links = driver.find_elements_by_tag_name('input')
    for i in list_links:
       if i.is_displayed and i not in initialNodes and  not(i.size['width']<1 or i.size['height']<1)and (i.size['width']*i.size['height']>=50):
	  initialNodes.add(i)
	  dr.rectangle(((i.location["x"],i.location["y"]),(i.location["x"]+i.size["width"],i.location["y"]+i.size["height"])), outline = "blue")
   
    
    #Save the plotted image initially  
    im.save(current_directory+"/Output/GOMORY/"+str(webURL.split('//')[1]).replace('/','_')+"_Round : 1_VertexSelected_"+t+".png", "PNG")
    print "Round 1 done . . . . " 
    
    #Store the filtered node information varID,tagPath,outerHTML,height,width,x,y,webElement,left,top,right,bottom
    #draw merged nodes
    print "Store the selected node information as VertexObject . . . . "
    k=0
    for i in initialNodes :
      tagPath=' '
      outerHTML=' ' 
      left={}
      top={}
      right={}
      bottom={}
      h=i.size["height"]
      elem=i
      w=i.size["width"]
      x=i.location["x"]
      y=i.location["y"]
      node = VertexObject(k,tagPath,outerHTML,h,w,x,y,elem,left,top,right,bottom)
      k=k+1
      mynodes.append(node)
    
    #--------------------------------ROUND 2 : filtering and merging nodes-------------------------------
    #Creating new image with webpage dimensions
    print "ROUND 2 : filtering and merging nodes . . . . "
    im = Image.new('RGB', (pageDim['x']+100,pageDim['y']+100), (255,255,255))
    dr = ImageDraw.Draw(im)
    #Filter smaller boxes
    initialnodes=Set(mynodes)
    for x1 in initialnodes : 
      for x2 in initialnodes :
	if x2!=x1 :
	  if (x1.x<x2.x) and (x1.x+x1.width>x2.x+x2.width) and (x1.y<x2.y) and (x1.y+x1.height>x2.y+x2.height) :
	    toBeRemoved.add(x2)
	    
	  elif (x1.x<x2.x+x2.width) and (x1.x+x1.width>x2.x) and (x1.y<x2.y+x2.height) and (x1.y+x1.height>x2.y) :
	    
	    if (x1.height*x1.width) > (x2.height*x2.width) :
	      toBeRemoved.add(x2)
	    else :
	      toBeRemoved.add(x1)
	    
	    
    print "Vertices filtered . . . . "    
    
      
    #Store the filtered node information
    #draw merged nodes
    print "Store the filtered node information as VertexObject . . . . "
    initialnodes.difference_update(toBeRemoved)
    for i in initialnodes :
      nodeInfo=driver.execute_script(GET_PARENTS,i.webElement)
      left={}
      right={}
      top={}
      bottom={}
      jsonobject=json.loads(nodeInfo)
      node = VertexObject(verID,jsonobject[0]['tagPath'],jsonobject[0]['outerHTML'],i.height,i.width,i.x,i.y,i.webElement,left,top,right,bottom)
      verID=verID+1
      myNodes.append(node)
      dr.rectangle(((i.x,i.y),(i.x+i.width,i.y+i.height)), outline = "blue")
    im.save(current_directory+"/Output/GOMORY/"+str(webURL.split('//')[1]).replace('/','_')+"_Round : 2_VertexFiltered_"+t+".png", "PNG")       
    print "Round 2 done . . . . " 
    
    im = Image.new('RGB', (pageDim['x']+100,pageDim['y']+100), (255,255,255))
    dr = ImageDraw.Draw(im)
    
    g = Graph(len(myNodes))
    for i in range(0,len(myNodes)) :
      g.vs[i]['VertexObject']=myNodes[i]
      dr.rectangle(((myNodes[i].x,myNodes[i].y),(myNodes[i].x+myNodes[i].width,myNodes[i].y+myNodes[i].height)), outline = "blue")
    #getting the neighbors
    
    print "Round 3 start : ---> graph creation and adding weights to edges "
    print "Finding Top,Bottom,Right,Left Neighbors of each node . . . . "
    for x1 in myNodes :
      leftRightLine=Set([])
      topBottomLine=Set([])
      for x in range(x1.y,x1.y+x1.height+1) :
	leftRightLine.add(x)
      for x in range(x1.x,x1.x+x1.width+1) :
	topBottomLine.add(x)
      left={}
      right={}
      top={}
      bottom={}
      for x2 in myNodes :
		  testLRLine=Set([])
		  testTBLine=Set([])
		  for x in range(x2.y,x2.y+x2.height+1) :
		    testLRLine.add(x)
		  for x in range(x2.x,x2.x+x2.width+1) :
		    testTBLine.add(x)
		  if x2!=x1 and bool(leftRightLine & testLRLine) :
		    if (x2.x+x2.width<=x1.x) :
			#calculate geometrical distance between x1 and x2
			xa=abs(x1.x-(x2.x+x2.width))
			left[x2]=xa
		    if(x2.x>=x1.x+x1.width) :
			#calculate geometrical distance between x1 and x2
			xa=abs(x2.x-(x1.x+x1.width))
			right[x2]=xa
		  if x2!=x1 and bool(topBottomLine & testTBLine) :
		    if (x2.y+x2.height<=x1.y) :
			#calculate geometrical distance between x1 and x2
			xa=abs(x1.y-(x2.y+x2.height))
			top[x2]=xa
		    if(x2.y>=x1.y+x1.height) :
			xa=abs(x2.y-(x1.y+x1.height))
			bottom[x2]=xa
      #-------------------getting nearest left neighbors-------------------------------#
      if len(left)>0 :
	min_value = min(left.itervalues())
	min_keys = [k for k in left if left[k] == min_value]
	l={}
	for m in min_keys :
	  l[m]=min_value
	x1.setLeft(l)
      #-------------------getting nearest right neighbors-------------------------------#
      if len(right)>0 :
	min_value = min(right.itervalues())
	min_keys = [k for k in right if right[k] == min_value]
	l={}
	for m in min_keys :
	  l[m]=min_value
	x1.setRight(l)
      #-------------------getting nearest top neighbors-------------------------------#
      if len(top)>0 :
	min_value = min(top.itervalues())
	min_keys = [k for k in top if top[k] == min_value]
	l={}
	for m in min_keys :
	  l[m]=min_value
	x1.setTop(l)
      #-------------------getting nearest bottom neighbors-------------------------------#
      if len(bottom)>0 :
	min_value = min(bottom.itervalues())
	min_keys = [k for k in bottom if bottom[k] == min_value]
	l={}
	for m in min_keys :
	  l[m]=min_value
	x1.setBottom(l)
    
    print "Calculating Path Similarity between each neighbors to assign weights . . . . "
    for i in myNodes :
      
      if i.left :
	
	for key in i.left :
	  if(len(i.tagPath)>len(key.tagPath)) :
	    m=len(i.tagPath)
	  else :
	    m=len(key.tagPath)
	  w=1-(float(Levenshtein.distance(i.tagPath,key.tagPath))/float(m))
	  g.add_edge(i.varID,key.varID,weight = w)
	  dr.line((i.x,i.y+i.height/2, key.x+key.width, key.y+key.height/2), fill="orange")
      
      if i.right :
	
	for key in i.right :
	  if(len(i.tagPath)>len(key.tagPath)) :
	    m=len(i.tagPath)
	  else :
	    m=len(key.tagPath)
	  w=1-(float(Levenshtein.distance(i.tagPath,key.tagPath))/float(m))
	  g.add_edge(i.varID,key.varID,weight = w)
	  dr.line((i.x+i.width,i.y+i.height/2+2, key.x, key.y+key.height/2+2), fill="red")
     
      
      if i.top :
	
	for key in i.top :
	  if(len(i.tagPath)>len(key.tagPath)) :
	    m=len(i.tagPath)
	  else :
	    m=len(key.tagPath)
	  w=1-(float(Levenshtein.distance(i.tagPath,key.tagPath))/float(m))
	  g.add_edge(i.varID,key.varID,weight = w)
	  dr.line((i.x+i.width/2,i.y, key.x+key.width/2, key.y+key.height), fill="green")
     
      
      if i.bottom :
	
	for key in i.bottom :
	  w=1-(float(Levenshtein.distance(i.tagPath,key.tagPath))/float(m))
	  g.add_edge(i.varID,key.varID,weight = w)
	  dr.line((i.x+i.width/2+2,i.y+i.height, key.x+key.width/2+2, key.y), fill="black")
     
      
    g.write_svg(current_directory+"/Output/GOMORY/"+str(webURL.split('//')[1]).replace('/','_')+"_Round : 3_UnpartitionedGraph_"+t+".svg", layout=g.layout_kamada_kawai())
    #Save the plotted image initially  
    im.save(current_directory+"/Output/GOMORY/"+str(webURL.split('//')[1]).replace('/','_')+"_Round : 3_EdgeAdded_"+t+".png", "PNG")
     
    print "Round 3 end : ---> graph creation and adding weights to edges "
    print "Round 4 start : ---> Gomory Hu Based Graph Clustering "
    print "Unpartitioned Graph : ",g
    print g.es["weight"]
    gh =g.gomory_hu_tree(capacity="weight")
    gh.write_svg(current_directory+"/Output/GOMORY/"+str(webURL.split('//')[1]).replace('/','_')+"_Round : 3_Gomory-Hu-Tree_"+t+".svg", layout=g.layout_kamada_kawai())
    eh=gh.get_edgelist()
    print "Gomory Hu Tree : ",gh
    print gh.es["flow"]
    print
    print
    print "Vertex Clustering starts . . . . "
    cluster=[]
    other=Set()
    for ehh in eh :
      hh=g.es.select(_between=([ehh[0]],[ehh[1]]))
      
      if 1.0 in hh["weight"] :
	if int(ehh[0]) in other :
	  for k in cluster :
	    if int(ehh[0]) in k :
	      k.append(int(ehh[1]))
	      other.add(int(ehh[1]))
	elif int(ehh[1]) in other :
	  for k in cluster :
	    if int(ehh[1]) in k :
	      k.append(int(ehh[0]))
	      other.add(int(ehh[0]))
	else :
	  temp=[]
	  temp.append(int(ehh[0]))
	  temp.append(int(ehh[1]))
	  cluster.append(temp)
	  other.add(int(ehh[0]))
	  other.add(int(ehh[1]))
    mySet=Set()
    for m in myNodes :
      mySet.add(int(m.varID))
    
    mySet1=mySet.difference(other)
    
    for k in mySet1 :
      temp=[]
      temp.append(k)
      cluster.append(temp)
    a=0
    for key in cluster:
      a=a+1
      for k in key :
	g.vs[k]['VertexObject'].clusterID=str(a)

	print
	print
    print "Round 4 end . . . . " 
    im = Image.new('RGB', (pageDim['x']+100,pageDim['y']+100), (255,255,255))
    dr = ImageDraw.Draw(im)  
    print "Writing the result as xml . . . . "
    root = lxml.etree.Element("SegmentedPage")
    doc = etree.ElementTree(root)
    parser = HTMLParser()
    for key in cluster :
      subroot=lxml.etree.SubElement(root, "Cluster")
      x=[]
      y=[]
      for k in key :
	d=lxml.etree.SubElement(subroot, "LayoutNode")
	d.attrib["varID"]=str(g.vs[k]['VertexObject'].varID)
	d.attrib["tagPath"]=str(g.vs[k]['VertexObject'].tagPath)
	s=unicode(g.vs[k]['VertexObject'].outerHTML)
	s = s.encode('utf-8')
	d.attrib["outerHTML"]=escape(s)
	d.attrib["RectTop"]=str(g.vs[k]['VertexObject'].y)
	d.attrib["RectLeft"]=str(g.vs[k]['VertexObject'].x)
	d.attrib["RectWidth"]=str(g.vs[k]['VertexObject'].width)
	d.attrib["RectHeight"]=str(g.vs[k]['VertexObject'].height)
	d.attrib["clusterID"]=str(g.vs[k]['VertexObject'].clusterID)
	dr.rectangle(((int(g.vs[k]['VertexObject'].x)+2,int(g.vs[k]['VertexObject'].y)+2),(int(g.vs[k]['VertexObject'].x+g.vs[k]['VertexObject'].width)-2,int(g.vs[k]['VertexObject'].y+g.vs[k]['VertexObject'].height)-2)), outline = "blue")
	x.append(int(g.vs[k]['VertexObject'].x))
	x.append(int(g.vs[k]['VertexObject'].x+g.vs[k]['VertexObject'].width))
	y.append(int(g.vs[k]['VertexObject'].y))
	y.append(int(g.vs[k]['VertexObject'].y+g.vs[k]['VertexObject'].height))

      dr.rectangle(((min(x),min(y)),(max(x),max(y))), outline = "red")
   
    outFile = open(current_directory+"/Output/GOMORY/segmented_webpage.xml", 'w')
    doc.write(outFile, xml_declaration=True, encoding='utf-16') 
    #Save the plotted image initially  
    im.save(current_directory+"/Output/GOMORY/"+str(webURL.split('//')[1]).replace('/','_')+"_ClusteredVertices_"+t+".png", "PNG")
    

   
# Tear down connection    
finally :
  driver.quit() 
 
 
 
