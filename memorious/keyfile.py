# Copyright (C) 2010-2012 Vincent Ollivier
#
# Memorious is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Memorious is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.

import errno
import os

class KeyFile(object):

    def __init__(self, path, key_size=256):
        self.path = path
        self.size = key_size

    @property
    def key(self):
        try:
            with open(self.path, 'rb') as f:
                return f.read(self.size // 8)
        except IOError:
            #raise FileNotFoundError("No such key file: '%s'" % self.path)
            raise IOError(errno.ENOENT, "No such key file: '%s'" % self.path)

    @classmethod
    def generate(cls, path, key_size=256, file_size=1024):
        """Generate a new key file."""
        assert file_size >= key_size
        if os.path.isfile(path):
            #raise FileExistsError("Key file exist: '%s'" % key_file)
            raise IOError(errno.EEXIST, "Key file exist: '%s'" % path)
        flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL
        if os.name == 'nt':
            flags = flags | os.O_BINARY
        with os.fdopen(os.open(path, flags, 0o400), 'wb') as f:
            f.write(os.urandom(file_size))
        return cls(path, key_size)
