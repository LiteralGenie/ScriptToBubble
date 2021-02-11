from classes import CenteredParagraph
from wand.image import Image
import utils


template_path= utils.ROOT_DIR + "tests/test_data/bubbles/" + "small_round_1.png"
font_path= utils.FONT_DIR + "Noir_regular.otf"
text= "AAAA\nAAAAA\nAAAAAA"

para= CenteredParagraph(text=text, font=font_path, font_size=15, line_height=15, center=(150,150))
para.draw(Image(filename=template_path))
print(para.debug())

img= para.render(Image(filename=template_path))
img.save(filename='./1_text_rendering.png')