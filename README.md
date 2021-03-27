(WIP) Automatically typeset a text script onto a set of comic pages.

### Setup

Requires Python 3.8+. See `/examples/` for example code.

1. `git clone https://github.com/LiteralGenie/ScriptToBubble/`
2. `cd ScriptToBubble`
3. `git submodule init`
4. `git submodule update`   
5. `python -m pip install -r requirements.txt`
6. `python -m nltk.downloader all`

### Typesetting Process

1. Segment panels by identifying contours.
2. (todo) Identify panel ordering.
3. Segment speech bubbles via Mask-RCNN.
4. (todo) Identify speech bubble ordering.
5. Identify best text placement and shaping. 
   - The "shape" of a paragraph refers to the position of the line-breaks. Possible line break insertion points are determined by identifying clause boundaries and certain part-of-speech tags for each word / phrase. 
   - The score for a given position / shaping is calculated using rays that extend from the edges of the text ([example](https://files.catbox.moe/07gz7n.png)). Currently, the position / shaping that gives the most balanced ray distributions vertically / horizontally is assigned the best score. 

### Todo
1. Unmerge panels that are bridged by speech bubble. (Split contour by concave vertices and regroup vertices.)
2. Infer panel ordering.   
3. Train bubble detection model (use segmented panels)
4. GUI
5. Redo prop caching
6. Shaping with hypenation.