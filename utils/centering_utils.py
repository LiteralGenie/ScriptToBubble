def get_2d_iter(cx, cy, radius=50, stride=5, max_x=None, max_y=None):
	x_bounds= [
		int(max(0, cx-radius)),
		int(min(cx+radius, max_x if max_x else cx+radius))
	]
	x_range= range(*x_bounds, stride)

	y_bounds= [
		int(max(0, cy-radius)),
		int(min(cy+radius, max_y if max_y else cy+radius))
	]
	y_range= range(*y_bounds, stride)

	for x in x_range:
		for y in y_range:
			yield x,y