from .bbox import Bbox
from wand.image import Image
import re


class CenteredLine:
	def __init__(self, text, para):
		self.text= text
		self.paragraph= para

		self.metrics= self.paragraph.draw.get_font_metrics(Image(filename='wizard:'), self._clean(text), multiline=False)

		self.bbox= Bbox(
			x=0, y=0,
			w=self.metrics.text_width,
			h=self.metrics.text_height
		)
		self.bbox.center= (para.center[0], None)

	@staticmethod
	def _clean(x):
		return re.sub(r'[.,;:\'"\]\[!@#$%^&*()]+$', '', x)

	def __str__(self):
		return f'"{self.text}" | {self.bbox}'