from webdav.WebdavClient import AuthorizationError
from diestrin import Config, Util
import re
import os

class Browse(object):
	"""
	Esta objeto muestra el custom navigation panel en sublime para navegar remotamente por los archivos del servidro
	@params:
		path: [string] Ruta a iniciar la navegacion
		console: [diestrin.Console.Console] Objeto para loguear en la vista
		config = None: [diestrin.Config.Config] Objeto para obtener la configuracion
		options = {"folder":[], "files":[]}: [dictionary] Diccionario de opciones a mostrar en los archivos
	"""
	def __init__(self, path, window, console, config=None, callback=None, options={"folder":[], "files":[]}, select_file=False):
		self.window = window
		self.console = console
		self.config = config
		self.util = Util.Util()
		self.current_path = None
		self.items_names = []
		self.items = []
		self.callback = callback
		self.options = options
		self.select_file = select_file
		self.selected_item = None

		if not self.config:
			self.__prepare_config(path)

		self.base_url = self.config.protocol + "://" + self.config.host + ":" + self.config.port
		self.current_path = self.config.root
		local_root = os.path.dirname(self.config.config_path)
		temp_path = os.path.dirname(path) if os.path.isfile(path) else path

		reg_result = re.search("^" + re.escape(local_root) + "\\/{0,1}$", temp_path)

		if not reg_result:
			start_path = re.sub(re.escape(local_root), "", temp_path)
			start_path = re.sub("\\\\", "/", start_path)
			self.current_path += start_path

		self.__get_collection()

	def restore_last_session(self):
		self.__get_collection()

	def __get_collection(self):
		self.console.begin_loading("Obteniendo el folder: " + self.base_url + self.current_path)

		self.util.get_collection(self.base_url + self.current_path, {"user":self.config.user, "password":self.config.password}, self.__default_get_collection_callback)

	def __default_get_collection_callback(self, thread):
		if thread.result:
			self.console.end_loading("Listo")
			self.console.begin_loading("Leyendo la respuesta")

			self.items_names = []
			self.items = []

			try:
				self.selected_item = (thread.collection,)

				if not self.select_file:
					self.__addBasicOptions()

				for resource, properties in thread.result:
					self.items_names.append( properties.getDisplayName() )
					self.items.append( (resource, properties) )

				self.console.end_loading("Listo")

			except AuthorizationError, e:
				self.console.end_loading("Error: " + str(e))
				return

			self.console.log("Mostrando las opciones\n")
			self.window.show_quick_panel(self.items_names, self.__select_callback)

	def __select_callback(self, index):
		selected = self.items[index]

		if self.select_file:
			self.callback(selected)
			return

		if index < 2:
			self.items[index]()
		elif index >= 2:
			self.selected_item = self.items[index]
			if self.items[index][1].getResourceType() == "collection":
				self.console.log("Seleccionado el directorio " + self.items_names[index] + "\n")
				
				self.current_path = self.items[index][0].path

				self.__get_collection()
			elif self.items[index][1].getResourceType() == "resource":
				self.console.log("Seleccionado el archivo " + self.items_names[index] + "\n")
				self.__options(True)

	def __select_file_option(self, index):
		if index is 0:
			self.__back()
			return

		selected = self.selected_item
		self.selected_item = None
		self.options["files"][index - 1]["fn"](selected)

	def __select_folder_option(self, index):
		if index is 0:
			self.__back()
			return

		selected = self.selected_item
		self.selected_item = None
		self.options["folder"][index - 1]["fn"](selected)

	def __addBasicOptions(self):
		self.items_names.append("-- Back --")
		self.items.append(self.__back)
		self.items_names.append("-- Options --")
		self.items.append(self.__options)

	def __back(self):
		if self.current_path != self.config.root:
			self.current_path = os.path.dirname(re.sub("\\/$", "", self.current_path))

		self.__get_collection()

	def __options(self, is_file=False):
		if is_file :
			if len(self.options["files"]):
				options_list = []
				options_list.append("-- Back --")
				
				for option in self.options["files"]:
					options_list.append(option["name"])

				self.console.log("Mostrando las opciones para el archivo %s\n" % str(self.selected_item[0].url))
				self.window.show_quick_panel(options_list, self.__select_file_option)
		else:
			if len(self.options["folder"]):
				options_list = []
				options_list.append("-- Back --")

				for option in self.options["folder"]:
					options_list.append(option["name"])

				self.console.log("Mostrando las opciones para el folder %s\n" % str(self.selected_item[0].url))
				self.window.show_quick_panel(options_list, self.__select_folder_option)

	def __prepare_config(self, path):
		if not self.config:
			self.console.begin_loading("Obteniendo archivo de configuracion")

			self.config = Config.Config(path)

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
