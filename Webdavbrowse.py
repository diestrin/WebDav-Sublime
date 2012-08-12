#import sublime
import sublime_plugin
from diestrin import Download, Upload, Console, Browse, Config

class WebdavbrowseCommand(sublime_plugin.WindowCommand):

	def run(self, paths):
		self.console = Console.Console(self.window)

		self.console.begin_loading("Obteniendo el archivo de configuracion")
		self.config = Config.Config(paths[0])
		self.config.get_host_config()

		self.url = self.config.protocol + "://" + self.config.host + ":" + self.config.port

		if self.config.error:
			self.console.show()
			self.console.end_loading("Error obteniendo el archivo de configuracion: " + str(self.config.error))
			return
		else:
			self.console.end_loading("Listo")

		self.browse = Browse.Browse(paths[0], self.window, self.console, config = self.config, options = {
			"folder":[
				{
					"name": "-- Download --",
					"fn": 	lambda resource: self.download_fodler(resource)
				},{
					"name": "--  Upload  --",
					"fn": 	lambda resource: self.upload_folder(resource)
				},{
					"name": "--  Delete  --",
					"fn": 	lambda resource: self.delete_folder(resource)
				}
			],
			"files":[
				{
					"name": "-- Download --",
					"fn": 	lambda resource: self.download_file(resource)
				},{
					"name": "--  Upload  --",
					"fn": 	lambda resource: self.upload_file(resource)
				},{
					"name": "--  Delete  --",
					"fn": 	lambda resource: self.delete_file(resource)
				}
			]})

	def upload_folder(self, resource):
		Upload.Upload(remote_path=self.url + self.config.root, pathToDownload=resource[0].url, 
				config=self.config, resource=resource, console=self.console, callback=self.browse.restore_last_session)

	def download_fodler(self, resource):
		Download.Download(remote_path=self.url + self.config.root, pathToDownload=resource[0].url, 
			config=self.config, resource=resource, console=self.console, callback=self.browse.restore_last_session)

	def delete_folder(self, resource):
		print "Borrando folder"

	def upload_file(self, resource):
		self.upload_folder(resource)

	def download_file(self, resource):
		self.download_fodler(resource)

	def delete_file(self, resource):
		print "Borrando archivo"
