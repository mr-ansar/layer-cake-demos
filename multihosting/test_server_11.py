# test_server_11.py
import layer_cake as lc
from test_api import Xy

DEFAULT_ADDRESS = lc.HostPort('127.0.0.1', 5050)
SERVER_API = [Xy,]

def server(self, server_address: lc.HostPort=None, size_of_queue: int=None, responsiveness: float=None, busy_pass_rate: int=10):
	server_address = server_address or DEFAULT_ADDRESS

	lc.listen(self, server_address, http_server=SERVER_API)
	m = self.input()
	if not isinstance(m, lc.Listening):
		return m

	lc.subscribe(self, r'test-multihosting:worker-11:[-a-f0-9]+', scope=lc.ScopeOfDirectory.LAN)
	m = self.input()
	if not isinstance(m, lc.Subscribed):
		return m
	subscribed = m

	worker_spool = self.create(lc.ObjectSpool, None, size_of_queue=size_of_queue, responsiveness=responsiveness, busy_pass_rate=busy_pass_rate)

	while True:
		m = self.input()
		if isinstance(m, Xy):
			pass
		elif isinstance(m, lc.Returned):
			d = self.debrief()
			if isinstance(d, lc.OnReturned):
				d(self, m)
			continue
		elif isinstance(m, lc.Available):
			self.send(lc.JoinSpool(m.publisher_address), worker_spool)
			continue
		elif isinstance(m, lc.Dropped):
			self.send(lc.LeaveSpool(m.remote_address), worker_spool)
			continue
		elif isinstance(m, lc.NotListening):
			break
		elif isinstance(m, lc.Faulted):
			return m
		elif isinstance(m, lc.Stop):
			return lc.Aborted()
		else:
			continue

		# Callback for on_return.
		def respond(self, response, args):
			self.send(lc.cast_to(response, self.returned_type), args.return_address)

		a = self.create(lc.GetResponse, m, worker_spool)
		self.on_return(a, respond, return_address=self.return_address)

	# Dont clobber m
	self.send(lc.Stop(), worker_spool)
	self.select(lc.Returned)

	lc.clear_subscribed(self, subscribed)
	self.select(lc.SubscribedCleared)

	return m	# NotListening

lc.bind(server)

if __name__ == '__main__':
	lc.create(server)
