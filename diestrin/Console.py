import sublime

class Console(object):
	def __init__(self, window):
		self.window = window
		self.panel = self.window.get_output_panel("webdav")
		self.is_loading = False

	def show(self):
		self.window.run_command("show_panel", {"panel":"output.webdav"})

	def hide(self):
		self.window.run_command("hide_panel", {"panel":"output.webdav"})

	def log(self, message):
		edit = self.panel.begin_edit()
		self.panel.insert(edit, self.panel.size(), message)
		self.panel.end_edit(edit)
		self.panel.show(self.panel.size())

	def begin_loading(self):
		self.is_loading = True
		self.loading()

	def end_loading(self, status):
		self.status = status
		self.is_loading = False

	def loading(self):
		if self.is_loading:
			sublime.set_timeout(lambda: self.log("."), 250)
			sublime.set_timeout(self.loading, 250)
		elif self.status:
			self.log(self.status + "\n")
