from utils.segment_utils import draw_contours, iter_overlaps, get_concavities, merge_points
import cv2, numpy as np


# inits
im_path= r"3-0_input_1.png"
im= cv2.imread(im_path)
im_gray= cv2.cvtColor(im, cv2.COLOR_BGR2GRAY)

# threshold and find contours
_, im_gray= cv2.threshold(im_gray, 240, 255, cv2.THRESH_BINARY)
contours,hierarchy = cv2.findContours(im_gray, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
cv2.imwrite('3-1_post_thresh.png', im_gray)

# filter contours
canvas= np.zeros(im.shape, dtype=np.uint8)
tmp= []
tmp2= [x for i,x in enumerate(contours) if hierarchy[0][i][3] == -1]
for i,x in enumerate(contours):
	if hierarchy[0][i][3] > 0: # only outermost contours
		continue
	if cv2.contourArea(x) < 100*100: # only if suff. large
		continue
	if hierarchy[0][i][3] == -1 and len(tmp2) <= 2: # remove page-sized contour
		continue
	tmp.append(x)
contours= tmp
out_im= draw_contours(contours, canvas.copy(), out_path='3-2_post_filters.png', markers=False)

# smooth edges
for i,cntr in enumerate(contours):
	epsilon= 0.001*cv2.arcLength(cntr, True)
	contours[i]= cv2.approxPolyDP(cntr, epsilon, True)
out_im= draw_contours(contours, canvas.copy(), out_path='3-3_post_smoothing.png', markers=True)

# merge clustered points
for i,cntr in enumerate(contours):
	filtered= merge_points(cntr, max_dist=5)
	if len(filtered):
		contours[i]= filtered
out_im= draw_contours(contours, canvas.copy(), out_path='3-4_post_clustering.png', markers=True)

# id concavities
concavities= []
for i,cntr in enumerate(contours):
	caves= get_concavities(cntr)
	for j in caves:
		coord= tuple(cntr[j][0])
		cv2.drawMarker(out_im, coord, (0,255,0), thickness=2)
	concavities.append(caves)
cv2.imwrite('3-4_post_clustering.png', out_im)

# subdivide contour if multiple concavities
tmp_lst= list(enumerate(contours))
for i,cntr in tmp_lst:
	caves= concavities[i]
	if len(caves) > 1:
		new_contours= []
		ind= 0
		while ind < len(caves)-1:
			c= caves[ind]
			c_next= caves[ind+1]

			tmp= cntr[c:c_next+1]
			new_contours.append(tmp)

			ind+= 1

		# join first / last
		tmp= list(cntr[caves[ind]:]) + list(cntr[:caves[0]+1])
		contours[i]= np.array(tmp)
		contours+= new_contours
out_im= draw_contours(contours, canvas.copy(), out_path='3-5_post_divide.png', markers=True)

# close contours
for i,cntr in enumerate(contours):
	epsilon= 75
	# contours[i]= cv2.approxPolyDP(cntr, epsilon, closed=True)
	contours[i]= cv2.convexHull(cntr)
tmp= draw_contours(contours, canvas.copy(), out_path='3-6_post_hull.png', markers=True)

# remove nested contours
while True:
	for x in iter_overlaps(contours):
		contours.pop(x[0])
		break # recreate iter because indices have changed
	else:
		break
tmp= draw_contours(contours, canvas.copy(), out_path='3-7_post_unoverlap.png', markers=True)
