import sublime
from webdav.WebdavClient import AuthorizationError
from diestrin import Threads, Config

import os
import re

class Upload(object):
	def __init__(self, paths=None, remote_path=None, config_path=None, pathToDownload=None, resource=None, console=None, callback=None):
		self.console = console
		self.callback = callback

		if paths:
			if os.path.isfile(paths[0]):
				self.init_form_command(paths[0])
			elif os.path.isdir(paths[0]):
				self.manage_folder_download(paths[0])
		else:
			self.console = console
			self.console.begin_loading("Subiendo el archivo: " + pathToDownload)

			self.callback = callback
			file_route = self.get_path_form_remote(config_path, remote_path, pathToDownload)
			
			if not os.path.exists(file_route):
				self.console.end_loading("Error: no existe la ruta " + file_route)
				return

			self.thread = Threads.WebdavUploadFile(resource[0], file_route)
			self.thread.start()
			self.handle_thread()

	def handle_thread(self):
		if not self.thread.is_alive():
			if self.thread.result == "Succes":
				self.console.end_loading("el archivo " + self.thread.local_path + "fue subido exitosamente.")
				if self.callback:
					self.callback()
			elif self.thread.result == "Error":
				self.console.end_loading("Error al subir el archivo " +  self.thread.local_path)
		else:
			sublime.set_timeout(self.handle_thread, 100)
			return

	def check_local_path(self, path):
		dirname = os.path.dirname(path)
		if not os.path.exists(dirname):
			os.makedirs(dirname)

	def get_path_form_local(self, root_path, local_path, remote_root, include_file = False):
		if not include_file:
			local_path = os.path.dirname(local_path)
		project_root = os.path.dirname(root_path)
		url_path = re.sub(re.escape( os.path.sep ), "/", re.sub( re.escape( project_root ), "", local_path ))
		return remote_root + url_path

	def get_path_form_remote(self, root_path, remote_path, local_path, check_paht = True):
		project_root = os.path.dirname(root_path)
		file_path = re.sub(re.escape("/"), re.escape( os.path.sep ), re.sub( re.escape( remote_path ), "", local_path ))
		if check_paht:
			self.check_local_path(project_root + file_path)
		return project_root + os.path.sep + file_path

	def getFolder(self, path):
		self.console.begin_loading("Conectando a " + path)

		thread = Threads.WebdavGetCollection(path, {"user":self.config.user, "password":self.config.password})
		thread.start()

		Threads.Handle(thread, self.handle_command_thread)

	def init_form_command(self, path):
		self.console.begin_loading("Obteniendo archivo de configuracion")

		self.config = Config.Config(path)
		self.path = path

		if(self.config.config_data):
			self.console.end_loading("listo el archivo de configuracion")
		else:
			self.console.end_loading("error en el archivo de configuracion")
		
		self.console.begin_loading("Leyendo archivo de configuracion")

		self.config.get_host_config()

		if(self.config.host):
			self.console.end_loading("listo la lecura del archivo")
		else:
			self.console.end_loading("error en la lectura")
			
		url = self.config.protocol + "://" + self.config.host + ":" + self.config.port

		request_url = self.get_path_form_local(self.config.config_path, path, url + self.config.root)
		self.file_url = self.get_path_form_local(self.config.config_path, path, url + self.config.root, True)

		self.getFolder(request_url)

	def handle_command_thread(self, thread):
		if thread.error:
			self.console.end_loading("ocurrio un error " + thread.error)
			return
			
		self.console.end_loading("listo la conexion")
		self.console.begin_loading("Leyendo la respuesta")

		request_resource = None
		try:
			for resource, properties in thread.result:
				if str(properties.getDisplayName()) == str(os.path.basename(self.file_url)):
					request_resource = resource

			self.console.end_loading("listo la lectura de la respuesta")

			self.console.begin_loading("Subiendo: ")
			
			self.thread = Threads.WebdavUploadFile(request_resource, self.path)
			self.thread.start()
			self.handle_thread()

		except AuthorizationError, e:
			self.console.end_loading("Error: " + str(e))

	def manage_folder_download(self, folder_path):
		walk = os.walk(folder_path)
		files_in_fodler = []

		for directory in walk:
			for file_name in directory[2]:
				files_in_fodler.append(os.path.join(directory[0], file_name))