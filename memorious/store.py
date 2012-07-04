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

import os
import string
import sqlite3

from random import SystemRandom

# self._algo must be a block cipher encryption algorithm
# capable of operating in cipher feedback (CFB) mode
# Supported algorithms: AES, Blowfish, DES...
from Crypto.Cipher import AES

from memorious.keyfile import KeyFile

class Store(object):
    """Manage an encrypted passwords database."""

    def __init__(self, mem_file, key_file, key_size=256, algorithm='aes'):
        """Restore in memory database from memorious file.

        Keyword arguments:
        mem_file -- the memorious file path
        key_file -- the key file path
        key_size -- the key size (128, 192 or 256 bits for AES)
        cipher   -- the cipher name (aes)
        """

        self._mem = mem_file
        self._key = KeyFile(key_file, key_size).key

        if algorithm == 'aes':
            if key_size not in [128, 192, 256]:
                raise ValueError
            self._algo = AES
        else:
            raise NotImplementedError

        self.closed = False

        # Create a database in memory
        self._con = sqlite3.connect(':memory:')
        if not os.path.isfile(self._mem):
            self._con.execute("""
                CREATE TABLE slots(
                    id INTEGER PRIMARY KEY,
                    domain,
                    username,
                    password,
                    comment
                );
                """)
            return

        # Decrypt SQL text contained in memorious file
        sql = ''
        with open(self._mem, 'rb') as f:
            # Retrieve the initialization vector (IV) transmitted along
            # with the ciphertext
            iv = f.read(self._algo.block_size)

            # Retreive and decrypt the ciphertext
            cipher = self._algo.new(self._key, self._algo.MODE_CFB, iv)
            while True:
                block = f.read(self._algo.block_size)
                if not block:
                    break
                sql += cipher.decrypt(block).decode()

        # Restore previous database
        self._con.executescript(sql)

    @classmethod
    def open(cls, **args):
        return cls(**args)

    def get(self, **fields):
        """Generate rows matching fields in the accounts table."""
        self._con.row_factory = sqlite3.Row
        query = 'SELECT * FROM slots'
        values = [v for v in fields.values() if v]
        if values:
            keys = (k for k in fields.keys() if fields[k])
            query += ' WHERE %s' % ' AND '.join('%s=?' % k for k in keys)
        for row in self._con.execute(query, values):
            yield row

    def put(self, **fields):
        """Add a new row in the accounts table."""
        assert ''.join(fields.keys()).isalpha()
        q_cols = ', '.join(fields.keys())
        q_vals = ', '.join('?' * len(fields))
        query = "INSERT INTO slots (%s) values (%s)" % (q_cols, q_vals)
        self._con.execute(query, list(fields.values()))

    def delete(self, id):
        """Remove a row from the accounts table."""
        self._con.execute('DELETE FROM slots WHERE id=?', (id,))

    def close(self):
        if self.closed:
            return

        # Dump database in SQL text format
        sql = ''.join(self._con.iterdump())

        # Write encrypted dump to temporary file
        randname = ''.join(SystemRandom().sample(string.ascii_lowercase, 8))
        tmp = '%s/%s.mem' % (os.path.dirname(self._mem), randname)

        flags = os.O_WRONLY | os.O_CREAT | os.O_TRUNC
        if os.name == 'nt':
            flags = flags | os.O_BINARY
        with os.fdopen(os.open(tmp, flags, 0o600), 'wb') as f:
            n = self._algo.block_size

            # CFB mode require an initialization vector (IV) which must
            # be unpredictable. The same IV will be used to encrypt a
            # plaintext and decrypt the corresponding ciphertext.
            iv = os.urandom(n)

            # IV need not to be secret, so it is transmitted along with
            # the ciphertext.
            f.write(iv)

            cipher = self._algo.new(self._key, self._algo.MODE_CFB, iv)
            for i in range(0, len(sql), n):
                # Each block of plaintext is encrypted and written to
                # the persistent storage file.
                f.write(cipher.encrypt(sql[i:i+n]))

            # Write to disk
            f.flush()
            os.fsync(f.fileno())

        # Backup old memorious file
        is_new = not os.path.exists(self._mem)
        if not is_new:
            os.rename(self._mem, self._mem + '~')

        # Replace old memorious file
        os.rename(tmp, self._mem)

        # Delete backup
        if not is_new:
            os.unlink(self._mem + '~')

        self.closed = True

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        if type is None:
            self.close()
        else:
            # An exception occurred. Any changes in the database should be
            # considered lost and not saved into the memorious file.
            self.closed = True
