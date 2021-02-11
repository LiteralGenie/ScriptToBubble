from .prop_cache import PropCache


class Bbox(PropCache):
	def __init__(self, x,y, w,h, linked_bbox=None, **kwargs):
		self._pos= (x,y) # BOTTOM-LEFT corner
		self.size= (w,h)

		if linked_bbox is None:
			linked_bbox= []
		self.linked_bbox= linked_bbox

		super().__init__(**kwargs)

	def __str__(self):
		return f"pos={self.pos} | size={self.size} | center={self.center}"

	@property
	def pos(self):
		return self._pos
	@pos.setter
	def pos(self, new_pos):
		ret= list(self.pos)
		new_linked= [list(x.pos) for x in self.linked_bbox]

		assert len(self._pos) == len(new_pos)

		for i in range(len(self._pos)):
			if new_pos[i] is not None:
				shift= new_pos[i] - ret[i]

				ret[i]+= shift
				for x in new_linked:
					x[i]+= shift

		self._pos= tuple(ret)
		for x,y in zip(self.linked_bbox, new_linked):
			x.pos= tuple(y)

		self.recache()

	@property
	def center(self):
		x= self.x + self.width/2
		y= self.y - self.height/2
		return (x,y)
	@center.setter
	def center(self, new_center):
		old_center= self.center
		new_linked= [list(x.center) for x in self.linked_bbox]
		assert len(old_center) == len(new_center) == len(self.pos)

		# old_pos + shift
		ret= list(self.pos)
		for i in range(len(self.pos)):
			if new_center[i] is not None:
				shift= new_center[i] - old_center[i]

				ret[i]+= shift
				for x in new_linked:
					x[i]+= shift

		self.pos= tuple(ret)
		for x,y in zip(self.linked_bbox, new_linked):
			x.center= tuple(y)

		self.recache()

	@property
	def x(self):
		return self.pos[0]
	@property
	def y(self):
		return self.pos[1]
	@property
	def width(self):
		return self.size[0]
	@property
	def height(self):
		return self.size[1]
	@property
	def center_x(self):
		return self.center[0]
	@property
	def center_y(self):
		return self.center[1]