import sublime_plugin
from diestrin import Upload, Console

class WebdavuploadCommand(sublime_plugin.WindowCommand):
	def run(self, paths):
		Upload.Upload(paths = paths, console = Console.Console(self.window))
