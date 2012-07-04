import os
import string
import unittest

from tempfile import NamedTemporaryFile

from memorious.keyfile import KeyFile
from memorious.store import Store

class TestStore(unittest.TestCase):

    def setUp(self):
        self.default_key_size = 256 # bits
        self.default_algorithm = 'aes'

        # Set up KeyFile
        with NamedTemporaryFile() as f:
            self.key_file = f.name
        self.assertFalse(os.path.exists(self.key_file))
        KeyFile.generate(self.key_file)
        self.assertTrue(os.path.exists(self.key_file))

        # Set up Store
        with NamedTemporaryFile() as f:
            self.mem_file = f.name
        self.assertFalse(os.path.exists(self.mem_file))
        self.config = {
            'mem_file': self.mem_file,
            'key_file': self.key_file,
            'key_size': self.default_key_size,
            'algorithm': self.default_algorithm
        }

    def tearDown(self):
        for path in [self.mem_file, self.key_file]:
            if os.path.exists(path):
                os.unlink(path)

    def test_init(self):
        store = Store(**self.config)
        self.assertFalse(store.closed)

        self.config['algorithm'] = 'des'
        with self.assertRaises(NotImplementedError):
            Store(**self.config)

        del self.config['key_size']

        self.config['algorithm'] = 'aes'
        for n in range(512):
            if n not in [128, 192, 256]:
                with self.assertRaises(ValueError):
                    Store(key_size=n, **self.config)

        self.config['algorithm'] = 'blowfish'
        for n in range(512):
            if not 32 <= n <= 448:
                with self.assertRaises(ValueError):
                    Store(key_size=n, **self.config)

    def test_open(self):
        with Store.open(**self.config) as store:
            self.assertFalse(store.closed)

    def test_put(self):
        for cipher in ['aes', 'blowfish']:
            self.config['algorithm'] = cipher
            with Store.open(**self.config) as store:
                fields = {
                    'domain': 'example.org',
                    'username': 'bob',
                    'password': 'secret',
                    'comment': 'test account'
                }
                store.put(**fields)
                accounts = list(store.get(**fields))
                self.assertEqual(len(accounts), 1)
                for account in accounts:
                    for k in fields.keys():
                        self.assertEqual(account[k], fields[k])

                fields = {
                    'domain': 'example.org',
                    'username': 'alice',
                    'password': 'secret'
                }
                store.put(**fields)
                accounts = list(store.get(**fields))
                self.assertEqual(len(accounts), 1)
                for account in accounts:
                    for k in fields.keys():
                        self.assertEqual(account[k], fields[k])
                    self.assertIsNone(account['comment'])

                fields = {
                    'domain': 'test.org',
                    'username': 'bob',
                    'password': 'secret'
                }
                store.put(**fields)

                self.assertEqual(len(list(store.get())), 3)
                self.assertEqual(len(list(store.get(domain='example.org'))), 2)
                self.assertEqual(len(list(store.get(username='bob'))), 2)
                self.assertEqual(len(list(store.get(username='alice'))), 1)

            os.unlink(self.mem_file)

    def test_get(self):
        db = [
            {
                'domain': 'example.org',
                'username': 'bob',
                'password': 'secret',
                'comment': 'test account'
            },
            {
                'domain': 'example.org',
                'username': 'alice',
                'password': 'secret'
            },
            {
                'domain': 'test.org',
                'username': 'bob',
                'password': 'secret'
            }
        ]

        for cipher in ['aes', 'blowfish']:
            self.config['algorithm'] = cipher

            # Create memorious file loaded with accounts
            with Store.open(**self.config) as store:
                for fields in db:
                    store.put(**fields)

            # Open and read memorious file
            with Store.open(**self.config) as store:
                accounts = list(store.get())
                self.assertEqual(len(accounts), len(db))
                for i, account in enumerate(accounts):
                    fields = db[i]
                    fields['id'] = i + 1
                    for k in fields.keys():
                        self.assertEqual(account[k], fields[k])
                    for k in (k for k in account.keys() if k not in fields.keys()):
                        self.assertIsNone(account[k])
            
            os.unlink(self.mem_file)


if __name__ == '__main__':
    unittest.main()