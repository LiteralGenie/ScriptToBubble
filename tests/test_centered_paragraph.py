from wand.image import Image
from classes import CenteredParagraph, CenteredLine, Bbox
import unittest, utils


class CenteredParagraphTests(unittest.TestCase):
	def setUp(self):
		self.para_args= dict(
			text="We have to go.\nI'm almost happy here.",
			font= utils.FONT_DIR + "Noir_regular.otf",
		)
		self.im_args= dict(
			width=1000,
			height=1000
		)

	def test_init(self):
		# inits
		init_cx= 100
		init_cy= 200
		para= CenteredParagraph(**self.para_args, center=(init_cx, init_cy))

		# check center
		self.assertEqual(para.bbox.center, (100,200))
		for x in para.lines:
			self.assertEqual(x.bbox.center_x, init_cx, f'Line [{para.lines.index(x)}] is not at paragraph center.')

		# check line heights
		for i in range(1,len(para.lines)):
			diff= para.lines[i].bbox.y - para.lines[i-1].bbox.y
			self.assertEqual(diff, para.line_height)

	def test_center_move(self):
		# inits
		init_cx= 100
		init_cy= 200
		para= CenteredParagraph(**self.para_args, center=(init_cx, init_cy))

		def get_prop(key_name):
			return [para.bbox.__getattribute__(key_name)] +\
				   [line.bbox.__getattribute__(key_name) for line in para.lines]
		def check_prop_shift(old, shift, prop_name):
			new= get_prop(prop_name)
			diffs= [x[1]-x[0] for x in zip(old,new)]

			for i in range(len(diffs)):
				name= "paragraph" if i == 0 else f"line {i-1}"
				self.assertEqual(
					diffs[i], shift,
					f'prop [{prop_name}] for [{name}] shifted by [{diffs[i]}] but expected shift was [{shift}].'
				)

		old_x= get_prop('x')
		old_center_x= get_prop('center_x')
		old_y= get_prop('y')
		old_center_y= get_prop('center_y')


		# move center horiz
		shift= 50
		para.bbox.center= (init_cx + shift, None)

		check_prop_shift(old_x, shift, 'x')
		check_prop_shift(old_center_x, shift, 'center_x')
		check_prop_shift(old_y, 0, 'y')
		check_prop_shift(old_center_y, 0, 'center_y')

		para.bbox.center= (init_cx, init_cy)


		# move center vert
		shift= -25000
		para.bbox.center= (None, init_cy + shift)

		check_prop_shift(old_x, 0, 'x')
		check_prop_shift(old_center_x, 0, 'center_x')
		check_prop_shift(old_y, shift, 'y')
		check_prop_shift(old_center_y, shift, 'center_y')

		para.bbox.center= (init_cx, init_cy)


	def test_line_move(self):
		# @todo: check that moving line affects para center
		pass


if __name__ == "__main__":
	unittest.main()