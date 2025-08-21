# test_resource.py
import layer_cake as lc

class Customer(object):
	def __init__(self, name: str=None, age: int=None):
		self.name = name
		self.age = age

lc.bind(Customer)
