Dumps a text script onto a comic page with empty speech bubbbles.  

## Setup

Requires Python 3.8+. See `/examples/` for example code.

1. `git clone https://github.com/LiteralGenie/ScriptToBubble/`
2. `cd ScriptToBubble`
3. `git submodule init`
4. `git submodule status`
5. `python -m pip install -r requirements.txt`
6. `python -m nltk.downloader all`

### Todo
1. Unmerge panels that are bridged by speech bubble. (Split contour by concave vertices and regroup vertices.)
2. Infer panel ordering.   
3. Train bubble detection model (use segmented panels)
4. GUI
5. Redo prop caching