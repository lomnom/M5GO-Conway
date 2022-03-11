from m5stack import *

ceil=lambda n: round(n+0.5)
floor=lambda n: round(n-0.5)

#some constants
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

class Conway: #representation of conway's game of life
  def __init__(self):
    self.grid=InfGrid()
    self.oldGrid=InfGrid()
  
  def neighbours(self,x,y): #get neighbours of a cell
    return self.grid[x+1:y+1]+self.grid[x:y+1]+self.grid[x-1:y+1]+ \
           self.grid[x+1:y]+                     self.grid[x-1:y]+ \
           self.grid[x+1:y-1]+self.grid[x:y-1]+self.grid[x-1:y-1]
  
  def tick(self): #advance the generation
    del self.oldGrid
    newGrid=InfGrid()
    toTick=set()
    sides=((1,1),(0,1),(-1,1),(1,0),(-1,0),(1,-1),(0,-1),(-1,-1))
    
    gridIterator=self.grid.__iter__()
    iterating=True
    
    while iterating:
      cells=0
      
      try: #proccess only 30 cells and the cells around, to save ram
        while cells!=30:
          xP,yP=next(gridIterator)
          for xO,yO in sides: #iterate through cells directly around current processing
            toTick.add((xP+xO,yP+yO))
          toTick.add((xP,yP))
          cells+=1
      except StopIteration:
        iterating=False
        
      for x,y in toTick: #stimulate every cell that needs to be stimulated
        besideN=self.neighbours(x,y)
        if (besideN==3 or besideN==2) and self.grid[x:y]:
          newGrid[x:y]=True 
        elif besideN==3 and not self.grid[x:y]:
          newGrid[x:y]=True
      toTick=set()
    
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

MOVE=0
ZOOM=1
SET=2
NMODES=3

modes=["move","zoom","set","quit"]

mode=MOVE

zoom=6
x = -floor((WIDTH/2)/zoom) #center the center of the board
y = -floor((HEIGHT/2)/zoom)

def text(txt):
  lcd.clear(BLACK)
  lcd.text(12,12,txt,RED)

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

text("mode: move")

import utime as time

while True:
  midSqMX=floor(WIDTH/2/zoom) # difference between x and x of in the middle of screen
  midSqMY=floor(HEIGHT/2/zoom)
  tickstartms=time.ticks_ms()
  
  cogol.showGrid(x,y,zoom)
  if mode!=SET and not paused:
    cogol.tick()
    
  if zoom>1: #render cursor
    lcd.rect(midSqMX*zoom,midSqMY*zoom,zoom,zoom,RED)
  if zoom==1:
    lcd.pixel(midSqMX*zoom,midSqMY*zoom,RED)
  
  time.sleep_ms(100-(time.ticks_ms()-tickstartms)) #make every frame 100ms

  btnBpressed=btnB.wasPressed()
  btnCpressed=btnC.wasPressed()
  btnApressed=btnA.wasPressed()
  
  if btnApressed and btnBpressed and btnCpressed: #pause
    paused=not paused
    text("Paused: "+str(paused))
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
      text("State: "+("live" if state else "dead"))
  elif btnApressed:
    if mode==MOVE: #advance cursor
      x+=direction[0] * (1 if not fastMove else ceil(midSqMX*0.75))
      y+=direction[1] * (1 if not fastMove else ceil(midSqMY*0.75))
      text("Direction: "+directions[direction])
    elif mode==ZOOM: #decrease zoom
      zoom -= 1 if zoom > 1 else 0
      newMidSqMX=floor(WIDTH/2/zoom) #center what was previusly centered before the zoom
      newMidSqMY=floor(HEIGHT/2/zoom)
      x-= newMidSqMX-midSqMX
      y-= newMidSqMY-midSqMY
      text("zoom: "+str(zoom))
    elif mode==SET: #advance cursor in set mode
      x+=direction[0]
      y+=direction[1]
      text("Direction: "+directions[direction])
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
      text("zoom: "+str(zoom))
      
