from peeking_iterator import peeking_iterator

def test_empty():
	pi = peeking_iterator([])
	assert pi.has_next()
	assert(pi.next() is None)
	assert not pi.has_next()

	pi = peeking_iterator([], end_default=42)
	assert(pi.next() == 42)
	assert not pi.has_next()

def test_non_empty():
	pi = peeking_iterator([1, 2])
	assert pi.has_next()
	next = pi.peek()
	assert next == 1
	next = pi.next()
	assert next == 1
	next = pi.peek()
	assert next == 2
	next = pi.next()
	assert next == 2
	next = pi.next()
	assert next is None
	assert not pi.has_next()

def test_push_back():
	pi = peeking_iterator([1, 2, 3])
	pi.push_back(42)
	assert pi.peek() == 42
	assert pi.next() == 42
	assert pi.next() == 1
	assert pi.next() == 2

def test_iterate():
	lst = [x for x in peeking_iterator([1, 2, 3])]
	assert lst == [1, 2, 3, None]
