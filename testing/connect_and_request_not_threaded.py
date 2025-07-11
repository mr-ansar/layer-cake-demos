# connect_and_request_not_threaded.py
import layer_cake as lc
import random
from test_api import Xy, table_type

#
random.seed()

#
DEFAULT_SERVER = lc.HostPort('127.0.0.1', 5050)

class ConnectAndRequest(lc.Point, lc.Stateless):
	def __init__(self, server_address: lc.HostPort=None,
			request_count: int=1, slow_down: float=0.5, big_table: int=100):
		lc.Point.__init__(self)
		lc.Stateless.__init__(self)
		self.server_address = server_address or DEFAULT_SERVER
		self.request_count = request_count
		self.slow_down = slow_down
		self.big_table = big_table

		self.sent = None
		self.client_address = None
	
	def send_request(self):
		'''Connection is active. Initiate request-response sequence.'''
		x = random.randint(1, self.big_table)
		y = random.randint(1, self.big_table)
		xy = Xy(x, y)
		self.send(xy, self.client_address)
		self.sent = xy

	def post_response(self, response):
		'''Response received, validate and determine next move.'''
		y = len(response)
		x = len(response[0])

		sent = self.sent
		if not (x == sent.x and y == sent.y):
			self.complete(lc.Faulted('not the matching table'))

		# Completed sequence of requests.
		self.request_count -= 1
		if self.request_count < 1:
			self.send(lc.Close(), self.client_address)
			return

		# Take a breath.
		s = lc.spread_out(self.slow_down)
		self.start(lc.T1, s)

def ConnectAndRequest_Start(self, message):
	lc.connect(self, self.server_address, http_client='/', layer_cake_json=True)

def ConnectAndRequest_Connected(self, message):
	self.client_address = self.return_address
	self.send_request()

def ConnectAndRequest_NotConnected(self, message):
	self.complete(message)

def ConnectAndRequest_list_list_float(self, message):
	self.post_response(message)

def ConnectAndRequest_Busy(self, message):
	self.request_count -= 1
	if self.request_count < 1:
		self.send(lc.Close(), self.client_address)
		return

	s = lc.spread_out(self.slow_down)
	self.start(lc.T1, s)

def ConnectAndRequest_T1(self, message):
	self.send_request()

def ConnectAndRequest_Closed(self, message):
	self.complete(lc.Ack())

def ConnectAndRequest_Stop(self, message):
	self.complete(lc.Aborted())

def ConnectAndRequest_Faulted(self, message):
	self.complete(message)

#
#
CONNECT_AND_REQUEST_DISPATCH = (
	lc.Start,
	lc.Connected, lc.NotConnected,
	table_type, lc.Busy, lc.T1,
	lc.Closed,
	lc.Stop,
	lc.Faulted,
)

lc.bind(ConnectAndRequest,
	CONNECT_AND_REQUEST_DISPATCH,
	return_type=lc.Any())

if __name__ == '__main__':
	lc.create(ConnectAndRequest)
