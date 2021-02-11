import cv2, numpy as np, random, math, itertools


# find angle (deg) between two vectors via dot product
# if signed, angle returned is relative to vec_1 (ie has range 360deg instead of 180deg)
def get_dot_angle(vec_1, vec_2, signed=True):
	numer= (vec_1[0] * vec_2[0]) + (vec_1[1] * vec_2[1])

	l1= math.sqrt(vec_1[0]**2 + vec_1[1]**2)
	l2= math.sqrt(vec_2[0]**2 + vec_2[1]**2)
	denom= l1*l2

	frac= numer/denom

	# arccos is only defined for [-1,1]
	assert abs(frac) < 1.05
	frac= min(max(frac, -1), 1)

	# get angle
	theta= math.acos( frac )
	if signed and (vec_1[1]-vec_2[1] < 0):
		theta*= -1

	# convert to degrees
	theta*= (180/math.pi)
	return theta % 360

# angle of vector with direction start --> end
# (find via dot product with (1,0))
def get_segment_angle(start, end): # todo: test
	x= end[0] - start[0]
	y= end[1] - start[1]
	return get_dot_angle(vec_1=(1,0), vec_2=(x,y), signed=True)

# find angle <ABC
def get_vertex_angle(a, b, c):
	ba= (a[0]-b[0], a[1]-b[1])
	bc= (c[0]-b[0], c[1]-b[1])
	return get_dot_angle(ba, bc, signed=True)

def arc_length(pt1, pt2): # todo: test
	dx= (pt2[0]-pt1[0])
	dy= (pt2[1]-pt1[1])
	return math.sqrt(dx**2 + dy**2)

# merge points that are close together
def merge_points(contour, max_dist=15):
	contour= list(contour)

	# loop until no changes
	flag= True
	while flag:
		flag= False
		ind= len(contour)

		# loop over segments
		while ind > 0:
			ind-= 1
			ind_2= (ind-1) % len(contour)

			pt_1= contour[ind][0]
			pt_2= contour[ind_2][0]

			if arc_length(pt_1, pt_2) <= max_dist:
				pt_avg= [pt_1[0] + pt_2[0], pt_1[1] + pt_2[1]]
				pt_avg= [round(x/2) for x in pt_avg]
				contour[ind_2]= np.array([pt_avg])

				contour.pop(ind)
				flag= True

	contour= np.array(contour)
	return contour

# merge consecutive segments with similar angles
def merge_segments(contour, min_length=20, max_angle=20):
	contour= list(contour)

	# loop until no changes
	flag= True
	while flag:
		flag= False
		ind= len(contour)

		# loop over segments
		while ind > 0:
			ind-= 1

			# use current index as center point
			pt_2= contour[ind][0]

			# get leftmost and rightmost points
			ind_1= prev_ind(ind, contour)
			pt_1= contour[ind_1][0]
			while arc_length(pt_2, pt_1) < min_length:
				ind_1= prev_ind(ind_1, contour)
				pt_1= contour[ind_1][0]

				if ind_1 == ind:
					break
			if ind_1 == ind:
				continue

			ind_3= next_ind(ind, contour)
			pt_3= contour[ind_3][0]
			while arc_length(pt_2, pt_3) < min_length:
				ind_3= next_ind(ind_3, contour)
				pt_3= contour[ind_3][0]

				if ind_3 == ind:
					break
			if ind_3 == ind:
				continue

			if not (ind != ind_1 != ind_3):
				continue

			# get angles
			theta_12= get_segment_angle(pt_1, pt_2)
			theta_23= get_segment_angle(pt_2, pt_3)
			theta_13= get_segment_angle(pt_1, pt_3)

			# compare angle of outer segment to inner segments
			diff_1= (theta_13 - theta_12) % 360
			diff_2= (theta_13 - theta_23) % 360

			def chk(x):
				x= x%360
				return (x <= max_angle) or (x >= 360- max_angle)
			if chk(diff_1) and chk(diff_2):
				# pop everything between the start / end indices (ie remove the shorter segments that were ignored)
				ind_pop= next_ind(ind_1, contour)
				to_pop= []
				while ind_pop != ind_3:
					to_pop.append(ind_pop)
					ind_pop= next_ind(ind_pop, contour)

				to_pop.sort(reverse=True)
				for x in to_pop:
					# print(f'popping {contour[x]} from btwn {pt_1} {pt_3} with angles\n\t1-2 {theta_12}\n\t2-3 {theta_23}\n\t1-3 {theta_13}')
					contour.pop(x)
				flag= True

				if len(to_pop) > 1:
					ind= min(ind, len(contour))

	contour= np.array(contour)
	return contour

def draw_contours(contours, canvas, cmin=10, cmax=255, thickness=1, out_path=None, markers=False):
	for x in contours:
		color= (random.randint(cmin,cmax), random.randint(cmin,cmax), random.randint(cmin,cmax))
		canvas= cv2.drawContours(canvas, [x], -1, color, thickness)

		if markers:
			for y in x:
				color= (0,0,255)
				cv2.drawMarker(canvas, tuple(y[0]), color, markerSize=10)

	if out_path:
		cv2.imwrite(out_path, canvas)
	return canvas

def next_ind(ind, contour):
	return (ind+1) % len(contour)
def prev_ind(ind, contour):
	return (ind-1) % len(contour)
def next_point(ind, contour):
	return contour[next_ind(ind,contour)]
def prev_point(ind, contour):
	return contour[prev_ind(ind,contour)]

# return indices of concavities
def get_concavities(contour, thresh=20, min_length=150):
	ret= []

	# get rightmost point
	right_ind= max([i for i in range(len(contour))], key=lambda i: contour[i][0][0])

	# find increment value that results in clockwise steps
	# find by checking neighbors -- whichever has smaller y-coord is clockwise direction
	prev_pt= prev_point(right_ind, contour)[0]
	next_pt= next_point(right_ind, contour)[0]

	if next_pt[1] < prev_pt[1]:
		step= 1
	else:
		step= -1

	# iterate and find
	ind= right_ind
	while (ind+step) % len(contour) != right_ind:
		ind= (ind+step) % len(contour)
		cur_pt= contour[ind][0]
		prev_pt= prev_point(ind, contour)[0]
		next_pt= next_point(ind, contour)[0]

		d_ab= arc_length(cur_pt, prev_pt)
		d_cb= arc_length(cur_pt, next_pt)
		# if arc_length(cur_pt, prev_pt) < min_length or \
		# 	arc_length(cur_pt, next_pt) < min_length:
		# 	continue

		angle= get_vertex_angle(prev_pt, cur_pt, next_pt)
		if 360-thresh <= angle <= 360:
			ret.append(ind)

			if d_ab < min_length or d_cb < min_length:
				# print(cur_pt, d_ab, d_cb)
				continue

	# return
	ret.sort()
	return ret

# return x_range, y_range, area -- (inclusive)
def _get_bbox_info(bbox):
	x1= (bbox[0], bbox[0]+bbox[2]-1)
	y1= (bbox[1], bbox[1]+bbox[3]-1)
	a1= bbox[2]*bbox[3]

	return x1,y1,a1

def get_box_overlap(box_1, box_2): # x,y,w,h
	x1,y1,a1= _get_bbox_info(box_1)
	x2,y2,a2= _get_bbox_info(box_2)

	# check no overlap
	if x1[1] < x2[0] or x2[1] < x1[0]:
		return 0

	# overlap range is max(starting points) to min(ending points)
	x_overlap= (max(x1[0], x2[0]), min(x1[1], x2[1]))
	y_overlap= (max(y1[0], y2[0]), min(y1[1], y2[1]))

	overlap= x_overlap[1] - x_overlap[0] + 1
	overlap*= y_overlap[1] - y_overlap[0] + 1

	# return
	assert overlap <= a1 and overlap <= a2
	return max(overlap/a1, overlap/a2)

def get_contour_overlap(cntr_1, cntr_2, boxes=None):
	if boxes is None:
		boxes= [cv2.boundingRect(cntr_1), cv2.boundingRect(cntr_2)] # x,y,w,h

	box_1,box_2= boxes
	x1,y1,a1= _get_bbox_info(box_1)
	x2,y2,a2= _get_bbox_info(box_2)

	# draw contour regions and get overlap
	dims= (max(y2+y1), max(x2+x1))
	canvas= np.zeros(dims, dtype=np.uint8)

	draw1= cv2.drawContours(canvas.copy(), [cntr_1], -1, 1, cv2.FILLED)
	draw2= cv2.drawContours(canvas.copy(), [cntr_2], -1, 1, cv2.FILLED)
	canvas= np.bitwise_and(draw1, draw2)

	overlap= cv2.findNonZero(canvas)
	if overlap is None:
		return 0
	overlap= len(overlap)

	# return
	assert overlap <= a1 and overlap <= a2
	return max(overlap/a1, overlap/a2)

# returns 2-tuples of indices of overlapping contours
# first index is always larger contour
def iter_overlaps(contours, thresh=0.85):
	boxes= [cv2.boundingRect(x) for x in contours]
	for i,j in itertools.combinations(range(len(contours)), 2):
		# inits
		base= contours[i]
		other= contours[j]
		base_bbox= boxes[i]
		other_bbox= boxes[j]

		# check bbox overlap (which gives max overlap)
		if get_box_overlap(base_bbox, other_bbox) < thresh:
			continue

		# get actual overlap
		if get_contour_overlap(base, other, [base_bbox, other_bbox]):
			_,_,a1= _get_bbox_info(base_bbox)
			_,_,a2= _get_bbox_info(other_bbox)

			if a1 >= a2:
				yield i,j
			else:
				yield j,i