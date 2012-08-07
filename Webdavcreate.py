import sublime
import sublime_plugin
import os.path
import shutil
import re

class WebdavcreateCommand(sublime_plugin.WindowCommand):
	def run(self, paths):
		try:
			dirName = None
			if os.path.isfile(paths[0]):
				dirName = os.path.dirname(paths[0])
			elif os.path.isdir(paths[0]):
				dirName = paths[0]

			if dirName:
				configPath = self.convert_to_system_path(sublime.packages_path() + "/webdav/webdav-config.json")

				dirName += "/webdav-config.json"
				dirName = self.convert_to_system_path(dirName)

				shutil.copyfile(configPath, dirName)
		except Exception, e:
			print "Error creando el archivo: "+str(e)

	def convert_to_system_path(self, path):
		return re.sub( re.escape("/"), re.escape(os.path.sep), path)