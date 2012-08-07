from webdav.WebdavClient import AuthorizationError
from diestrin import Threads, Download, Upload, Console, Config

import sublime
import sublime_plugin

import re

class WebdavbrowseCommand(sublime_plugin.WindowCommand):

	def run(self, paths):
		self.console = Console.Console(self.window)

		self.console.begin_loading("Obteniendo archivo de configuracion")

		self.config = Config.Config(paths[0])

		if(self.config.config_data):
			self.console.end_loading("Listo")
		else:
			self.console.end_loading("Error")
		
		self.console.begin_loading("Leyendo archivo de configuracion")

		self.config.get_host_config()

		if(self.config.host):
			self.console.end_loading("Listo")
		else:
			self.console.end_loading("Error")
			
		self.url = self.config.protocol + "://" + self.config.host + ":" + self.config.port

		self.current_path = self.config.root
		self.items_names = []
		self.items = []

		self.getFolder(self.config.root)

	def getFolder(self, path):
		self.console.begin_loading("Conectando a " + self.url + path)

		thread = Threads.WebdavGetCollection(self.url + path, {"user":self.config.user, "password":self.config.password})
		thread.start()

		Threads.Handle(thread, self.handle_threads)

	def handle_threads(self, thread):
		if thread.result:
			self.console.end_loading("Listo")
			self.console.begin_loading("Leyendo la respuesta")

			try:
				self.addBasicOptions()

				for resource, properties in thread.result:
					self.items_names.append( properties.getDisplayName() )
					self.items.append( (resource, properties) )

				self.console.end_loading("Listo")

			except AuthorizationError, e:
				self.console.end_loading("Error: " + str(e))
				return

			self.console.log("Mostrando las opciones\n")
			self.window.show_quick_panel(self.items_names, self.itemCallback)
			return

	def addBasicOptions(self):
		self.items_names.append("-- Back --")
		self.items_names.append("-- Options --")

		self.items.append((False, False))
		self.items.append((False, False))

	def itemCallback(self, index):
		if index > 1 or index == 0:
			self.console.log("seleccionado el item " + self.items_names[index] + "\n")
			if index == 0 or self.items[index][1].getResourceType() == "collection":

				self.current_path = re.sub(u"\w+\/$", "", self.current_path) if index == 0 else self.items[index][0].path

				self.items_names = []
				self.items = []

				self.getFolder(self.current_path)

			else:
				self.selected_item = self.items[index]
				self.addFileOptions()

		elif index == 1:
			self.addFolderOptions()

	def addFolderOptions(self):
		optionItems = []

		optionItems.append("-- Back --")
		optionItems.append("-- Download --")
		optionItems.append("-- Upload --")

		self.window.show_quick_panel(optionItems, self.optionsCallback)

	def addFileOptions(self):
		optionItems = []

		optionItems.append("-- Back --")
		optionItems.append("-- Download --")
		optionItems.append("-- Upload --")

		self.window.show_quick_panel(optionItems, self.optionsCallback)

	def optionsCallback(self, index):
		if index == 0:		# Back
			self.items_names = []
			self.items = []

			self.getFolder(self.current_path)
		elif index == 1:	# Download
			Download.Download(remote_path=self.url + self.config.root, pathToDownload=self.selected_item[0].url, 
				config_path=self.config.config_path, resource=self.selected_item, console=self.console, callback=self.addFileOptions)
		elif index == 2:	# Upload
			Upload.Upload(remote_path=self.url + self.config.root, pathToDownload=self.selected_item[0].url, 
				config_path=self.config.config_path, resource=self.selected_item, console=self.console, callback=self.addFileOptions)




















"""for view in self.window.views():
	result = re.search(r"(script\.js$)", view.file_name())
	if result:
		print ".... Descargando contenido......"
		self.items[index][0].downloadFile(view.file_name(), {"Cookie":self.cookies})
		print ".....Contenido descargado......."""

"""for view in self.window.views():
	result = re.search(r"(script\.js$)", view.file_name())
	if result:
		print ".... Subiendo contenido......"
		localFile = open(view.file_name(), 'r')
		self.items[index][0].uploadFile(localFile, extra_hdrs={"Cookie":self.cookies})
		print ".....Contenido subido......."""

"""if len(paths) and os.path.exists(paths[0]):
	if os.path.isfile(paths[0]):
		print "File: ", str(os.path.basename(paths[0])), "\nSize:", str(os.path.getsize(paths[0]))
	elif os.path.isdir(paths[0]):
		print "Folder: ", str(os.path.basename(paths[0]))"""
