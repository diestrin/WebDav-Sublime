class BadConfig(Exception):
	def __init__(self, value):
		self.value = "Bad configuration file: %s" % value

	def __str__(self):
		return str(self.value)

class BadAuthorization(Exception):
	def __init__(self, value):
		self.value = "You ar not allowed to do this action: %s" % value

	def __str__(self):
		return str(self.value)