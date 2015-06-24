import collections

class peeking_iterator(object):
	def __init__(self, it, end_default=None):
		self.it = iter(it)
		self.end_default = end_default
		self.has_ended = False
		self.next_list = collections.deque()

	def __iter__(self):
		return self

	def __get_next(self):
		if self.has_ended:
			raise StopIteration()
		try:
			return self.it.next()
		except StopIteration:
			self.has_ended = True
			return self.end_default

	def next(self):
		return self.__next__()

	def __next__(self):
		if self.next_list:
			return self.next_list.popleft()
		else:
			return self.__get_next()

	def peek(self):
		if not self.next_list:
			self.next_list.append(self.__get_next())
		return self.next_list[0]

	def has_next(self):
		return not (self.has_ended and (not self.next_list))

	def push_back(self, item):
		self.next_list.appendleft(item)
