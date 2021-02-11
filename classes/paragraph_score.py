import statistics
from functools import cached_property


class LineScore:
	HORIZONTAL= 0
	VERTICAL= 1

	def __init__(self,  left=None, right=None, line=None, typ=None):
		self.left= left
		self.right= right
		self.line= line

		if typ is None:
			self.typ= self.HORIZONTAL

	@cached_property
	def score(self):
		if self.left==0 or self.right==0:
			return None
		else:
			# return statistics.stdev([self.left, self.right])
			return [self.left, self.right]
			# return abs(l - r) / (l + r)

	def valid(self):
		return self.score is not None

	def __str__(self):
		return f"{self.left} | {self.right} | {self.score} | {self.line.text}"

	@classmethod
	def get_vert_score(cls, coord, check_up, line, mask):
		left_col= int(line.bbox.x)
		right_col= int(line.bbox.x + line.bbox.width - 1)

		kwargs= dict()
		if check_up:
			kwargs['end']= coord
			max_score= mask.shape[0]-1 - coord
		else:
			kwargs['start']= coord
			max_score= max(coord, 0)

		if 0 <= left_col <= mask.shape[1]-1:
			walls= mask.get_v_walls(left_col)
			dists= Wall.get_dists(index=coord, walls=walls, **kwargs)
			if dists:
				dists= min(dists, key=lambda x: x['dist'])
				l_score= dists['dist']
			else:
				l_score= max_score
		else:
			l_score= 0

		if 0 <= right_col <= mask.shape[1]-1:
			walls= mask.get_v_walls(right_col)
			dists= Wall.get_dists(index=coord, walls=walls, **kwargs)
			if dists:
				dists= min(dists, key=lambda x: x['dist'])
				r_score= dists['dist']
			else:
				r_score= max_score
		else:
			r_score= 0

		assert l_score >= 0
		assert r_score >= 0
		return cls(left=l_score, right=r_score, line=line, typ=cls.VERTICAL)

	@classmethod
	def get_horiz_score(cls, left_coord, right_coord, line, mask):
		row= int(line.bbox.center_y)
		if not 0 <= row <= mask.shape[0]-1:
			return cls(left=0, right=0, line=line, typ=cls.HORIZONTAL)
		walls= mask.get_h_walls(row)

		dists= Wall.get_dists(left_coord, walls, end=left_coord)
		if dists:
			dists= min(dists, key=lambda x: x['dist'])
			l_score= dists['dist']
		else:
			l_score= max(left_coord, 0)

		dists= Wall.get_dists(right_coord, walls, start=right_coord)
		if dists:
			dists= min(dists, key=lambda x: x['dist'])
			r_score= dists['dist']
		else:
			r_score= min(mask.shape[1]-1 - right_coord,
						 mask.shape[1]-1)

		l_score= max(l_score, 0)
		r_score= max(r_score, 0)
		return cls(left=l_score, right=r_score, line=line, typ=cls.HORIZONTAL)

class ParagraphScore:
	def __init__(self, para):
		self.h_scores= []
		self.v_scores= []
		self.para= para

	@cached_property
	def score(self):
		a= [x.score for x in self.h_scores] + [x.score for x in self.v_scores]
		a= [x for x in a if x is not None]

		b= []
		for x in a:
			b+= x

		# if len(b) > 3: #@
		if not b:
			return None
		return statistics.stdev(b) / statistics.mean(b)
		# else:
		# 	# @
		# 	return 999

	def valid(self):
		return all(x.valid() for x in self.v_scores + self.h_scores)

	def __str__(self):
		return f"{self.score:.3f}"

	# def score(self):
	# 	a= [x.score() for x in self.h_scores] + [x.score() for x in self.v_scores]
	# 	a= [x for x in a if x is not None]
	#
	# 	b= []
	# 	for x in a:
	# 		b+= x
	#
	# 	b.sort()
	# 	if len(b) % 2 == 1:
	# 		med= b[len(b) // 2]
	# 	else:
	# 		med= len(b) // 2
	# 		med= (b[med] + b[med-1]) / 2
	#
	# 	if len(b) > 3:
	# 		return statistics.median(abs(x-med) for x in b)

	@staticmethod
	def from_paragraph(para, mask):
		ret= ParagraphScore(para=para)

		# horiz scores
		for l in para.lines:
			left_coord= l.bbox.x
			right_coord= l.bbox.x + l.bbox.width - 1

			# try:
			score= LineScore.get_horiz_score(left_coord, right_coord, l, mask)
			if score:
				ret.h_scores.append(score)
			# except IndexError:
			#
			# 	ret.h_scores.append(LineScore(left=0, right=0, line=l, typ=LineScore.HORIZONTAL))

		# vert scores
		mid= round(len(para.lines)/2)
		for i,l in enumerate(para.lines):
			# upper half
			if i+1 <= mid:
				# top-most or longer than all above
				if l == para.lines[0] or all(l.bbox.width > x.bbox.width for x in para.lines[i+1:]):
					top= l.bbox.y - l.bbox.height + 1
					score= LineScore.get_vert_score(top, True, l, mask)
					if score:
						ret.v_scores.append(score)

			# lower half
			if i+1 >= mid:
				# bot-most of longer than all below
				if l == para.lines[-1] or all(l.bbox.width > x.bbox.width for x in para.lines[:i]):
					bot= l.bbox.y
					score= LineScore.get_vert_score(bot, False, l, mask)
					if score:
						ret.v_scores.append(score)

		return ret

class Wall:
	def __init__(self, start, end=None):
		self.start= start

		if end is None:
			end= start
		self.end= end

	def __contains__(self, val):
		return self.start <= val <= self.end

	@staticmethod
	def get_dists(index, walls, start=None, end=None):
		ret= []
		walls= [x for x in walls if ((not start or x.end >= start) and (not end or x.start <= end))]
		for w in walls:
			if index in w:
				dist= 0
			else:
				dist= min( abs(index-w.start), abs(index-w.end) )

			ret.append(dict(
				wall=w,
				dist=dist
			))

		return ret

	@classmethod
	def get_walls(cls, lst):
		ret= []; ind= 0
		while res := cls._get_wall(lst, start_index=ind):
			ind= res['next_index']
			ret.append(res['wall'])
		return ret

	# find intervals of black
	@classmethod
	def _get_wall(cls, lst, start_index=0):
		ind= start_index

		# get start index
		while ind < len(lst):
			if lst[ind] == 0:
				start= ind
				ind+= 1
				break
			else:
				ind+= 1
		else:
			return None # all pixels from [start_index] are white

		# get end index
		while ind < len(lst):
			if lst[ind] != 0:
				end= ind
				ind+= 1
				break
			else:
				ind+= 1
		else:
			end= len(lst)-1 # all pixels from [start] are black

		# return
		return dict(
			wall=Wall(start=start, end=end),
			next_index= ind
		)