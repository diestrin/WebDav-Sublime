#import sublime
import sublime_plugin
from diestrin.Download import Download

class WebdavdownloadCommand(sublime_plugin.WindowCommand):
	def run(self, paths):
		Download(paths = paths)
		