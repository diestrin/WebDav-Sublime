from webdav.WebdavClient import AuthorizationError
from webdav.Connection import Connection
from diestrin import Errors, Threads

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
		config_data = None
		config_file = None
		initial_path = paths[0] if os.path.isdir(paths[0]) else os.path.dirname(paths[0])

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
			config_data = json.load(config_file)
			config_file.close()
			break

		if not config_file:
			return

		try:
			self.host = str(config_data["host"])
			self.root = str(config_data["root"]) if config_data.has_key("root") else "/"
			self.port = str(config_data["port"]) if config_data.has_key("port") else None
			self.protocol = "https" if config_data.has_key("ssl") and config_data["ssl"] else "http"

			self.user = str(config_data["user"]) if config_data.has_key("user") else None
			self.password = str(config_data["password"]) if  config_data.has_key("password") else None

			if not self.port:
				if self.protocol == "http":
					self.port = "80"
				elif self.protocol == "https":
					self.port = "443"

		except KeyError, e:
			raise Errors.BadConfig(e)
			
		self.url = self.protocol + "://" + self.host + ":" + self.port

		self.current_path = self.root
		self.items_names = []
		self.items = []

		self.getFolder(self.root)

	def getFolder(self, path):
		print "-- Iniciando hilo de ejecucion --"
		thread = Threads.WebdavGetCollection(self.url + path, {"user":self.user, "password":self.password})
		thread.start()
		self.handle_threads(thread)

	def handle_threads(self, thread):
		if not thread.is_alive() and thread.result:
			try:
				self.addBasicOptions()

				for resource, properties in thread.result:
					self.items_names.append( properties.getDisplayName() )
					self.items.append( (resource, properties) )

				print "-- Folder obtenido! --"

			except AuthorizationError, e:
				raise Errors.BadAuthorization(e)

			self.window.show_quick_panel(self.items_names, self.itemCallback)
			return

		sublime.set_timeout(lambda: self.handle_threads(thread), 100)
		return

	def getCookies(self, item):
		return item.getSpecificOption("set-cookie")

	def addBasicOptions(self):
		self.items_names.append("-- Back --")
		self.items_names.append("-- Options --")

		self.items.append((False, False))
		self.items.append((False, False))

	def itemCallback(self, index):
		if index > 1 or index == 0:
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
			self.window.run_command("webdavdownload")#, args = {
			#		"config_data":		self.config_data,
			#		"extra_hdrs":		{"Cookie":self.cookie},
			#		"pathToDownload":	self.selected_item.url,
			#		"config_path":		self.config_path
			#	})
		elif index == 2:	# Upload
			self.window.run_command("webdavupload")



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
