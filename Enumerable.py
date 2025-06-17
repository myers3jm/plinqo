import collections
from collections import UserList
from collections.abc import Iterable
import typing
from typing import TypeVar, Callable
import doctest

Enumerable = TypeVar('Enumerable', bound='Enumerable')
T = TypeVar('T', bound='T')

# Base collection class for plinqo
class Enumerable(UserList):
	def __init__(self):
		super().__init__()

	def __init__(self, data):
		super().__init__(data)
	
	# Filtering data
	def OfType(self, t: type) -> Enumerable:
	    """Return an Enumerable containing only the elements of the input Enumerable which are of the input type

	    Declare the Enumerable e
	    >>> e = Enumerable(['a', 'b', 'c', 'd', 0, 2, 4, 5, 0xff, 0x00, 0x5d, ['1', '2', '3'], {'a': '0', 'b': '1'}, {'a', 'b', 'c', 0, 1, 2}, Enumerable([1, 2, 3])])
		
	    String
	    >>> e.OfType(str)
	    ['a', 'b', 'c', 'd']
		
	    Integer
	    >>> e.OfType(int)
	    [0, 2, 4, 5, 255, 0, 93]
		
	    List
	    >>> e.OfType(list)
	    [['1', '2', '3']]
		
	    Dictionary
	    >>> e.OfType(dict)
	    [{'a': '0', 'b': '1'}]

	    Set
	    >>> e.OfType(set) == [{'a', 'b', 'c', 0, 1, 2}]
	    True

	    Custom
	    >>> e.OfType(Enumerable)
	    [[1, 2, 3]]
	    """
	    return Enumerable([x for x in self.data if type(x) == t])
	
	def Where(self, f: Callable[..., bool]) -> Enumerable:
	    """Return an Enumerable containing only the elements of the input Enumerable for which the input function returns True

	    Declare the Enumerable e
	    >>> e = Enumerable(['a', 'b', 'c', 'd', 0, 2, 4, 5, 0xff, 0x00, 0x5d, ['1', '2', '3'], {'a': '0', 'b': '1'}, {'a', 'b', 'c', 0, 1, 2}, Enumerable([1, 2, 3])])

	    Lambda is even
	    >>> e.Where(lambda a : a % 2 == 0)
	    [0, 2, 4, 0]

	    Named function
	    >>> def isOdd(x):
	    ...     return x % 2 != 0
	    >>> e.Where(isOdd)
	    [5, 255, 93]

	    Lambda len > 2
	        There is a set present in the output, so we cannot hardcode the expected result in the doctest. This verifies the len > 2 requirement is met
	    >>> all([len(x) > 2 for x in e.Where(lambda a : len(a) > 2)])
	    True
	    """

	    def attempt(x) -> bool:
	        try:
	            return f(x)
	        except:
	            pass
	    return Enumerable([x for x in self.data if attempt(x)])

	# Projection operations
	def Select(self, f: Callable[..., type]) -> Enumerable:
		"""Return an Enumerable containing the result of applying the input function to each of the input Enumerable's elements

		Declare the Enumerable e
		>>> e = Enumerable(['a', 'b', 'c', 'd', 0, 2, 4, 5, 0xff, 0x00, 0x5d, ['1', '2', '3'], {'a': '0', 'b': '1'}, {'a', 'b', 'c', 0, 1, 2}, Enumerable([1, 2, 3])])

		String operation
		>>> e.Select(lambda a : a.upper())
		['A', 'B', 'C', 'D', None, None, None, None, None, None, None, None, None, None, None]

		Arithmetic
		>>> e.Select(lambda a : a * 2)
		['aa', 'bb', 'cc', 'dd', 0, 4, 8, 10, 510, 0, 186, ['1', '2', '3', '1', '2', '3'], None, None, [1, 2, 3, 1, 2, 3]]
		"""
		def attempt(x):
			try:
				return f(x)
			except:
				pass
		return Enumerable([attempt(x) for x in self.data])
	
	def SelectMany(self, f: Callable[..., type]) -> Enumerable:
		"""Return an Enumerable containing the result of applying the input function to each of the input Enumerable's Enumerable elements and then flattens the result into one Enumerable

		Declare the Enumerable e
		>>> e = Enumerable(['a', 'b', 'c', 'd', 0, 2, 4, 5, 0xff, 0x00, 0x5d, ['1', '2', '3'], {'a': '0', 'b': '1'}, {'a', 'b', 'c', 0, 1, 2}, Enumerable([1, 2, 3])])

		String operation WIP
		>>> e.SelectMany(lambda a : a.upper()) # doctest: +ELLIPSIS
		['A', 'B', 'C', 'D', None, None, None, None, None, None, None, '1', '2', '3', None, None, ..., None, None, None]

		Arithmetic
		>>> e.SelectMany(lambda a : a * 2) # doctest: +ELLIPSIS
		['aa', 'bb', 'cc', 'dd', 0, 4, 8, 10, 510, 0, 186, '11', '22', '33', ('a', '0', 'a', '0'), ('b', '1', 'b', '1'), ..., 2, 4, 6]
		"""

		def flatten(items):
			for item in items:
				if isinstance(item, dict):
					for k, v in item.items():
						yield (k, v)
				elif isinstance(item, Iterable) and not isinstance(item, (str, bytes)):
					yield from flatten(item)
				else:
					yield item

		def attempt(x):
			try:
				return f(x)
			except:
				pass

		return Enumerable([attempt(x) for x in flatten(self.data)])
	
	def Zip(self, *arrays: Iterable[T]) -> Enumerable:
		"""Return an Enumerable containing a sequence of tuples with elements from both the calling Enumerable and the input iterables

		It is worth noting that the type hint makes use of a generic type 'T'. While this may seem to suggest the passed iterables should be homogeneous,
			Python does allow heterogeneous collections, so this function does support heterogeneity.

		Declare the Enumerable e
		>>> e = Enumerable([0, 1, 2, 3, 4, 5])

		List
		>>> e.Zip([9, 8, 7])
		[(0, 9), (1, 8), (2, 7)]

		Dict
		>>> e.Zip({'a': 0, 'b': 1, 'c': 2})
		[(0, 'a'), (1, 'b'), (2, 'c')]

		Set
		>>> e.Zip({'a', 'b', 'c'}) # doctest: +ELLIPSIS
		[(0, ...), (1, ...), (2, ...)]

		Enumerable
		>>> e.Zip(Enumerable([9, 8, 7]))
		[(0, 9), (1, 8), (2, 7)]

		Multiple iterables
		>>> e.Zip([9, 8, 7], [6, 5, 4])
		[(0, 9, 6), (1, 8, 5), (2, 7, 4)]
		>>> e.Zip([9, 8, 7], [6, 5, 4], [3, 2, 1])
		[(0, 9, 6, 3), (1, 8, 5, 2), (2, 7, 4, 1)]
		>>> e.Zip([9, 8, 7], [6, 5], [3, 2, 1])
		[(0, 9, 6, 3), (1, 8, 5, 2)]
		"""
		return Enumerable(zip(self.data, *arrays))

if __name__ == '__main__':
	doctest.testmod()