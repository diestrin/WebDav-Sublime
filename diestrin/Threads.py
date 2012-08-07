from webdav.WebdavClient import CollectionStorer
import threading

class WebdavGetCollection(threading.Thread):
	def __init__(self, url, auth={}):

		self.url = url
		self.auth = auth if auth else None
		self.result = None

		threading.Thread.__init__(self)

	def run(self):
		self.collection = CollectionStorer(self.url,validateResourceNames = False)
		if self.auth:
			self.collection.connection.addBasicAuthorization(self.auth["user"], self.auth["password"])
			
		self.collection.connection.cookie = self.collection.getSpecificOption("set-cookie")
		self.result = self.collection.getCollectionContents()
		self.cookie = self.collection.getSpecificOption("set-cookie")

class WebdavDownloadFile(threading.Thread):
	def __init__(self, resource, local_path):
		self.resource = resource
		self.local_path = local_path

		threading.Thread.__init__(self)
		
	def run(self):
		try:
			self.resource.downloadFile(self.local_path)
			self.result = "Succes"
		except:
			self.result = "Error"

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