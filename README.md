# M5GO-Conway, an implementation of Conway's game of life on the M5GO, with Zoom, Set and Move functions!
## Installation
Use the python flasher in https://flow.m5stack.com/ to upload the contents od Conway.py to your M5GO

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

### 'Move' mode
Press button `C` to turn the cursor direction 90 degrees clockwise   
- Debug text: `Direction: {cursorDirection}`   

Press button `A` to advance the cursor by 1 cell  
- Debug text: `Direction: {cursorDirection}`  

### 'Zoom' mode
Press button `C` to reduce the cell render size by 1px
- Debug text: `zoom: {cellSize}`  

Press button `A` to increase the cell render size by 1px   
- Debug text: `zoom: {cellSize}`  

### 'Set' mode
When in this mode, stimulation is paused  
Press button `A` and `C` at the same time to toggle the state of the cursor cell  
Press button `C` to turn the cursor direction 90 degrees clockwise  
- Debug text: `Direction: {cursorDirection}`

Press button `A` to advance the cursor by 1 cell
- Debug text: `Direction: {cursorDirection}`
