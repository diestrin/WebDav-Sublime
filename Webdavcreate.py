import sublime
import sublime_plugin
import os.path
import shutil

class WebdavcreateCommand(sublime_plugin.WindowCommand):
	def run(self, paths):
		if len(paths) and os.path.exists(paths[0]):
			dirName = None
			if os.path.isfile(paths[0]):
				dirName = os.path.dirname(paths[0])
			elif os.path.isdir(paths[0]):
				dirName = paths[0]

			if dirName:
				configPath = sublime.packages_path() + "/webdav/webdav-config.json"
				dirName += "/webdav-config.json"
				if os.path.exists(configPath):
					shutil.copyfile(configPath, dirName)
