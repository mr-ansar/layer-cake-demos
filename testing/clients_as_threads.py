# clients_as_threads.py
import layer_cake as lc
import random
from test_api import Xy, table_type
import connect_and_request
import connect_and_request_not_threaded
import connect_and_request_named_thread
import connect_and_request_state_machine

#
DEFAULT_SERVER = lc.HostPort('127.0.0.1', 5050)

#
def clients_as_threads(self, client_type: lc.Type=None,
	thread_count: int=1, server_address: lc.HostPort=None,
	request_count: int=1, slow_down: float=1.0, big_table: int=100):

	client = connect_and_request.ConnectAndRequest
	if isinstance(client_type, lc.UserDefined):
		client = client_type.element
	self.server_address = server_address or DEFAULT_SERVER

	def restart(self, value, args):
		a = self.create(client, server_address=server_address,
			request_count=request_count, slow_down=slow_down,
			big_table=big_table)
		self.on_return(a, check_response)

	def check_response(self, value, args):
		if isinstance(value, lc.Faulted):
			if not isinstance(value, lc.TimedOut):
				return
			self.warning(fault=str(value), tag=lc.portable_to_tag(self.returned_type))

		a = self.create(lc.Delay, seconds=slow_down)
		self.on_return(a, restart)

	# Start with full set and setup replace callback.
	for i in range(thread_count):
		a = self.create(client, server_address=server_address,
			request_count=request_count, slow_down=slow_down,
			big_table=big_table)
		self.on_return(a, check_response)

	# Two ways this can end - control-c and faults.
	# By default it will be because all the clients faulted.
	ending = lc.Faulted('number of clients declined to zero', 'see logs')

	while self.working():
		m = self.input()
		if isinstance(m, lc.Stop):
			self.abort()
			ending = lc.Aborted()
			break
		elif isinstance(m, lc.Returned):
			d = self.debrief()
			if isinstance(d, lc.OnReturned):
				d(self, m)
				continue

			value, port = m.cast_back()
			self.warning(fault=str(value), tag=lc.portable_to_tag(port))


	# Wait for clearing of clients.
	while self.working():
		r = self.input()
		if isinstance(r, lc.Returned):
			d = self.debrief()
			# No callback processing.
			# Just debrief() to clear the OnReturned entry.

	return ending

lc.bind(clients_as_threads)

if __name__ == '__main__':
	lc.create(clients_as_threads)
