import sublime
import re

class Console(object):
	def __init__(self, window):
		self.window = window
		self.panel = self.window.get_output_panel("webdav")
		self.is_loading = False
		self.loading_end = False
		self.max_num_char = 20

	def show(self):
		self.window.run_command("show_panel", {"panel":"output.webdav"})

	def hide(self):
		self.window.run_command("hide_panel", {"panel":"output.webdav"})

	def log(self, message):
		edit = self.panel.begin_edit()
		self.panel.insert(edit, self.panel.size(), message)
		self.panel.end_edit(edit)
		self.panel.show(self.panel.size())

	def begin_loading(self, message):
		self.log(message + "\n")
		self.is_loading = True
		self.loading_end = True
		self.contador = 0
		self.loading()
		self.show()

	def end_loading(self, status):
		self.status = status
		self.is_loading = False

	def loading(self):
		breakLine = ""
		if self.contador == self.max_num_char:
			breakLine = "\n"

		if self.is_loading:
			self.contador += 1
			self.log("." + breakLine)
			sublime.set_timeout(self.loading, 250)
		elif self.status and self.loading_end:
			loading_end = False
			self.log(self.status + "\n")
