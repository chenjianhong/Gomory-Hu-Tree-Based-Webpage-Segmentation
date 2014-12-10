class VertexObject:
     
   def __init__( self,varID,tagPath,outerHTML,height,width,x,y,webElement,left,top,right,bottom):
      self.varID=varID
      self.tagPath = tagPath
      self.outerHTML = outerHTML
      self.height=height
      self.width=width
      self.x=x
      self.y=y
      self.webElement=webElement
      self.left=left
      self.top=top
      self.right=right
      self.bottom=bottom
      self.clusterID=0   
   def setLeft(self,left):
     self.left=left
   def setTop(self,top):
     self.top=top
   def setRight(self,right):
     self.right=right
   def setBottom(self,bottom):
     self.bottom=bottom
   def __del__(self):
      class_name = self.__class__.__name__
      print class_name, "destroyed" 

 
