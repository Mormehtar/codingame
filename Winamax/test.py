import Winamax.maps as maps
import Winamax.first as first

test_map = maps.test8

print(test_map)
print()
print('*'*40)
print()
test_map = '\n'.join(test_map.split('\n')[1:-1])
data = first.simulate_data(test_map)
first.solve(*data)
