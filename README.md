(WIP) Automatically typeset a text script onto a set of comic pages.

### Setup

Requires Python 3.8+. See `/examples/` for usage.

1. `git clone https://github.com/LiteralGenie/ScriptToBubble/`
2. `cd ScriptToBubble`
3. `git submodule init`
4. `git submodule update`   
5. `python -m pip install -r requirements.txt`
6. `python -m nltk.downloader all`

### Typesetting Process

1. Segment panels by identifying contours. <details><summary>example (from `/examples/3_panel_segmentation/`)</summary><img src=https://raw.githubusercontent.com/LiteralGenie/ScriptToBubble/master/examples/3_panel_segmentation/3-1_merged.png>
   From left-to-right:
   * Original image
   * After thresholding
   * After contour filtering (based on size, parent contours, etc)
   * After point clustering
   * Concavity identification
   * After concavity removal
   * Convex hull (reudces number of points)
   * Shrink any overlapping contours</details>
2. (todo) Identify panel ordering.
3. Segment speech bubbles via Mask-RCNN.
4. (todo) Identify speech bubble ordering.
5. Identify best text placement and shaping. 
   - The "shape" of a paragraph refers to the position of the line-breaks. Possible line break insertion points are determined by identifying clause boundaries and certain part-of-speech tags for each word / phrase. 
   - The score for a given position / shaping is calculated using rays that extend from the edges of the text ([example](https://files.catbox.moe/07gz7n.png)). Currently, the position / shaping that gives the most balanced ray distributions vertically / horizontally is assigned the best score.
   <details><summary>example (from /examples/2_text_centering/)</summary><img src=https://raw.githubusercontent.com/LiteralGenie/ScriptToBubble/master/examples/2_text_centering/2-2_merged.png>
   <br>left: Text auto-centered and with line-breaks auto-inserted
   <br>right: Heatmap of scores for each center location (with the text shape shown on left)</details>

### Todo
1. ~~Unmerge panels that are bridged by speech bubble. (Split contour by concave vertices and regroup vertices.)~~
2. Infer panel ordering.   
3. Train bubble detection model (use segmented panels)
4. GUI
5. Redo prop caching
6. Shaping with hypenation.