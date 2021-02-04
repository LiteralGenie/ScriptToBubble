from .bbox import Bbox
from wand.image import Image
import re, logging, os


class CenteredLine:
	def __init__(self, text, para):
		self.text= text
		self.paragraph= para

		self.metrics= self.paragraph.draw.get_font_metrics(Image(filename='wizard:'), self._clean(text), multiline=False)

		h= self.metrics.y2
		if h > para.line_height:
			t= text[:17] + "..." if len(text) > 20 else text
			t+= f" / {os.path.basename(para.draw.font)} / size={para.draw.font_size}"
			logging.warning(f"Auto-adjusting paragraph spacing. Height ({h}) of line [{t}] exceeds max line height ({para.line_height})")

			para.line_height= h
			para.spacing= 0

		self.bbox= Bbox(
			x=0, y=0,
			w=self.metrics.text_width,
			h=self.metrics.y2
		)
		self.bbox.center= (para.center[0], None)

	@staticmethod
	def _clean(x):
		return re.sub(r'[.,;:\'"\]\[!@#$%^&*()]+$', '', x)

	def __str__(self):
		return f'"{self.text}" | {self.bbox}'