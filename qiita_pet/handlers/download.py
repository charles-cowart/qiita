from tornado.web import authenticated

from os.path import split

from .base_handlers import BaseHandler
from qiita_pet.exceptions import QiitaPetAuthorizationError
from qiita_db.util import filepath_id_to_rel_path
from qiita_db.meta_util import get_accessible_filepath_ids


class DownloadHandler(BaseHandler):
    @authenticated
    def get(self, filepath_id):
        filepath_id = int(filepath_id)
        # Check access to file
        accessible_filepaths = get_accessible_filepath_ids(self.current_user)

        if filepath_id not in accessible_filepaths:
            raise QiitaPetAuthorizationError(
                self.current_user, 'filepath id %d' % filepath_id)

        relpath = filepath_id_to_rel_path(filepath_id)
        fname = split(relpath)[-1]

        self.set_header('Content-Description', 'File Transfer')
        self.set_header('Content-Type', 'application/octet-stream')
        self.set_header('Content-Transfer-Encoding', 'binary')
        self.set_header('Expires',  '0')
        self.set_header('X-Accel-Redirect', '/protected/' + relpath)
        self.set_header('Content-Disposition',
                        'attachment; filename=%s' % fname)

        self.finish()
