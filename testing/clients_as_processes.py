# clients_as_processes.py
import layer_cake as lc
import random
from test_api import Xy, table_type
from clients_as_threads import clients_as_threads

#
DEFAULT_SERVER = lc.HostPort('127.0.0.1', 5050)

#
#
def clients_as_processes(self, process_count: int=1, thread_count: int=1,
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

	# Two ways this can end - control-c and faults.
	ending = lc.Faulted('too many client faults', 'see logs')

	while self.working():
		m = self.input()
		if isinstance(m, lc.Stop):
			self.abort()
			ending = lc.Aborted()
		elif isinstance(m, lc.Returned):
			d = self.debrief()

	return ending

lc.bind(clients_as_processes)

if __name__ == '__main__':
	lc.create(clients_as_processes)
