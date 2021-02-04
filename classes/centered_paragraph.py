from .bbox import Bbox
from .centered_line import CenteredLine
from wand.drawing import Drawing
import utils


class CenteredParagraph:
	def __init__(self, text, font, font_size=15, center=(0,0), spacing=4, line_height=None, antialias=True):
		# spacing=0
		self.center= center

		self.text= text
		split= self.text.split("\n")
		self.num_lines= len(split)

		if line_height is None:
			self.line_height= 3*font_size/4  + spacing # assume 72(?) dpi
			self.spacing= spacing
		else:
			self.line_height= line_height
			self.spacing= line_height - 3*font_size/4

		self.draw= Drawing()
		self.draw.font= font
		self.draw.font_size= font_size
		self.draw.text_antialias= antialias

		# post-init inits
		self.lines= self._get_lines(split)

	def render(self, image):
		for l in self.lines:
			pos= l.bbox.pos
			self.draw.text(int(pos[0]), int(pos[1]), l.text)

		self.draw(image)
		return image

	def _get_lines(self, lst):
		# inits
		ret= []

		# create lines
		total_height= self.num_lines * self.line_height
		current_height= 0
		for i,x in enumerate(lst):
			l= CenteredLine(x, self)

			if i == 0:
				topmost_height= l.bbox.height
				current_height+= l.bbox.height
				total_height-= (self.line_height - topmost_height) # exclude whitespace for topmost line
			else:
				current_height+= self.line_height

			ypos= current_height + self.center[1]
			ypos-= total_height/2 # centering

			l.bbox.pos= (None, ypos)

			ret.append(l)

		# clean up
		return ret

	@property
	def bbox(self):
		x= min(x.bbox.pos[0] for x in self.lines)
		y= max(x.bbox.pos[1] for x in self.lines)
		w= max(x.bbox.size[0] for x in self.lines)

		h= (self.num_lines-1) * self.line_height # height of all lines except top
		h+= self.lines[0].bbox.height # height of top-most line

		return Bbox(x=x, y=y, w=w, h=h, linked=[x.bbox for x in self.lines])

	def __str__(self):
		t= self.text.replace("\n","\\n")
		return f'"{t}" | {self.bbox}'
