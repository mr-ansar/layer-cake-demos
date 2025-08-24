# test_server_resource.py
import layer_cake as lc
from test_resource import Customer

# Network location and processing of request URI.
DEFAULT_ADDRESS = lc.HostPort('127.0.0.1', 5050)
SERVER_RESOURCE = [Customer]
RESOURCE_FORM = lc.ReForm('/{resource}(/{identity})?', resource=r'\w+', identity=r'[0-9]+')

# Define the store. Need a proper place to create the storage,
# so file and memory members need to wait until lc.model_folder()
# is available (see below).
DB = lc.Gas(
	type=lc.def_type(dict[int,Customer]),	# What's in there.
	file=None,									# Storage I/O.
	memory=None,								# In-memory image.
	counter=1
)

# Restful style dispatching.
def retrieve_Customer(self):
	return lc.cast_to(DB.memory, DB.type)

# Special names provide access to elements of the original HTTP
# request, e.g. the reference to "body" accesses the payload
# from the request. The passing of decode_resource to add() means
# that the payload is already decoded to a Customer. Special
# names supported are "http", "header" and "body".
def create_Customer(self, body=None):
	number = DB.counter
	DB.counter += 1

	DB.memory[number] = body
	DB.file.store(DB.memory)
	return lc.HttpResponse(status_code=201, reason_phrase='Created')

# Reference to "header" accesses the dict[str,str] in the original
# HTTP request. The passing of None to add() means that header is
# received below untouched.
def read_Customer(self, identity=None, header=None):
	customer = DB.memory.get(identity, None)
	if customer is None:
		return lc.HttpResponse(status_code=404, reason_phrase='Not Found')
	return customer

def update_Customer(self, body=None, identity=None):
	if identity not in DB.memory:
		return lc.HttpResponse(status_code=404, reason_phrase='Not Found')
	DB.memory[identity] = body
	DB.file.store(DB.memory)
	return lc.HttpResponse(status_code=200)

def delete_Customer(self, identity=None):
	customer = DB.memory.pop(identity, None)
	if customer is None:
		return lc.HttpResponse(status_code=404, reason_phrase='Not Found')
	DB.file.store(DB.memory)
	return lc.HttpResponse(status_code=200)

# Create the mappings from the received request to a resource-based function.
SERVER_DISPATCH = lc.ResourceDispatch(RESOURCE_FORM, SERVER_RESOURCE)

# Arguments are declared as name=conversion where conversion is a function
# that accepts text and returns a required type. Special conversion
# functions include;
# - decode_resource .... convert the JSON body to an instance of the resource.
# - decode_body ........ convert the JSON body to an instance of the specified type.

SERVER_DISPATCH.add(Customer, lc.HttpMethod.GET, retrieve_Customer)
SERVER_DISPATCH.add(Customer, lc.HttpMethod.POST, create_Customer, body=lc.decode_resource)
SERVER_DISPATCH.add(Customer, lc.HttpMethod.GET, read_Customer, identity=int, header=None)
SERVER_DISPATCH.add(Customer, lc.HttpMethod.PUT, update_Customer, body=lc.decode_resource, identity=int)
SERVER_DISPATCH.add(Customer, lc.HttpMethod.DELETE, delete_Customer, identity=int)

#
#
def server(self, server_address: lc.HostPort=None):
	server_address = server_address or DEFAULT_ADDRESS

	# Query the runtime for an appropriate place to
	# store the db.
	model = lc.model_folder()

	# Initialize the storage machinery.
	# Load the saved image, creating an empty instance as needed.
	DB.file = model.file('customers', DB.type, create_default=True)
	DB.memory = DB.file.recover()

	# A cheap, reliable alternative to storing the next serial id.
	DB.counter = 1 if len(DB.memory) < 1 else max(DB.memory.keys()) + 1

	lc.listen(self, server_address, uri_form=RESOURCE_FORM)
	m = self.input()
	if not isinstance(m, lc.Listening):
		return m

	while True:
		m = self.input()
		if isinstance(m, lc.FormRequest):
			pass
		elif isinstance(m, lc.Faulted):
			return m
		elif isinstance(m, lc.Stop):
			return lc.Aborted()
		else:
			continue

		SERVER_DISPATCH(self, m)

lc.bind(server)

if __name__ == '__main__':
	lc.create(server)
