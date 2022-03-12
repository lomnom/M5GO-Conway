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
  
  def neighbours(self,x,y): #get neighbours of a cell
    n=0
    rawGrid=self.grid.rawgrid
    row=rawGrid.get(y+1)
    if row:
      n+= (x+1 in row)+(x in row)+(x-1 in row)
    row=rawGrid.get(y)
    if row:
      n+= (x+1 in row)+(x-1 in row)
    row=rawGrid.get(y-1)
    if row:
      n+= (x+1 in row)+(x in row)+(x-1 in row)
    return n
  
  def tick(self): #advance the generation
    del self.oldGrid
    #Implementing a cache for items to tick just made the device run out of ram
    #Putting a limit on the cache made the algorithm slower than the original
    #This is optimal.
    newGrid=InfGrid()
    sides=((1,1),(0,1),(-1,1),(1,0),(-1,0),(1,-1),(0,-1),(-1,-1))
    
    for gx,gy in self.grid:
      for ox,oy in sides:
        x,y=gx+ox,gy+oy
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

cogol=Conway()

for x,y in ((-1,0),(0,0),(1,0)):
  cogol.grid[x:y]=True

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
  
  ctime=time.ticks_ms()
  if ctime>tickstartms: #overfflow check
    time.sleep_ms(100-(time.ticks_ms()-tickstartms)) #make every frame 100ms
  else:
    time.sleep_ms(100)

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
      text("State: "+("live" if not state else "dead"))
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
      
