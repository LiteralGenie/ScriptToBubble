import time


class Timestamp:
	def __init__(self):
		self.start= time.time()

	def __call__(self):
		return self.time()

	def time(self, brackets=False):
		ret= f"{time.time()-self.start:.1f}s"
		if brackets:
			ret= f"[{ret}]"
		return ret

	def log(self, msg, escape=True):
		if escape:
			msg= msg.replace("\n", "\\n")
		print(f"\r{self.time(True)} {msg}", end="")