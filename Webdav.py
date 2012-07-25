import sublime, sublime_plugin
from webdav.WebdavClient import CollectionStorer,AuthorizationError

class WebdavCommand(sublime_plugin.WindowCommand):

	def callB(self, index):
		if index > 1:
			if self.items[index][1].getResourceType() == "collection":
				self.currentPath = self.items[index][0].path
				self.webdavConnection = self.getFolder(self.currentPath)
				self.lista = []
				self.items = []
				self.addBasicOptions()

				for resource, properties in self.webdavConnection.getCollectionContents():
					self.lista.append(properties.getDisplayName())
					self.items.append((resource,properties))

				self.window.show_quick_panel(self.lista,self.callB)
		elif index == 0:
			#if self.currentPath != self.root:
			self.lista = []
			self.items = []
			self.addBasicOptions()

			for resource, properties in self.webdavConnection.getCollectionContents():
				self.lista.append(properties.getDisplayName())
				self.items.append((resource,properties))

			self.window.show_quick_panel(self.lista,self.callB)
		elif index == 1:
			self.lista = []
			self.items = []
			self.addBasicOptions(False)

			self.window.show_quick_panel(self.lista,self.callB)


	def run(self):
		self.path = "https://example.com"
		self.root = "/home/"
		self.currentPath = self.root
		self.user = "user"
		self.pasw = "password"
		self.lista = []
		self.items = []
		self.webdavConnection = self.getFolder(self.root)

		try:
			self.addBasicOptions()
			for resource, properties in self.webdavConnection.getCollectionContents():
				self.lista.append(properties.getDisplayName())
				self.items.append((resource,properties))

			self.window.show_quick_panel(self.lista,self.callB)
		except AuthorizationError, e:
			raise e

	def getFolder(self,path):
		connection = CollectionStorer(self.path + path, validateResourceNames=False)
		connection.connection.addBasicAuthorization(self.user, self.pasw)
		return connection

	def addBasicOptions(self,folderOption = True):
		self.lista.append("--Back--")
		self.items.append((False,False))
		if folderOption:
			self.lista.append("--Folder Options--")
			self.items.append((False,False))