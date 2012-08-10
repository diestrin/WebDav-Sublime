from webdav.WebdavClient import CollectionStorer, AuthorizationError, parseDigestAuthInfo
import threading
import sublime

class WebdavGetCollection(threading.Thread):
	def __init__(self, url=None, auth={}, collection=None):

		self.url = url
		self.auth = auth if auth else None
		self.result = None
		self.collection = collection
		self.error = None

		threading.Thread.__init__(self)

	def run(self):
		try:
			if self.url:
				self.collection = CollectionStorer(self.url, validateResourceNames = False)

			authFailures = 0
			while authFailures < 2:
				try:
					self.result = self.collection.getCollectionContents()
					if self.collection.getSpecificOption("set-cookie"):
						self.collection.connection.cookie = self.collection.getSpecificOption("set-cookie")
						self.cookie = self.collection.getSpecificOption("set-cookie")
					break
				except AuthorizationError, e:
					if e.authType == "Basic":
						self.collection.connection.addBasicAuthorization(self.auth["user"], self.auth["password"])
					elif e.authType == "Digest":
						info = parseDigestAuthInfo(e.authInfo)
						self.collection.connection.addDigestAuthorization(self.auth["user"], self.auth["password"], realm=info["realm"], qop=info["qop"], nonce=info["nonce"])						
					else:
						self.error = "Error: " + str(e)
						
					authFailures += 1

		except Exception, e:
			self.error = "Error: " + str(e)

class WebdavDownloadFile(threading.Thread):
	def __init__(self, resource, local_path):
		self.resource = resource
		self.local_path = local_path

		threading.Thread.__init__(self)
		
	def run(self):
		try:
			self.resource.downloadFile(self.local_path)
			self.result = "Succes"
		except Exception, e:
			self.result = "Error: " + str(e)

class WebdavUploadFile(threading.Thread):
	def __init__(self, resource, local_path):
		self.resource = resource
		self.local_path = local_path

		threading.Thread.__init__(self)
		
	def run(self):
		try:
			local_file = open(self.local_path, "r")
			self.resource.uploadFile(local_file)
			self.result = "Succes"
		except:
			self.result = "Error"

class Handle(object):
	def __init__(self, thread, success):
		self.thread = thread
		self.success = success

		self.__handle()

	def __handle(self):
		if not self.thread.is_alive():
			self.success(self.thread)
			return

		sublime.set_timeout(self.__handle, 100)