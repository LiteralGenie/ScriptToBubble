import cv2, numpy as np, random, math


# find angle (deg) between two points using dot product of (x2-x1, y2-y1) and (1,0)
def angle(pt1, pt2): # todo: test
		x= pt2[0] - pt1[0]
		y= pt2[1] - pt1[1]
		dist= math.sqrt(x**2 + y**2)

		numer= x
		denom= dist
		frac= numer/denom

		assert abs(frac) < 1.1
		frac= min(max(frac, -1), 1)

		theta= math.acos( frac )
		if y < 0:
			theta*= -1

		theta*= (180/math.pi)
		return theta % 360

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
def merge_segments(contour, min_length=20, max_angle=10):
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
			ind_1= (ind-1) % len(contour)
			pt_1= contour[ind_1][0]
			while arc_length(pt_2, pt_1) < min_length:
				ind_1= (ind_1-1) % len(contour)
				pt_1= contour[ind_1][0]

				if ind_1 == ind:
					break
			if ind_1 == ind:
				continue

			ind_3= (ind+1) % len(contour)
			pt_3= contour[ind_3][0]
			while arc_length(pt_2, pt_3) < min_length:
				ind_3= (ind_3+1) % len(contour)
				pt_3= contour[ind_3][0]

				if ind_3 == ind:
					break
			if ind_3 == ind:
				continue

			if not (ind != ind_1 != ind_3):
				continue

			# get angles
			theta_12= angle(pt_1, pt_2)
			theta_23= angle(pt_2, pt_3)
			theta_13= angle(pt_1, pt_3)

			# compare angle of outer segment to inner segments
			diff_1= (theta_13 - theta_12) % 360
			diff_2= (theta_13 - theta_23) % 360

			def chk(x):
				x= x%360
				return (x <= max_angle) or (x >= 360- max_angle)
			if chk(diff_1) and chk(diff_2):
				# pop everything between the start / end indices (ie remove the shorter segments that were ignored)
				ind_pop= (ind_1+1) % len(contour)
				to_pop= []
				while ind_pop != ind_3:
					to_pop.append(ind_pop)
					ind_pop= (ind_pop+1) % len(contour)

				to_pop.sort(reverse=True)
				for x in to_pop:
					print(f'popping {contour[x]} from btwn {pt_1} {pt_3} with angles\n\t1-2 {theta_12}\n\t2-3 {theta_23}\n\t1-3 {theta_13}')
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