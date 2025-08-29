# clients_as_processes.py
import layer_cake as lc
import random
from test_api import Xy, table_type
from clients_as_threads import clients_as_threads

#
DEFAULT_SERVER = lc.HostPort('127.0.0.1', 5050)

#
#
def clients_as_processes(self, process_count: int=1, thread_count: int=1, test_span: lc.TimeSpan=None,
	client_type: lc.Type=None, server_address: lc.HostPort=None,
	request_count: int=1, slow_down: float=1.0, big_table: int=100):
	server_address = server_address or DEFAULT_SERVER

	# Start the processes.
	for i in range(process_count):
		a = self.create(lc.ProcessObject, clients_as_threads,
			thread_count=thread_count,
			client_type=client_type, server_address=server_address,
			request_count=request_count, slow_down=slow_down,
			big_table=big_table)
		self.assign(a, i)

	if test_span is not None:
		self.start(lc.T1, test_span)

	unexpected = 0
	while self.working():
		m = self.input()
		if isinstance(m, lc.Stop):
			self.abort()
		elif isinstance(m, lc.T1):
			self.abort()
		elif isinstance(m, lc.Returned):
			d = self.debrief()
			value, port = m.cast_back()

			# Termination due to abort().
			if isinstance(value, lc.Aborted):
				continue

			# Something less desirable.
			if isinstance(value, lc.Faulted):
				self.warning('Faulted', fault=str(value))
			else:
				self.warning('Unexpected', tag=lc.portable_to_tag(port))
			unexpected += 1

	return lc.cast_to(unexpected, lc.int_type)

lc.bind(clients_as_processes)

if __name__ == '__main__':
	lc.create(clients_as_processes)
