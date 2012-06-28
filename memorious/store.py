# Copyright (C) 2010 Vincent Ollivier <contact@vincentollivier.com>
#
# This file is part of Memorious.
#
# Memorious is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.

import errno
import os
import sqlite3
import string

from random import SystemRandom

# DES, AES, Blowfish
from Crypto.Cipher import AES as Cipher

class Store(object):
    """Manage an encrypted passwords database."""

    def __init__(self, encrypted_dump_file, key_file, key_size=256):
        """Restore in memory database from encrypted dump file.

        Keyword arguments:
        encrypted_dump_file -- the encrypted dump file path
        key_file -- the key file path
        key_size -- the key size (128, 192 or 256 bits for AES)
        """
        self.closed = False

        # Create a database in memory
        self._con = sqlite3.connect(':memory:')

        # Decrypt database dump file
        dump = ''
        self._key = KeyFile(key_file, key_size).key
        self._path = encrypted_dump_file
        if os.path.isfile(self._path):
            with open(self._path) as f:
                # Need a block cipher encryption algorithm
                # operating in cipher feedback (CFB) mode
                cipher = Cipher.new(self._key, Cipher.MODE_CFB)
                c = f.read(cipher.block_size)
                while c != '':
                    dump = '%s%s' % (dump, cipher.decrypt(c))
                    c = f.read(cipher.block_size)
                    cipher = Cipher.new(self._key, Cipher.MODE_CFB, cipher.IV)
            # Restore previous database from dump
            self._con.executescript(dump)
        else:
            print 'Creating a new database ...'
            self._con.execute("""
                CREATE TABLE slots(
                    id INTEGER PRIMARY KEY,
                    domain,
                    username,
                    password,
                    comment
                );
                """)

    @classmethod
    def open(cls, encrypted_dump_file, key_file, key_size=256):
        safe = cls(encrypted_dump_file, key_file, key_size)
        return safe

    def get(self, **params):
        """Generate row matching params in the password list."""
        self._con.row_factory = sqlite3.Row
        query = 'SELECT * FROM slots'
        values = [val for val in params.values() if val != '']
        if values:
            query += ' WHERE %s' % ' AND '.join(
                '%s=?' % key for key in params.keys() if params[key] != ''
            )
        for row in self._con.execute(query, values):
            yield row

    def put(self, **params):
        """Add a new row in the password list."""
        assert ''.join(params.keys()).isalpha()
        q_cols = ', '.join(params.keys())
        q_vals = ', '.join('?' * len(params))
        query = "INSERT INTO slots (%s) values (%s)" % (q_cols, q_vals)
        self._con.execute(query, params.values())

    def delete(self, id):
        """Remove a row from the password list."""
        self._con.execute('DELETE FROM slots WHERE id=?', (id,))

    def close(self):
        if self.closed:
            return

        # Dump database
        dump = ''.join(self._con.iterdump())

        # Encrypt dump to the persistent file
        with open(self._path, 'wb') as f:
            cipher = Cipher.new(self._key, Cipher.MODE_CFB)
            while dump:
                f.write(cipher.encrypt(dump[:cipher.block_size]))
                dump = dump[cipher.block_size:]
                cipher = Cipher.new(self._key, Cipher.MODE_CFB, cipher.IV)

        self.closed = True

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        if type is None:
            self.close()
        else:
            # An exception occurred. Any changes in the database should be
            # considered lost and not dumped into the encrypted file.
            self.closed = True


class KeyFile(object):

    def __init__(self, path, key_size=256):
        self.path = path
        self.size = key_size

    @property
    def key(self):
        try:
            with open(self.path) as f:
                return f.read(self.size / 8)
        except IOError:
            raise IOError, (errno.ENOENT, "No such key file: '%s'" % self.path)

    @classmethod
    def generate(cls, path, key_size=256, file_size=1024):
        """Generate a new key file."""
        assert file_size >= key_size
        if os.path.isfile(path):
            raise IOError, (errno.EEXIST, "Key file exist: '%s'" % path)
        with open(path, 'wb') as f:
            f.write(os.urandom(file_size))
        return cls(path, key_size)

class Password(object):
    def __init__(self, password):
        self.password = password

    def __repr__(self):
        return self.password

    def is_strong(self):
        raise NotImplementedError

    @classmethod
    def generate(cls, length, secure):
        alphabet = string.letters + string.digits
        if secure:
            alphabet += string.punctuation

        # Uses the os.urandom() function for random numbers generator source
        rand = SystemRandom()

        # Shuffle the alphabet a random number of times
        perm_list = list(alphabet)
        for i in xrange(rand.randint(128, 256)):
            rand.shuffle(perm_list)

        # Randomly choose the password in this alphabet
        password = ''.join(rand.sample(perm_list, length))

        return cls(password)
