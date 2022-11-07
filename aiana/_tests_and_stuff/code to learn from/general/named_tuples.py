
# #
from collections import namedtuple

test_tuple = namedtuple('foo', ('a', 'b', 'c'))
result = test_tuple(1, 2, 3)
# #
string=""
for item in result:
    string += f'{item}\t'
string
# #
a,b = result
