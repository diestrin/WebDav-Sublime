from webdav.WebdavClient import AuthorizationError
from diestrin import Errors, Threads, Download, Upload, Console

import sublime
import sublime_plugin

import json
import os
import re

class WebdavbrowseCommand(sublime_plugin.WindowCommand):

	def run(self, paths):
		deepFolder = len(str(paths[0]).split("\\"))
		stepBack = ""
		self.config_path = None
		self.config_data = None
		config_file = None
		initial_path = paths[0] if os.path.isdir(paths[0]) else os.path.dirname(paths[0])

		self.console = Console.Console(self.window)
		self.console.show()

		self.console.log("Obteniendo archivo de configuracion")
		self.console.begin_loading()

		while deepFolder > 0:
			temp_path = initial_path + stepBack + os.path.sep + "webdav-config.json"
			if not os.path.exists(temp_path):
				deepFolder -= 1
				stepBack += os.path.sep + ".."
				continue

			if config_file != None:
				break

			self.config_path = os.path.normpath(temp_path)
			config_file = open(self.config_path)
			self.config_data = json.load(config_file)
			config_file.close()
			break

		if not config_file:
			self.console.end_loading("Error")
			return

		self.console.end_loading("Listo")
		self.console.log("Leyendo archivo de configuracion")
		self.console.begin_loading()

		try:
			self.host = str(self.config_data["host"])
			self.root = str(self.config_data["root"]) if self.config_data.has_key("root") else "/"
			self.port = str(self.config_data["port"]) if self.config_data.has_key("port") else None
			self.protocol = "https" if self.config_data.has_key("ssl") and self.config_data["ssl"] else "http"

			self.user = str(self.config_data["user"]) if self.config_data.has_key("user") else None
			self.password = str(self.config_data["password"]) if  self.config_data.has_key("password") else None

			if not self.port:
				if self.protocol == "http":
					self.port = "80"
				elif self.protocol == "https":
					self.port = "443"

		except KeyError, e:
			self.console.end_loading("Error")
			raise Errors.BadConfig(e)

		self.console.end_loading("Listo")
			
		self.url = self.protocol + "://" + self.host + ":" + self.port

		self.current_path = self.root
		self.items_names = []
		self.items = []

		self.getFolder(self.root)

	def getFolder(self, path):
		self.console.log("Conectando a " + self.url + path)
		self.console.begin_loading()
		print "-- Iniciando hilo de ejecucion --"
		thread = Threads.WebdavGetCollection(self.url + path, {"user":self.user, "password":self.password})
		thread.start()
		self.handle_threads(thread)

	def handle_threads(self, thread):
		if not thread.is_alive() and thread.result:
			self.console.end_loading("Listo")
			self.console.log("Leyendo la respuesta")
			self.console.begin_loading()
			try:
				self.addBasicOptions()

				for resource, properties in thread.result:
					self.items_names.append( properties.getDisplayName() )
					self.items.append( (resource, properties) )

				self.console.end_loading("Listo")
				print "-- Folder obtenido! --"

			except AuthorizationError, e:
				self.console.end_loading("Error")
				raise Errors.BadAuthorization(e)

			self.console.log("Mostrando las opciones\n")
			self.window.show_quick_panel(self.items_names, self.itemCallback)
			return

		sublime.set_timeout(lambda: self.handle_threads(thread), 100)
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
			Download.Download(remote_path=self.url + self.root, pathToDownload=self.selected_item[0].url, 
				config_path=self.config_path, resource=self.selected_item, console=self.console, callback=self.addFileOptions)
		elif index == 2:	# Upload
			Upload.Upload(remote_path=self.url + self.root, pathToDownload=self.selected_item[0].url, 
				config_path=self.config_path, resource=self.selected_item, console=self.console, callback=self.addFileOptions)




















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
