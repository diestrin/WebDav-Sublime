import sublime_plugin
from diestrin import Download, Console

class WebdavdownloadCommand(sublime_plugin.WindowCommand):
	def run(self, paths):
		Download.Download(paths = paths, console = Console.Console(self.window))
		