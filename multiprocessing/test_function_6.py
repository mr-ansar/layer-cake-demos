# test_function_6.py
import random
import layer_cake as lc
from test_api import table_type

random.seed()

def texture(self, x=8, y=8):
	table = []
	for r in range(y):
		row = [None] * x
		table.append(row)
		for c in range(x):
			row[c] = random.random()

	return table

lc.bind(texture, return_type=table_type, x=int, y=int)

if __name__ == '__main__':
	lc.create(texture)
