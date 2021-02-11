from classes import WordGroup, CenteredParagraph, Mask, Image
from utils.centering_utils import get_2d_iter
from utils.pyStatParser.stat_parser import Parser
import utils, cv2, bisect


# inits
ts= utils.Timestamp()

sentence= 'I went against my heart and I made a choice.' + ' To accept her.' # ' It was something I had to do.'
# sentence= 'AL forces are sequentially warping in from warp-safe zones 3 billion kilometers outside of the system.'

# todo: display word group as [a] [[b c] [d]] [...]
# wg= WordGroup.from_text(sentence)
tree= Parser().parse(sentence)
wg= WordGroup.from_parse_tree(tree)

template_path= utils.ROOT_DIR + "tests/test_data/bubbles/" + "big_crop_2.png"
w,h= cv2.imread(template_path).shape[:2]

font_path= utils.FONT_DIR + "Noir_regular.otf"
font_opts= dict(font=font_path, font_size=15, line_height=12)

# get possible paragraphs
scores= []
others= []
mask_tmplt,mw,mh= None, None, None
for i,text in enumerate(wg.get_break_iter()):
	ts.log(f"Scoring text shapes [{i} / {wg.num_possibilites}] ... | {text}")

	stride=5
	radius= 50
	center= (140,160)
	num_candidates= 10

	para= CenteredParagraph(text=text, center=center, **font_opts)
	if not mask_tmplt:
		mask= Mask.from_image(template_path, para)
	else:
		mask= mask_tmplt.walled_copy(para)

	# cache mask dimensions
	if mw is None or mh is None:
		mw,mh= mask.mask_shape

	# check if text fits bubble at all
	pw,ph= para.bbox.width, para.bbox.height
	if pw > mw or ph > mh:
		continue

	# initial scoring
	for coord in get_2d_iter(*center, radius=radius, stride=stride, max_x=w-1, max_y=h-1):
		score= mask.get_score(*coord)

	# filter candidates and rescore
	candidates= mask.filter_candidates(n=num_candidates, min_dist=stride-1)
	for x in candidates:
		for coord in get_2d_iter(*x.para.center, radius=stride, stride=1, max_x=w-1, max_y=h-1):
			mask.get_score(*coord)

	if not mask.sorted_scores:
		# print()
		# ts.log(f"WARNING: no scores | {mw,mh} {pw,ph} | {text}")
		# print()
		continue

	# cache mask walls
	if not mask_tmplt:
		mask_tmplt= mask.walled_copy()

	# save best score
	best_score= mask.sorted_scores[0]
	ind= bisect.bisect_right(scores, best_score.score)

	scores.insert(ind, best_score.score)
	others.insert(ind, dict(
		text=text, center=best_score.para.center, mask=mask
	))

# get best
best_para= CenteredParagraph(text=others[0]['text'], center=others[0]['center'], **font_opts)
best_mask= others[0]['mask']

# show best paragraph
best_para.render(Image(filename=template_path)).save(filename='2-2_post_center.png')
best_im= cv2.imread('./2-2_post_center.png')

# debug
heatmap= best_mask.get_heatmap(template_path)
cv2.imwrite("./2-2_heatmap.png", heatmap)

cv2.imshow(".", heatmap)
cv2.imshow('..', best_im)
tree.draw() # todo: save tree to png

cv2.waitKey(0)
cv2.destroyAllWindows()