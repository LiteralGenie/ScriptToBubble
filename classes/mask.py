import bisect, cv2, math, numpy as np
from .paragraph_score import Wall, ParagraphScore


class Mask:
	"""
	Caches scores + horiz walls + vert walls for a given pixel mask
	"""

	class ScoreList:
		"""
		Sorted score list
		"""
		def __init__(self, mask):
			self.scores= [] # score (number)
			self.indexes= [] # coordinate (x,y)
			self.mask= mask

		def __getitem__(self, item):
			it= self.indexes[item]
			if isinstance(it, list):
				return [self.mask.scores[x] for x in it]
			else:
				return self.mask.scores[it]

		def __len__(self):
			return len(self.indexes)

		def insert(self, x):
			ind= bisect.bisect_right(self.scores, x.score)
			self.scores.insert(ind, x.score)
			self.indexes.insert(ind, x.para.center)

	def __init__(self, pixel_mask, para):
		self.h_walls= {}
		self.v_walls= {}
		self.pixel_mask= pixel_mask
		self.para= para

		self.scores= dict()
		self.limits= dict(
			l={}, r={}, t={}, b={}
		)
		self.sorted_scores= self.ScoreList(self)

	@classmethod
	def from_image(cls, im_path, para):
		im= cv2.imread(im_path)
		im= cv2.cvtColor(im, cv2.COLOR_BGR2GRAY)

		h,w= im.shape
		mask= np.zeros((h+2, w+2), dtype=np.uint8)

		c= para.bbox.center
		c= (int(c[0]), int(c[1]))
		cv2.floodFill(
			im, mask, c, 125, loDiff=5, upDiff=5,
			# flags=cv2.FLOODFILL_MASK_ONLY
		)

		return cls(pixel_mask=mask[1:h+1, 1:w+1], para=para)

	def __getitem__(self, item):
		return self.pixel_mask.__getitem__(item)

	@property
	def shape(self):
		return self.pixel_mask.shape

	def get_h_walls(self, row):
		if int(row) in self.h_walls:
			return self.h_walls[row]
		else:
			tmp= list(self.pixel_mask[row, :])
			ret= Wall.get_walls(tmp)
			self.h_walls[row]= ret
			return ret

	def get_v_walls(self, col):
		if int(col) in self.v_walls:
			return self.v_walls[col]
		else:
			tmp= list(self.pixel_mask[:, col])
			ret= Wall.get_walls(tmp)
			self.v_walls[col]= ret
			return ret

	def get_score(self, x, y):
		# if cached, return
		if (x,y) in self.scores:
			return self.scores[(x,y)]

		# check if coordinate is out of bounds
		p= self.para.copy()
		p.bbox.center= (x,y)

		def chk_gt(val, key, coord):
			tmp= self.limits[key].get(coord, None)
			return (tmp is None) or (tmp < val)
		def chk_lt(val, key, coord):
			tmp= self.limits[key].get(coord, None)
			return (tmp is None) or (tmp > val)

		# @todo: doesnt work if start is offcenter
		# for l in p.lines:
		# 	cx,cy= l.bbox.center
		#
		# 	# check horizontal limits -- center_x is between known limits
		# 	if not (chk_gt(cx, 'l', cy) and chk_lt(cx, 'r', cy)):
		# 		return None
		# 	# check vertical limits -- center_y is between known limits
		# 	if not (chk_gt(cx, 'b', cy) and chk_lt(cx, 't', cy)):
		# 		return None

		# get score
		ps= ParagraphScore.from_paragraph(p, self)

		# @todo: doesnt work if start is offcenter
		# check out of bounds
		flag= False
		for score in ps.h_scores:
			bbox= score.line.bbox
			cy= bbox.center_y
			if score.left == 0:
				x= bbox.x
				if x > self.limits['l'].get(cy, -1):
					self.limits['l'][cy]= x
				flag= True
			if score.right == 0:
				x= bbox.x + bbox.width - 1
				if x < self.limits['r'].get(cy, x+1):
					self.limits['r'][cy]= x
				flag= True

		for score in ps.v_scores:
			bbox= score.line.bbox
			cx= bbox.center_x
			if score.left == 0:
				y= bbox.y - bbox.height + 1
				if y < self.limits['t'].get(cx, -1):
					self.limits['t'][cx]= y
				flag= True
			if score.right == 0:
				y= bbox.y
				if y > self.limits['b'].get(cx, y+1):
					self.limits['b'][cx]= y
				flag= True

		if not flag:
			self.scores[(x,y)]= ps
			self.sorted_scores.insert(ps)
			return ps
		else:
			return None

	def get_heatmap(self, im_path):
		heatmap= cv2.imread(im_path)

		# non-linear, more rapid color shifts at vals closer to min
		# clips to 1 for inputs close to 1
		def remap(x):
			ret= math.sqrt(x) + x/5
			return min(ret, 1)

		s= self.sorted_scores
		min_s= s[0].score
		max_s= s[-1].score

		# colors= [(1,0,0), (0,1,0), (0,1,1), (0,0,1)]
		colors= [
			(0,0,0), (1,0,0), (1,1,0), (0,1,0), (0,1,1), (0,0,1), (1,1,1)
		]
		n= len(colors)-1

		for x in s:
			mult= (x.score - min_s) / (max_s - min_s)
			mult= remap(mult)

			color_start= colors[int(n*mult)]
			color_end= min(int(n*mult)+1, n)
			color_end= colors[color_end]

			c= []
			for i in range(3):
				tmp= color_start[i] + mult*(color_end[i] - color_start[i])
				tmp*= 255
				c.append(tmp)

			cntr= x.para.center
			try:
				heatmap[int(cntr[1]), int(cntr[0]), :]= c
			except IndexError:
				pass

		return heatmap

	# get [n] best scores whose x & y coordinates are at least [thresh+1] pixels apart
	def filter_candidates(self, n, thresh):
		ret= []

		# filter candidates
		def chk(pos_a, pos_b):
			if not isinstance(pos_a, tuple):
				pos_a= pos_a.para.bbox.pos
			if not isinstance(pos_b, tuple):
				pos_b= pos_b.para.bbox.pos

			diff_x= abs(pos_a[0] - pos_b[0])
			diff_y= abs(pos_a[1] - pos_b[1])

			return (diff_x <= thresh) and (diff_y <= thresh)

		exclude= set()
		ind= 0
		while len(ret) < n and ind < len(self.sorted_scores):
			s= self.sorted_scores[ind]
			pos= s.para.bbox.pos

			if pos in exclude:
				ind+= 1
				continue
			ret.append(s)

			for x in self.sorted_scores[ind+1:]:
				tmp= x.para.bbox.pos
				if chk(pos, tmp):
					exclude.add(tmp)

			ind+=1

		return ret