# test_server_10.py
from enum import Enum
from uuid import UUID
import layer_cake as lc
from test_api import Xy, Customer, table_type
from test_worker_10 import worker

DEFAULT_ADDRESS = lc.HostPort('127.0.0.1', 5050)
SERVER_API = [Xy, Customer]

#
#
def server(self, server_address: lc.HostPort=None):
	server_address = server_address or DEFAULT_ADDRESS

	lc.listen(self, server_address, http_server=SERVER_API)
	m = self.input()
	if not isinstance(m, lc.Listening):
		return m

	lc.subscribe(self, r'test-multihosting:worker-10:[-a-f0-9]+', scope=lc.ScopeOfDirectory.LAN)
	m = self.input()
	if not isinstance(m, lc.Subscribed):
		return m

	worker_spool = self.create(lc.ObjectSpool, None)

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
		elif isinstance(m, lc.Faulted):
			return m
		elif isinstance(m, lc.Stop):
			return lc.Aborted()
		else:
			continue

		def respond(self, response, args):
			self.send(lc.cast_to(response, self.returned_type), args.return_address)

		a = self.create(lc.GetResponse, m, worker_spool)
		self.on_return(a, respond, return_address=self.return_address)

lc.bind(server, return_type=lc.Any())

if __name__ == '__main__':
	lc.create(server)
