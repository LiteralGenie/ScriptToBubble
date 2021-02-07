from classes import *
from wand.image import Image
import utils, cv2


# inits
ts= utils.Timestamp()
template_path= utils.ROOT_DIR + "tests/test_data/bubbles/" + "big_crop_2.png"
font_path= utils.FONT_DIR + "Noir_regular.otf"
text= "We have to go.\nI'm almost\nhappy here."

para= CenteredParagraph(text=text, font=font_path, font_size=15, line_height=12, center=(140,160))
mask= Mask.from_image(template_path, para)

# show image + paragraph info
print(para.debug(), "\n")
para.render(Image(filename=template_path)).save(filename='2_pre_center.png')


# initial scan
stride= 5
x_min= 100
x_max= 200
y_min= 100
y_max= 200

for i in range(x_min, x_max, stride):
	for j in range(y_min, y_max, stride):
		s= mask.get_score(i, j)
		ts.log(f"Initial scan... | {(i,j)} | {s.score if s else None}")
print()

# find most promising locations and rescan
num_candidates= 10
candidates= mask.filter_candidates(num_candidates, stride-1)

for x in candidates:
	ctr= x.para.center
	range_x= range(-(stride-1), stride)
	range_y= range(-(stride-1), stride)
	for i in range_x:
		for j in range_y:
			s= mask.get_score(ctr[0] + i, ctr[1] + j)
			ts.log(f"Checking candidates... | {(i,j)} | {s.score if s else None}")
print()

# choose best position
para.bbox.center= mask.sorted_scores[0].para.bbox.center
para.render(Image(filename=template_path)).save(filename='2_post_center.png')

# get heatmap of position scores
heatmap= mask.get_heatmap(template_path)
cv2.imwrite("./2_heatmap.png", heatmap)
cv2.imshow(".", heatmap)
cv2.waitKey(0)
cv2.destroyAllWindows()