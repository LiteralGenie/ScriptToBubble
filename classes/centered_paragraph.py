from .bbox import Bbox
from .prop_cache import PropCache
from wand.drawing import Drawing
from wand.image import Image
from functools import cached_property
import re, logging, os


class CenteredLine(PropCache):
	_dummy= Image(filename='wizard:')

	def __init__(self, text, para, para_center=(0,0), metrics=None, **kwargs):
		super().__init__(**kwargs)

		self._text= text
		self.paragraph= para

		if metrics is None:
			self.metrics= self._set_metrics(text)
		else:
			self.metrics= metrics

		self._set_bbox(self.metrics)
		self._bbox.center= (para_center[0], None)
		self._bbox.linked.append(self)

	def _set_metrics(self, text):
		self.metrics= self.paragraph.draw.get_font_metrics(self._dummy, self._clean(text), multiline=False)

		para= self.paragraph
		h= self.metrics.y2
		if h > para.line_height:
			t= text[:17] + "..." if len(text) > 20 else text
			t+= f" / {os.path.basename(para.draw.font)} / size={para.draw.font_size}"
			logging.warning(f"Auto-adjusting paragraph spacing. Height ({h}) of line [{t}] exceeds max line height ({para.line_height})")

			para.line_height= h
			para.spacing= 0

		return self.metrics

	def _set_bbox(self, metrics):
		if hasattr(self, '_bbox'):
			x,y= self._bbox.pos
			old_center= self._bbox.center
		else:
			x,y= 0,0
			old_center= None

		self._bbox= Bbox(
			x=x, y=y,
			w=metrics.text_width,
			h=metrics.y2,
			linked=[self]
		)
		if old_center:
			self._bbox.center= old_center

		return self._bbox

	def invalidate(self):
		pass

	@property
	def text(self):
		return self._text
	@text.setter
	def text(self, val):
		self._text= val
		self._set_metrics(val)
		self.recache()

	@property
	def bbox(self):
		return self._bbox
	@bbox.setter
	def bbox(self, val):
		self._bbox= val
		self.recache()

	@staticmethod
	def _clean(x):
		return re.sub(r'[.,;:\'"\]\[!@#$%^&*()]+$', '', x)

	def __str__(self):
		return f'"{self.text}" | {self.bbox}'


class CenteredParagraph(PropCache):
	def __init__(self, text, font, font_size=15, center=(0,0), spacing=4, line_height=None, antialias=True, metrics=None, full_init=True, **kwargs):
		super().__init__(**kwargs)

		self.text= text
		split= self.text.split("\n")
		self.num_lines= len(split)

		if line_height is None:
			self.line_height= 3*font_size/4  + spacing # assume 72(?) dpi
			self.spacing= spacing
		else:
			self.line_height= line_height
			self.spacing= line_height - 3*font_size/4

		self.draw= None
		if full_init:
			self.draw= Drawing()
			self.draw.font= font
			self.draw.font_size= font_size
			self.draw.text_antialias= antialias

		# leave this at end of init
		self.lines= []
		self.lines= self._get_lines(split, center, metrics=metrics)

	def invalidate(self):
		for x in ["bbox", "center"]:
			try:
				delattr(self, x)
			except AttributeError:
				pass

			# attr= getattr(self, x, None)
			# if attr is not None:
			# 	delattr(self, x)


	def copy(self, deepcopy=False):
		ret= self.__class__(
			text=self.text, center=self.bbox.center, spacing=self.spacing,
			font="", metrics=[x.metrics for x in self.lines],
			full_init=deepcopy
		)
		if deepcopy:
			ret.draw= self.draw.clone()
		else:
			ret.draw= self.draw
		return ret

	def render(self, image):
		d= self.draw.clone()
		for l in self.lines:
			pos= l.bbox.pos
			d.text(int(pos[0]), int(pos[1]), l.text)

		d(image)
		return image

	def _get_lines(self, lst, center, metrics=None):
		# create lines
		ret= []
		for i,x in enumerate(lst):
			m= None
			if isinstance(metrics, list):
				m= metrics[i]
			ret.append(CenteredLine(x, self, para_center=center, metrics=m, linked=[self]))

		# adjust position
		total_height= self.num_lines * self.line_height
		current_height= 0
		for i,l in enumerate(ret):
			if i == 0:
				topmost_height= l.bbox.height
				current_height+= l.bbox.height
				total_height-= (self.line_height - topmost_height) # exclude whitespace for topmost line
			else:
				current_height+= self.line_height

			ypos= current_height + center[1]
			ypos-= total_height/2 # centering

			l.bbox.pos= (None, ypos)

		# clean up
		for x in ret:
			x.linked.append(self)
		return ret

	def shift(self, x=0, y=0):
		if x != 0 or y != 0:
			c= list(self.bbox.center)
			c= [c[0]+x if x else None,
				c[1]+y if y else None]
			self.bbox.center= tuple(c)
		return self

	# todo: test recache
	@cached_property
	def bbox(self):
		# if not self.lines:
		# 	return Bbox(0,0,0,0, linked=[self])

		x= min(x.bbox.pos[0] for x in self.lines)
		y= max(x.bbox.pos[1] for x in self.lines)
		w= max(x.bbox.size[0] for x in self.lines)

		h= (self.num_lines-1) * self.line_height # height of all lines except top
		h+= self.lines[0].bbox.height # height of top-most line

		return Bbox(x=x, y=y, w=w, h=h, linked_bbox=[x.bbox for x in self.lines], linked=[self])

	@cached_property
	def center(self):
		return self.bbox.center

	def __str__(self):
		t= self.text.replace("\n","\\n")
		return f'"{t}" | {self.bbox}'

	def debug(self):
		t= self.text.replace("\n","\\n")
		ret= f'"{t}" | line_height={self.line_height} | spacing={self.spacing} | {self.bbox}'
		ret+= "\n\t" + "\n\t".join(str(x) for x in self.lines)
		return ret