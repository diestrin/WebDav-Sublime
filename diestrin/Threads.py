from webdav.WebdavClient import CollectionStorer
import threading

class WebdavGetCollection(threading.Thread):
	def __init__(self, url, auth={}):

		self.url = url
		self.auth = auth if auth else None
		self.result = None

		threading.Thread.__init__(self)

	def run(self):
		print "-- Obteniendo el folder %s --" % self.url
		self.collection = CollectionStorer(self.url,validateResourceNames = False)
		if self.auth:
			self.collection.connection.addBasicAuthorization(self.auth["user"], self.auth["password"])
		self.collection.connection.cookie = self.collection.getSpecificOption("set-cookie")
		self.result = self.collection.getCollectionContents()
		self.cookie = self.collection.getSpecificOption("set-cookie")