import os
import json

class Config(object):
	def __init__(self, path):
		self.config_path = None
		self.config_data = None
		self.error = None

		initial_path = path if os.path.isdir(path) else os.path.dirname(path)
		deepFolder = len(str(initial_path).split("\\"))
		stepBack = ""
		config_file = None

		while deepFolder > 0:
			if config_file != None:
				break

			temp_path = initial_path + stepBack + os.path.sep + "webdav-config.json"

			if not os.path.exists(temp_path):
				deepFolder -= 1
				stepBack += os.path.sep + ".."
				continue

			self.config_path = os.path.normpath(temp_path)
			config_file = open(self.config_path)
			self.config_data = json.load(config_file)
			config_file.close()
			break

	def get_config_data(self):
		return self.config_data

	def get_config_path(self):
		return self.config_path

	def get_host_config(self):
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
		except Exception, e:
			self.error = e