import sublime
from webdav.WebdavClient import AuthorizationError
from diestrin import Threads, Config

import os
import re

class Download(object):
	def __init__(self, paths=None, remote_path=None, config_path=None, pathToDownload=None, resource=None, console=None, callback=None):
		self.console = console
		self.callback = callback

		if paths:
			self.init_form_command(paths[0])

		else:
			self.download_from_resource(config_path, remote_path, pathToDownload, resource[0], self.handle_thread)
			
	def download_from_resource(self, config_path, remote_path, pathToDownload, resource, callback):
		self.console.begin_loading("Descargando: ")
		
		url = self.get_path_form_remote(config_path, remote_path, pathToDownload)

		self.thread = Threads.WebdavDownloadFile(resource, url)
		self.thread.start()
		Threads.Handle(self.thread, callback)
		
	def handle_thread(self, thread):
		if thread.result == "Succes":
			self.console.end_loading("lista la descarga en " + thread.local_path)
			if self.callback:
				self.callback()
		elif thread.result == "Error":
			self.console.end_loading("error en la descarga")

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
		return project_root + file_path

	def getFolder(self, path, callback):
		self.console.begin_loading("Conectando a " + path)

		thread = Threads.WebdavGetCollection(path, {"user":self.config.user, "password":self.config.password})
		thread.start()

		Threads.Handle(thread, callback)

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
			
		self.url = self.config.protocol + "://" + self.config.host + ":" + self.config.port

		if os.path.isfile(path):
			request_url = self.get_path_form_local(self.config.config_path, path, self.url + self.config.root)
			self.file_url = self.get_path_form_local(self.config.config_path, path, self.url + self.config.root, True)
			self.getFolder(request_url, self.handle_command_thread)
			
		elif os.path.isdir(path):
			request_url = self.get_path_form_local(self.config.config_path, path, self.url + self.config.root, True)
			self.list_to_download = []
			self.getFolder(request_url, self.manage_folder_download)

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

			self.console.begin_loading("Descargando: ")
			
			self.thread = Threads.WebdavDownloadFile(request_resource, self.path)
			self.thread.start()
			self.handle_thread()

		except AuthorizationError, e:
			self.console.end_loading("Error: " + str(e))

	def getFolderToDownload(self, resource):
		thread = Threads.WebdavGetCollection(auth={"user":self.config.user, "password":self.config.password}, collection=resource)
		Threads.Handle(thread, self.manage_folder_download)

	def manage_folder_download(self, thread):
		folders = 0
		if thread.error:
			self.console.end_loading("Error: " + thread.error)
			
		elif thread.result:
			self.console.end_loading("Listo")
			for resource, properties in thread.result:
				if properties.getResourceType() == "collection":
					#self.getFolderToDownload(resource)
					self.getFolder(resource.url, self.manage_folder_download)
					folders += 1
				elif properties.getResourceType() == "resource":
					self.list_to_download.append((resource, properties))

		if folders is 0:
			self.download_item_numer = 0
			self.download_all_items()

	def download_all_items(self):
		if len(self.list_to_download):
			resource  = self.list_to_download.pop(self.download_item_numer)[0]
			print resource
			self.download_from_resource(self.config.config_path, self.url + self.config.root, resource.url, resource, self.dowload_all_callback)

	def dowload_all_callback(self, thread):
		if self.thread.result == "Succes":
			self.console.end_loading("lista la descarga en " + self.thread.local_path)
			if self.callback:
				self.callback()
		elif self.thread.result == "Error":
			self.console.end_loading("error en la descarga")

		if len(self.list_to_download):
			self.download_all_items()