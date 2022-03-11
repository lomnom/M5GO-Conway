from m5stack import *
from math import ceil, floor
import time

WHITE=0xFFFFFF
GREY=0xAAAAAA
BLACK=0x000000

CYAN=0x00FFFF
RED=0xFF0000

HEIGHT=240
WIDTH=320

lcd.clear(BLACK)

class InfGrid: #infinite grid of 2-states
  def __init__(self,grid=None):
    grid=grid if grid else {}
    self.grid=grid # dict{set{int}}
    
  def __getitem__(self,index):
    x=index.start
    y=index.stop
    if y in self.grid:
      row=self.grid[y]
      if x in row: #check if x coordinate in set of coordinates for row
        return True
      else:
        return False
    else:
      return False
  
  def __setitem__(self,index,value):
    x=index.start
    y=index.stop
    if value:
      if y in self.grid:
        rowSet=self.grid[y] #get set of dictated row if already exists
      else:
        rowSet=set() #make a new set otherwise
        self.grid[y]=rowSet
      rowSet.add(x) #add the x coord to the set of x coords for row
    else:
      if y in self.grid: 
        rowSet=self.grid[y]
        if x in rowSet: #remove item from set of coords in row if exists
          rowSet.remove(x)
        if len(rowSet)==0: #delete row set if no other coords
          del self.grid[y]
    
  def copy(self): #copy the infinite grid
    newGrid={}
    for index in self.grid:
      newGrid[index]=self.grid[index].copy()
    return InfGrid(grid=newGrid)
  
  def __iter__(self): #iterate through every coordinate
    for y in self.grid:
      for x in self.grid[y]:
        yield (x,y)

class Conway:
  sides=[
    lambda x,y: (x+1,y+1),
    lambda x,y: (x-1,y-1),
    lambda x,y: (x+1,y-1),
    lambda x,y: (x-1,y+1),
    lambda x,y: (x-1,y),
    lambda x,y: (x+1,y),
    lambda x,y: (x,y-1),
    lambda x,y: (x,y+1)
  ]
  def __init__(self):
    self.grid=InfGrid()
    self.oldGrid=InfGrid()

  def neighbours(self,x,y): #get neighbours of a cell
    neighbourN=0
    for side in self.sides:
      sX,sY=side(x,y)
      neighbourN+=int(self.grid[sX:sY])
    return neighbourN
  
  def tick(self): #advance the generation
    newGrid=InfGrid()
    toTick=set()
    for x,y in self.grid:
      for side in self.sides:
        toTick.add(side(x,y))

    for x,y in toTick: #stimulate every cell that needs to be stimutlated
      besideN=self.neighbours(x,y)
      if (besideN==3 or besideN==2) and self.grid[x:y]:
        newGrid[x:y]=True 
      elif besideN==3 and not self.grid[x:y]:
        newGrid[x:y]=True
    
    self.oldGrid=self.grid
    self.grid=newGrid
  
  #   x: top left x of matrix in rendered 
  #   y: top left y of matrix in rendered
  #   zoom: size of every rendered cell
  #   color: fill color of cell
  #   border: border color of cell
  #   cleared: color of cells that are cleared on render
  def showGrid(self,x,y,zoom,color=WHITE,border=GREY,cleared=BLACK):
    rawGrid=self.grid.grid
    rawOldGrid=self.oldGrid.grid
    rEndX=x+ceil(WIDTH/zoom) #ends of stimulated part of matrix
    rEndY=y+ceil(HEIGHT/zoom)
    
    if zoom>1: #fix rect not rendering when size is 1*1
      rect=lcd.rect
    else:
      rect=lambda x,y,w,h,b,color: lcd.pixel(x,y,color)
    
    for row in range(y,rEndY+1):
      rowExists=row in rawGrid
      if rowExists:
        posY=(row-y)*zoom #y coordinate to draw squares
        rowSet=rawGrid[row] #cache set
        for item in rowSet:
          if rEndX>=item>=x:
            rect((item-x)*zoom,posY,zoom,zoom,border,color) #render item if within viewport
      
      if row in rawOldGrid: #remove old filled items
        posY=(row-y)*zoom
        for item in rawOldGrid[row]: 
          if rEndX>=item>=x and not (rowExists and item in rowSet):
            rect((item-x)*zoom,posY,zoom,zoom,cleared,cleared) #clear old items

cogol=Conway()

#glider
# cogol.grid[0:-1]=True
# cogol.grid[-1:-1]=True
# cogol.grid[1:-1]=True
# cogol.grid[1:0]=True
# cogol.grid[0:1]=True

#blinker
cogol.grid[0:0]=True
cogol.grid[1:0]=True
cogol.grid[-1:0]=True

from utime import sleep

MOVE=0
ZOOM=1
SET=2
NMODES=3

modes=["move","zoom","set","quit"]

mode=MOVE

zoom=6
x = -floor((WIDTH/2)/zoom)
y = -floor((HEIGHT/2)/zoom)

def text(txt):
  lcd.clear(BLACK)
  lcd.text(12,12,txt,RED)

direction=(0,-1)
turn=lambda dir: (-dir[1],dir[0])
paused=False
  
directions={
  (0,1): "down",
  (1,0): "right",
  (0,-1):"up",
  (-1,0):"left"
}

text("mode: move")

while True:
  midSqMX=floor(WIDTH/2/zoom)
  midSqMY=floor(HEIGHT/2/zoom)
  tickstartms=time.ticks_ms()
  
  cogol.showGrid(x,y,zoom)
  if mode!=SET and not paused:
    cogol.tick()
    
  if zoom>1:
    lcd.rect(midSqMX*zoom,midSqMY*zoom,zoom,zoom,RED)
  if zoom==1:
    lcd.pixel(midSqMX*zoom,midSqMY*zoom,RED)
  
  time.sleep_ms(100-(time.ticks_ms()-tickstartms))

  btnBpressed=btnB.wasPressed()
  btnCpressed=btnC.wasPressed()
  btnApressed=btnA.wasPressed()
  
  if btnApressed and btnBpressed and btnCpressed:
    paused=not paused
    text("Paused: "+str(paused))
  elif btnBpressed:
    mode+=1
    mode=mode%NMODES
    text("Mode: "+modes[mode])
  elif btnApressed:
    if mode==MOVE:
      x+=direction[0]
      y+=direction[1]
      text("Direction: "+directions[direction])
    elif mode==ZOOM:
      zoom -= 1 if zoom > 1 else 0
      text("zoom: "+str(zoom))
      newMidSqMX=floor(WIDTH/2/zoom)
      newMidSqMY=floor(HEIGHT/2/zoom)
      x-= newMidSqMX-midSqMX
      y-= newMidSqMY-midSqMY
    elif mode==SET:
      if btnCpressed:
        cogol.oldGrid=cogol.grid.copy()
        state=cogol.grid[midSqMX+x:midSqMY+y]
        cogol.grid[midSqMX+x:midSqMY+y]=not state
        text("State: "+("live" if state else "dead"))
      else:
        x+=direction[0]
        y+=direction[1]
        text("Direction: "+directions[direction])
  elif btnCpressed:
    if mode==MOVE or mode==SET:
      direction=turn(direction)
      text("Direction: "+directions[direction])
    elif mode==ZOOM:
      zoom+=1
      newMidSqMX=floor(WIDTH/2/zoom)
      newMidSqMY=floor(HEIGHT/2/zoom)
      x-= newMidSqMX-midSqMX
      y-= newMidSqMY-midSqMY
      text("zoom: "+str(zoom))
