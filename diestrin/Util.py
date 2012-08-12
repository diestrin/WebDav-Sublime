from diestrin import Threads
import os
import re

class Util(object):

	def get_collection(self, path, auth, callback):
		thread = Threads.WebdavGetCollection(path, auth)
		thread.start()

		Threads.Handle(thread, callback)

	def get_path_form_local(self, root_path, local_path, remote_root, include_file = False):
		if not include_file:
			local_path = os.path.dirname(local_path)

		project_root = os.path.dirname(root_path)
		url_path = re.sub(re.escape( os.path.sep ), "/", re.sub( re.escape( project_root ), "", local_path ))
		return remote_root + url_path

	def get_path_form_remote(self, root_path, remote_path, local_path, check_path = True):
		project_root = os.path.dirname(root_path)
		file_path = re.sub(re.escape("/"), re.escape( os.path.sep ), re.sub( re.escape( remote_path ), "", local_path ))
		if check_path:
			self.check_local_path(project_root + file_path)
		return project_root + file_path

	def check_local_path(self, path):
		dirname = os.path.dirname(path)
		if not os.path.exists(dirname):
			os.makedirs(dirname)