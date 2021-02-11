from classes import CenteredParagraph
from wand.image import Image
import utils


template_path= utils.ROOT_DIR + "tests/test_data/bubbles/" + "small_round_1.png"
font_path= utils.FONT_DIR + "Noir_regular.otf"
text= "Lorem ipsum\ndolor sit amet..."

para= CenteredParagraph(text=text, center=(150,150),
						font=font_path, font_size=12, line_height=12)
para.draw(Image(filename=template_path))
print(para.debug())

img= para.render(Image(filename=template_path))
img.save(filename='./1_text_rendering.png')