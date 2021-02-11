class PropCache:
	def __init__(self, linked=None):
		if linked is None:
			linked= []
		self.linked= linked

	def recache(self):
		for x in self.linked:
			x.recache()
		self.invalidate()

	def invalidate(self):
		pass