Dumps a text script onto a comic page with empty speech bubbbles.  

## Setup

Requires Python 3.8+
See /examples/ for example code.

1. `git clone https://github.com/LiteralGenie/ScriptToBubble/`
2. `cd ScriptToBubble`
3. `git submodule init`
4. `git submodule status`

### Todo
1. Unmerge panels that are bridged by speech bubble.
   - (Find combination of 3 to 4 sided polygons with best IoU score and highest aggregate overlap with original contour area?)
2. GUI
3. Photoshop script