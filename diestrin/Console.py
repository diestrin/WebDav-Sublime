from sublime import set_timeout

class Console(object):
	def __init__(self, window):
		self.window = window
		self.panel = self.window.get_output_panel("webdav")
		self.panel.settings().set("word_wrap", True)
		self.is_loading = False
		self.status = None
		self.queue = []

	def show(self):
		self.window.run_command("show_panel", {"panel":"output.webdav"})

	def hide(self):
		self.window.run_command("hide_panel", {"panel":"output.webdav"})

	def log(self, message, is_loader = False):
		if not is_loader and self.is_loading:
			self.queue.append(lambda: self.log(message, is_loader))
			return

		edit = self.panel.begin_edit()
		self.panel.insert(edit, self.panel.size(), message)
		self.panel.end_edit(edit)
		self.panel.show(self.panel.size())

	def begin_loading(self, message):
		"Iniciando loading para: " + message
		if self.is_loading:
			self.queue.append(lambda: self.begin_loading(message))
			return

		self.log(message)
		self.show()
		self.is_loading = True
		self.loading()

	def end_loading(self, status):
		self.status = status
		self.is_loading = False
		self.loading()

	def loading(self):
		if self.is_loading:
			self.log(".", True)
			set_timeout(self.loading, 150)
		elif self.status:
			self.log(self.status + "\n", True)
			self.status = None
			self.flush_queue()

	def flush_queue(self):
		if len(self.queue):
			self.queue.pop(0)()