import sublime
import sublime_plugin
from webdav.WebdavClient import AuthorizationError
from diestrin import Errors, Threads

import json
import os
import re

class WebdavdownloadCommand(sublime_plugin.WindowCommand):
	def run(self, args = {"paths":None, "config_data":{}, "extra_hdrs":{}, "pathToDownload":None, "config_path":None, "resource":None}):

		print "Iniciando descarga"

		if args.has_key("config_data") and args.has_key("extra_hdrs") and args.has_key("athToDownload") and args.has_key("config_path") and args.has_key("resource"):
			self.config_data = args["config_data"]
			self.config_path = args["config_path"]
			self.pathToDownload = args["pathToDownload"]
			self.extra_hdrs = args["extra_hdrs"]
			self.resource = args["resource"]
		elif args.has_key("paths"):
			self.initFromScratch(args["paths"][0])

		if not self.config_data:
			print "Descarga detenida, no hay suficiente informacion"
			return

		try:
			self.host = str(self.config_data["host"])
			self.root = str(self.config_data["root"]) if self.config_data["root"] else "/"
			self.port = str(self.config_data["port"]) if self.config_data["port"] else "80"
			self.protocol = "https" if self.config_data["ssl"] else "http"

			self.user = str(self.config_data["user"]) if self.config_data["user"] else None
			self.password = str(self.config_data["password"]) if self.config_data["password"] else None

		except KeyError, e:
			raise Errors.BadConfig(e)

		self.host = self.protocol + "://" + self.host + ":" + self.port

		if args.has_key("extra_hdrs"):
			self.donwload()
		else:
			self.requestFolder(args["paths"][0])

	def initFromScratch(self, path):
		deepFolder = len(str(path).split("\\"))
		stepBack = ""
		config_path = None
		self.config_data = None
		config_file = None
		initial_path = path if os.path.isdir(path) else os.path.dirname(path)

		while deepFolder > 0:
			temp_path = initial_path + stepBack + os.path.sep + "webdav-config.json"
			if not os.path.exists(temp_path):
				deepFolder -= 1
				stepBack += os.path.sep + ".."
				continue

			if config_file != None:
				break

			self.config_path = os.path.normpath(temp_path)
			config_file = open(config_path)
			self.config_data = json.load(config_file)
			config_file.close()
			break

		self.relative_path = re.sub(re.escape(self.config_path), "", path)

	def download(self, resource):
		localFilePath = re.sub( re.escape( self.host + self.root ), "", self.pathToDownload )
		print localFilePath
		#self.resource.downloadFile(localFilePath, self.extra_hdrs)

	def requestFolder(self, path):
		self.path_to_save = re.sub( re.escape( os.path.dirname(self.config_path) ), "", path )
		thread = Threads.WebdavGetCollection(self.host, self.root + self.path_to_save, self.user, self.password)
		thread.start()
		self.handle_threads(thread)

	def handle_threads(self, thread):
		if thread.result:
			try:
				for resource, properties in thread.result:
					print resource.url			

			except AuthorizationError, e:
				raise Errors.BadAuthorization(e)

			return

		sublime.set_timeout(lambda: self.handle_threads(thread), 100)
		return