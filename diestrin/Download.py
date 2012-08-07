import sublime
#from webdav.WebdavClient import AuthorizationError
from diestrin import Threads

#import json
import os
import re

class Download(object):
	def __init__(self, paths=None, remote_path=None, config_path=None, pathToDownload=None, resource=None, console=None, callback=None):
		if paths:
			return
		else:
			self.console = console
			self.console.log("Descargando: ")
			self.console.begin_loading()

			self.callback = callback
			self.project_root = os.path.dirname(config_path)
			self.local_path = re.sub(re.escape("/"), re.escape( os.path.sep ), re.sub( re.escape( remote_path ), "", pathToDownload ))
			self.check_local_path(self.project_root + self.local_path)

			self.thread = Threads.WebdavDownloadFile(resource[0], self.project_root + self.local_path)
			self.thread.start()
			self.handle_thread()

	def handle_thread(self):
		if not self.thread.is_alive():
			if self.thread.result == "Succes":
				self.console.end_loading("Listo")
				if self.callback:
					self.callback()
			elif self.thread.result == "Error":
				self.console.end_loading("Error")
		else:
			sublime.set_timeout(self.handle_thread, 100)
			return

	def check_local_path(self, path):
		dirname = os.path.dirname(path)
		if not os.path.exists(dirname):
			os.makedirs(dirname)
