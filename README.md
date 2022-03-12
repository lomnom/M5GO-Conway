# M5GO-Conway, a fast<sub>[1]</sub> implementation of Conway's game of life on the M5GO, with Zoom, Set and Move functions!
<sub>[1]</sub>: Fast for the hardware that it runs on
## Installation
Use the python flasher in https://flow.m5stack.com/ to upload the contents of Conway.py to your M5GO

## Usage
```
+-------------+
| +---------+ |
| | Display | |
| |         | |
| +---------+ |
| [A] [B] [C] |
+-------------+
```
Cursor: hollow red square around the cell in the middle of the screen  
Debug text: text at the top left of the screen 

### Changing modes
Press button `B` to cycle through the modes `Move`, `Zoom`, and `Set`  
- Debug text: `Mode: {mode}`  

### Pausing and unpausing stimulation:  
Press button `A`, `B` and `C` together   
- Debug text: `Paused: {isPaused}`  

### Extra info text
Press button `A` and `B` together to toggle extra info text  
- Extra info at bottom left
  ```
  {ms}ms
  Gen: {generation}
  X{xCoord} Y{yCoord}
  ```
 - Debug text: `Info: {infoOn}`

Press button `B` and `C` to reset the generation counter
- Debug text: `Generation reset`

### 'Move' mode
Press button `A` and `C` to toggle FastMove, that causes the cursor to move in large steps  

Press button `C` to turn the cursor direction 90 degrees clockwise   
- Debug text: `Direction: {cursorDirection}`   

Press button `A` to advance the cursor by 1 cell, or 75% of the screen, if FastMove is enabled.  
- Debug text: `Direction: {cursorDirection}`  

### 'Zoom' mode
Press button `C` to reduce the cell render size by 1px
- Debug text: `zoom: {cellSize}`  

Press button `A` to increase the cell render size by 1px   
- Debug text: `zoom: {cellSize}`  

### 'Set' mode
When in this mode, stimulation is paused  
Press button `A` and `C` at the same time to toggle the state of the cursor cell  
- Debug text: `State: {state}`

Press button `C` to turn the cursor direction 90 degrees clockwise  
- Debug text: `Direction: {cursorDirection}`

Press button `A` to advance the cursor by 1 cell
- Debug text: `Direction: {cursorDirection}`

### Load .cells file
Place the file in the root directory of the sd card, as `pattern.cells`
