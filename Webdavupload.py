#import sublime
import sublime_plugin

class WebdavuploadCommand(sublime_plugin.WindowCommand):
	def run(self, paths):
		print "Uploading..."
