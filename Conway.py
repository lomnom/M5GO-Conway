from m5stack import *
import gc

ceil=lambda n: round(n+0.5)
floor=lambda n: round(n-0.5)

lcd.font(lcd.FONT_DefaultSmall)

#some constants
WHITE=0xFFFFFF
GREY=0xAAAAAA
BLACK=0x000000

CYAN=0x00FFFF
RED=0xFF0000
GREEN=0x00FF00

HEIGHT=240
WIDTH=320

TXTLINE=lcd.fontSize()[1]

lcd.clear(BLACK)

class InfGrid: #infinite grid of 2-states
  def __init__(self,grid=None):
    grid=grid if grid else {}
    self.rawgrid=grid # dict{int:set{int}}
    
  def __getitem__(self,index): #slice(x,y,None)
    x=index.start
    y=index.stop
    
    rowSet=self.rawgrid.get(y)
    if rowSet:
      return x in rowSet
    else:
      return False
  
  def __setitem__(self,index,value):
    x=index.start
    y=index.stop
    rowSet=self.rawgrid.get(y)
    if value:
      if not rowSet:
        rowSet=set() #make a new set if row doesnt exist
        self.rawgrid[y]=rowSet
      rowSet.add(x) #add the x coord to the set of x coords for row
    else:
      if rowSet: 
        rowSet.discard(x)
        if not rowSet: #delete row set if no other coords
          del self.rawgrid[y]
    
  def copy(self): #copy the infinite grid
    newGrid={}
    for index in self.rawgrid:
      newGrid[index]=self.rawgrid[index].copy()
    return InfGrid(grid=newGrid)
  
  def __iter__(self): #iterate through every coordinate
    for y in self.rawgrid:
      for x in self.rawgrid[y]:
        yield (x,y)

class Conway: #representation of conway's game of life
  def __init__(self):
    self.grid=InfGrid()
    self.oldGrid=InfGrid()
    self.generation=0
    self.population=0
    self.oldPopulation=0
  
  def tick(self): #advance the generation
    del self.oldGrid
    #Implementing a cache for items to tick just made the device run out of ram
    #Putting a limit on the cache made the algorithm slower than the original
    #This is optimal.
    self.oldPopulation=self.population
    self.population=0
    newGrid=InfGrid()
    rawGrid=self.grid.rawgrid
    rawNewGrid=newGrid.rawgrid
    sides=((1,1),(0,1),(-1,1),(1,0),(-1,0),(1,-1),(0,-1),(-1,-1))
    
    rowSetCache=[]
    newSetCache=[]
    
    prevRow=None
    for row in sorted(rawGrid):
      cacheUnshared=(row-prevRow if not prevRow is None else 69)
      newCacheUnshared=(cacheUnshared if cacheUnshared<=3 else 3)
      cacheUnshared=(cacheUnshared if cacheUnshared<=5 else 5)
      rowSetCache=rowSetCache[cacheUnshared:]
      newSetCache=newSetCache[newCacheUnshared:]
      rowSetCache+=[rawGrid.get(row+n) for n in range((3-cacheUnshared),3)]
      newSetCache+=[rawNewGrid.get(row+n) for n in range((2-newCacheUnshared),2)]
      for col in rowSetCache[2]:
        for ox,oy in sides:
          x,y=col+ox,row+oy
          currNewRow=newSetCache[1+oy]
          if currNewRow and x in currNewRow: continue

          rowSet=rowSetCache[2+oy]
          rowUpSet=rowSetCache[3+oy]
          rowDownSet=rowSetCache[1+oy]
          
          beside=0
          if rowUpSet:
            beside+= (x+1 in rowUpSet)+(x in rowUpSet)+(x-1 in rowUpSet)
          if rowSet:
            beside+= (x+1 in rowSet)+(x-1 in rowSet)
          if beside<4 and rowDownSet:
            beside+= (x+1 in rowDownSet)+(x in rowDownSet)+(x-1 in rowDownSet)
          
          if beside==3 or (beside==2 and rowSet and x in rowSet):
            if not currNewRow:
              currNewRow=set()
              newSetCache[1+oy]=currNewRow
              rawNewGrid[y]=currNewRow
            currNewRow.add(x)
            self.population+=1
    
    self.oldGrid=self.grid
    self.grid=newGrid
    self.generation+=1
  
  #   x: top left x of matrix in rendered 
  #   y: top left y of matrix in rendered
  #   zoom: size of every rendered cell
  #   color: fill color of cell
  #   border: border color of cell
  #   cleared: color of cells that are cleared on render
  def showGrid(self,x,y,zoom,color=WHITE,border=GREY,cleared=BLACK):
    rawGrid=self.grid.rawgrid
    rawOldGrid=self.oldGrid.rawgrid
    rEndX=x+ceil(WIDTH/zoom) #ends of stimulated part of matrix
    rEndY=y+ceil(HEIGHT/zoom)
    
    if zoom>1: #fix rect not rendering when size is 1*1
      rect=lcd.rect
    else:
      rect=lambda x,y,w,h,b,color: lcd.pixel(x,y,color)
    
    for row in range(y,rEndY+1):
      rowSet=rawGrid.get(row)
      if rowSet:
        posY=(row-y)*zoom #y coordinate to draw squares
        for item in rowSet:
          if rEndX>=item>=x:
            rect((item-x)*zoom,posY,zoom,zoom,border,color) #render item if within viewport
      
      oldRowSet=rawOldGrid.get(row)
      if oldRowSet: #remove old filled items
        posY=(row-y)*zoom
        for item in oldRowSet: 
          if rEndX>=item>=x and not (rowSet and item in rowSet):
            rect((item-x)*zoom,posY,zoom,zoom,cleared,cleared) #clear old items
            
def cellsIter(file):
  file=open("/sd/{}.cells".format(file),"r")
  line=file.readline()
  while line[0]=="!":
    line=file.readline()
  file.seek(file.tell()-len(line))
  
  x,y=0,0
  char=file.read(1)
  while char:
    if char=='.':
      x+=1
    elif char=='O':
      x+=1
      yield (x,y)
    elif char=='\n':
      y+=1
      x=0
    char=file.read(1)

cogol=Conway()

MOVE=0
ZOOM=1
SET=2
NMODES=3

modes=["move","zoom","set","quit"]

mode=MOVE

zoom=6
x = -floor((WIDTH/2)/zoom) #center the center of the board
y = -floor((HEIGHT/2)/zoom)

info=False

try:
  maxX=0
  maxY=0
  for x,y in cellsIter("pattern"):
    cogol.grid[x:y]=True
    if x>maxX: maxX=x
    if y>maxY: maxY=y
  
  x=floor((maxX/2)-(WIDTH/zoom/2))
  y=floor((maxY/2)-(HEIGHT/zoom/2))
except OSError:
  for x,y in ((-1,0),(0,0),(1,0)):
    cogol.grid[x:y]=True
  x=floor((3/2)-(WIDTH/zoom/2))
  y=floor((1/2)-(HEIGHT/zoom/2))

def text(txt,clear=False):
  lcd.rect(12,12,WIDTH,TXTLINE,BLACK,BLACK) if not clear else lcd.clear()
  lcd.text(12,12,txt,RED)

infoWidth=0
def showInfo():
  global infoWidth
  lcd.rect(WIDTH-infoWidth,HEIGHT-(TXTLINE*4),infoWidth,TXTLINE*4,BLACK,BLACK)
  infoWidth=[]
  def showLine(text,n,color=RED):
    global infoWidth
    infoWidth+=[lcd.textWidth(text)]
    lcd.text(lcd.RIGHT,HEIGHT-(TXTLINE*n),text,color)
  showLine("X{} Y{}".format(x+midSqMX,y+midSqMY),1)
  showLine("Gen="+str(cogol.generation)+", Pop="+str(cogol.population),2)
  showLine(str(ctime)+"ms",3,color=GREEN if ctime<100 else RED)
  free=round(gc.mem_free()/1000)
  showLine(str(free)+"kb",4,color=GREEN if free>30 else RED)
  infoWidth=max(infoWidth)

direction=(0,-1)
turn=lambda dir: (-dir[1],dir[0])
paused=False

fastMove=False

directions={
  (0,1): "down",
  (1,0): "right",
  (0,-1):"up",
  (-1,0):"left"
}

text("mode: move",clear=True)

import utime as time

while True:
  gc.collect()
  
  midSqMX=floor(WIDTH/2/zoom) # difference between x and x of in the middle of screen
  midSqMY=floor(HEIGHT/2/zoom)
  tickstartms=time.ticks_ms()
  
  if info:
    showInfo()
    
  cogol.showGrid(x,y,zoom)
  
  if mode!=SET and not paused:
    cogol.tick()
    
  if zoom>1: #render cursor
    lcd.rect(midSqMX*zoom,midSqMY*zoom,zoom,zoom,RED)
  if zoom==1:
    lcd.pixel(midSqMX*zoom,midSqMY*zoom,RED)
  
  ctime=time.ticks_ms()-tickstartms
  if ctime>tickstartms: #overfflow check
    time.sleep_ms(100-ctime) #make every frame 100ms
  else:
    time.sleep_ms(100)

  btnBpressed=btnB.wasPressed()
  btnCpressed=btnC.wasPressed()
  btnApressed=btnA.wasPressed()
  
  if btnApressed and btnBpressed and btnCpressed: #pause
    paused=not paused
    text("Paused: "+str(paused))
  elif btnApressed and btnBpressed:
    info=not info
    text("Info: "+str(info),clear=True)
  elif btnCpressed and btnBpressed:
    cogol.generation=0
    text("Generation reset")
  elif btnBpressed: #change mode
    mode+=1
    mode=mode%NMODES
    text("Mode: "+modes[mode])
  elif btnApressed and btnCpressed:
    if mode==MOVE: #toggle fastmove
      fastMove=not fastMove
      text("FastMove: "+str(fastMove))
    elif mode==SET: #toggle cursor cell
      cogol.oldGrid=cogol.grid.copy()
      state=cogol.grid[midSqMX+x:midSqMY+y]
      cogol.grid[midSqMX+x:midSqMY+y]=not state
      text("State: "+("live" if not state else "dead"))
  elif btnApressed:
    if mode==MOVE: #advance cursor
      x+=direction[0] * (1 if not fastMove else ceil(midSqMX/5))
      y+=direction[1] * (1 if not fastMove else ceil(midSqMY/5))
      text("Direction: "+directions[direction],clear=True)
    elif mode==ZOOM: #decrease zoom
      zoom -= 1 if zoom > 1 else 0
      newMidSqMX=floor(WIDTH/2/zoom) #center what was previusly centered before the zoom
      newMidSqMY=floor(HEIGHT/2/zoom)
      x-= newMidSqMX-midSqMX
      y-= newMidSqMY-midSqMY
      text("zoom: "+str(zoom),clear=True)
    elif mode==SET: #advance cursor in set mode
      x+=direction[0]
      y+=direction[1]
      text("Direction: "+directions[direction],clear=True)
  elif btnCpressed:
    if mode==MOVE or mode==SET: #change direction
      direction=turn(direction)
      text("Direction: "+directions[direction])
    elif mode==ZOOM: #increase zoom
      zoom+=1
      newMidSqMX=floor(WIDTH/2/zoom)
      newMidSqMY=floor(HEIGHT/2/zoom)
      x-= newMidSqMX-midSqMX
      y-= newMidSqMY-midSqMY
      text("zoom: "+str(zoom),clear=True)
