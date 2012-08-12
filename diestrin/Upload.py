#import sublime
from webdav.WebdavClient import AuthorizationError
from diestrin import Threads, Config, Util

import os
import re

class Upload(object):
	def __init__(self, paths=None, remote_path=None, config=None, pathToUplaod=None, resource=None, console=None, callback=None):
		self.util = Util.Util()
		self.console = console
		self.callback = callback
		self.resource = resource
		self.config = config
		
		# None values
		self.config = None
		self.path = paths[0] if len(paths) else None
		self.total_no_files = 0
		self.list_to_upload = []

		if paths:
			self.init_form_command()
		elif resource:
			self.upload_from_resource(pathToUplaod, self.handle_thread)

	def init_form_command(self):
		self.console.begin_loading("Obteniendo archivo de configuracion")

		self.config = Config.Config(self.path)

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

		if os.path.isfile(self.path):
			request_url = self.util.get_path_form_local(
					self.config.config_path, 
					self.path, 
					self.url + self.config.root
				)
			self.file_url = self.util.get_path_form_local(
					self.config.config_path, 
					self.path, 
					self.url + self.config.root, 
					True
				)
			self.getFolder(request_url, self.handle_command_thread)

		elif os.path.isdir(self.path):
			request_url = self.util.get_path_form_local(
					self.config.config_path, 
					self.path, 
					self.url + self.config.root, 
					True
				)
			self.list_to_upload = []
			self.validate_remote(request_url, {
					"user":self.config.user, 
					"password":self.config.password
				}, lambda request_url: self.getFolder(request_url, self.manage_folder_upload))

	def upload_from_resource(self, pathToUpload, callback):
		self.console.begin_loading("Subiendo el archivo: " + pathToUpload)

		file_route = self.util.get_path_form_remote(
				self.config.config_path, 
				self.config.remote_path, 
				pathToUpload
			)
		
		if not os.path.exists(file_route):
			self.console.end_loading("Error: no existe la ruta " + file_route)
			return

		thread = Threads.WebdavUploadFile(self.resource[0], file_route)
		thread.start()
		Threads.Handle(thread, callback)

	def getFolder(self, path,callback):
		self.console.begin_loading("Conectando a " + path)
		self.util.get_collection(path, {"user":self.config.user, "password":self.config.password}, callback)

	def manage_folder_upload(self, thread):
		folders = 0
		if thread.error:
			self.console.end_loading("Error: " + thread.error)
			return
			
		elif thread.result:
			self.console.end_loading("Listo")
			for resource, properties in thread.result:
				if properties.getResourceType() == "collection":
					self.getFolder(resource.url, self.manage_folder_upload)
					folders += 1
				elif properties.getResourceType() == "resource":
					self.list_to_upload.append((resource, properties))

		self.total_no_files = len(self.upload_all_items)

		if folders is 0:
			self.upload_item_numer = 0
			self.upload_all_items()

	def upload_all_items(self):
		if len(self.list_to_upload):
			resource  = self.list_to_upload.pop(self.upload_item_numer)[0]
			self.upload_from_resource(self.config, self.url + self.config.root, resource.url, resource, self.upload_all_callback)

	def validate_remote(self, url=None, auth={}, callback=None):
		self.console.begin_loading("Verificando el directorio %s" % str(url))
		thread = Threads.WebdavTestFile(url, auth, callback)
		thread.start()
		Threads.Handle(thread, self.handle_validate)

	# HANDLERS #

	def handle_validate(self, thread):
		if thread.error:
			self.console.end_loading("el directorio aun no existe")
			self.validate_remote(os.path.dirname(thread.url), thread.auth, thread.callback)
			return

		self.console.end_loading("se verifico correctamente")
		thread.callback(thread.url)

	def upload_all_callback(self, thread):
		if self.thread.result == "Succes":
			self.console.end_loading("lista la descarga en " + self.thread.local_path)
			if self.callback:
				self.callback()
		elif self.thread.result == "Error":
			self.console.end_loading("error en la descarga")

		if len(self.list_to_upload):
			self.upload_all_items()
		else:
			self.console.log("Se descargaron %i archivos" % self.total_no_files)

	def handle_thread(self, thread):
		if thread.error:
			if re.search("precondition failed", thread.error, re.I):
				self.console.end_loading("Es necesario borrar el archivo para volver a subirlo")
				self.console.begin_loading("Eliminando el archivo en el servidor")
				new_thread = Threads.WebdavDeleteFile(thread.collection, thread.local_path)
				new_thread.start()
				Threads.Handle(new_thread, self.handle_delete_upload)
				return

			self.console.end_loading("Error al subir el archivo " +  thread.local_path + ": " + thread.error)
		elif thread.result == "Succes":
			self.console.end_loading("el archivo " + thread.local_path + " fue subido exitosamente.")
			if self.callback:
				self.callback()

	def handle_delete_upload(self, thread):
		if thread.error:
			self.console.end_loading("ocurrio un error borrando el archivo " + thread.error)
			return
		self.console.end_loading(" el archivo fue borrado exitosamente")

		self.console.begin_loading("Creando el archivo en el servidor")
		new_thread = Threads.WebdavCreateFile(thread.collection, thread.local_path)
		new_thread.start()
		Threads.Handle(new_thread, self.handle_thread)

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

			if not request_resource:
				self.console.begin_loading("Creando el archivo en el servidor")
				thread = Threads.WebdavCreateFile(thread.collection, self.path)
				thread.start()
				Threads.Handle(thread, self.handle_thread)
				return

			self.console.begin_loading("Subiendo: ")
			
			thread = Threads.WebdavUploadFile(request_resource, self.path)
			thread.start()
			Threads.Handle(thread, self.handle_thread)

		except AuthorizationError, e:
			self.console.end_loading("Error: " + str(e))
			self.console.log("Resource " + request_resource + "\n")
			self.console.log("Local path: " + self.path + "\n")
