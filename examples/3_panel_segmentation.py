import cv2, numpy as np, random, math
from utils.segment_utils import *


# inits
im_path= r"./3-0_input_1.png"
im= cv2.imread(im_path)
im_gray= cv2.cvtColor(im, cv2.COLOR_BGR2GRAY)

# threshold and find contours
_, im_gray= cv2.threshold(im_gray, 240, 255, cv2.THRESH_BINARY)
contours,hierarchy = cv2.findContours(im_gray, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
cv2.imwrite('3-1_post_thresh.png', im_gray)

# filter contours
canvas= np.zeros(im.shape, dtype=np.uint8)
contours= [x for i,x in enumerate(contours) if hierarchy[0][i][3] <= 0] # only outermost contours (allow both 0 and -1 because -1 may be contour for page)
contours= [x for x in contours if cv2.contourArea(x) >= 100*100]
tmp= draw_contours(contours, canvas.copy(), out_path='3-2_post_filters.png')

# # merge consecutive segments with similar angles
for i,cntr in enumerate(contours):
	contours[i]= merge_segments(cntr)
tmp= draw_contours(contours, canvas.copy(), out_path='3-3_post_merge.png', markers=True)

# # merge clustered points
for i,cntr in enumerate(contours):
	filtered= merge_points(cntr)
	if len(filtered):
		contours[i]= filtered
tmp= draw_contours(contours, canvas.copy(), out_path='3-4_post_clustering.png', markers=True)

# close contours
for i,cntr in enumerate(contours):
	epsilon= 75
	# contours[i]= cv2.approxPolyDP(cntr, epsilon, closed=True)
	contours[i]= cv2.convexHull(cntr)
tmp= draw_contours(contours, canvas.copy(), out_path='3-5_post_hull.png', markers=True)