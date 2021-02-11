from utils.pyStatParser.stat_parser import Parser
from collections import deque


class Word:
	def __init__(self, text, is_break=False, pre="", post=""):
		self.text= text
		self.is_break= is_break
		self.pre= pre
		self.post= post

	def __str__(self):
		ret= f"{self.pre}{self.text}{self.post}"
		return ret

# todo: break on dash
# todo: dont break on apostrophe
# todo: comment
class WordGroup:
	# http://www.surdeanu.info/mihai/teaching/ista555-fall13/readings/PennTreebankConstituents.html
	break_labels= ["NP", "VP", "PP", "ADJP", "ADVP", "CONJP", "QP",
				   "WHADJP", "WHAVP", "WHAVP", "WHPP", "WHNP", ]
	punct_labels= [".", ","]

	def __init__(self, words):
		self.words= words

	def __str__(self):
		return " ".join(f"{x}" for x in self.words)

	@property
	def breakpoints(self):
		return [i for i in range(len(self.words)) if self.words[i].is_break and i!=(len(self.words)-1)]
	@property
	def num_possibilites(self):
		# each breakpoint is true or false (2 options)
		# each unique possibility is some tuple of true / false
		#
		return 2**(len(self.breakpoints)-1)

	@classmethod
	def from_text(cls, text):
		parser = Parser()
		tree= parser.parse(text)
		return cls.from_parse_tree(tree)

	@classmethod
	def from_parse_tree(cls, tree):
		def walk(node, is_first_child=False, is_last_child=False):
			labels= node.label().split("+")
			has_label= any(y in cls.break_labels for y in labels)

			for x in node:
				# check for phrase boundary
				if x in [node[0], node[-1]]:
					first_flag= False
					last_flag= False

					if x is node[0]:
						first_flag= has_label or is_first_child
					if x is node[-1]:
						last_flag= has_label or is_last_child
				else:
					first_flag= False
					last_flag= False

				# yield if leaf
				# indicate if x and all ancestors are first-childs of a break-label node
				# indicate if x and all ancestors are last-childs of a break-label node
				if len(x) == 1 and isinstance(x[0], str):
					yield dict(text=x.leaves()[0], labels=x.label().split("+"),
							   is_first_child=first_flag, is_last_child=last_flag)
				# else recurse
				else:
					for y in walk(x, is_first_child=first_flag,  is_last_child=last_flag):
						yield y

		lst= []
		first_carry= False
		last_carry= False
		for res in walk(tree):

			# if punctuation, append to previous word if possible
			if len(lst) >= 1 and any(l in cls.punct_labels for l in res['labels']):
				lst[-1].text+= res['text']
				first_carry |= res['is_first_child']
				last_carry |= res['is_last_child']
			# if word is start of phrase, mark the previous word a breakpoint
			# if word is end of phrase, mark as breakpoint
			else:
				if first_carry or res['is_first_child']:
					if lst:
						lst[-1].is_break= True

				lst.append(Word(
					text= res['text'],
					is_break= last_carry or res['is_last_child']
				))
				first_carry= False
				last_carry= False

		return cls(lst)

	def _iter_inds(self, opts): # todo: test
		stack= deque(self.breakpoints)
		yield stack

		def next_opt(current):
			try:
				return next(x for x in opts if x > current)
			except StopIteration:
				return None

		while not (len(stack) == 1 and stack[0] == opts[-1]):
			tmp= next_opt(stack.pop())
			while tmp is None:
				tmp= next_opt(stack.pop())

			while tmp is not None:
				stack.append(tmp)
				tmp= next_opt(tmp)

			yield stack
		yield []

	def get_break_iter(self): # todo: test for dupes
		opts= self.breakpoints
		text= [str(x) for x in self.words]

		for lst in self._iter_inds(opts):
			ret= ""
			for ind,word in enumerate(text):
				if ind in lst:
					ret+= f"{word}\n"
				elif word is not text[-1]:
					ret+= f"{word} "
				else:
					ret+= word
			yield ret