import os
import string
import unittest

from tempfile import NamedTemporaryFile

from memorious.keyfile import KeyFile

class TestKeyFile(unittest.TestCase):

    def setUp(self):
        self.default_key_size = 256 # bits
        self.default_file_size = 1024 # bits

    def test_init(self):
        self.assertEqual(KeyFile('test').path, 'test')
        self.assertEqual(KeyFile('test').size, self.default_key_size)
        self.assertEqual(KeyFile('test', 128).size, 128)

    def test_key(self):
        key = os.urandom(self.default_key_size // 8)
        pad_size = self.default_file_size - self.default_key_size
        pad = os.urandom(pad_size // 8)
        with NamedTemporaryFile() as f:
            f.write(key)
            f.write(pad)
            f.flush()
            key_file = KeyFile(f.name)
            self.assertEqual(len(key_file.key), self.default_key_size // 8)
            self.assertEqual(key_file.key, key)

    def test_generate(self):
        with NamedTemporaryFile() as f:
            path = f.name
            with self.assertRaises(IOError):
                KeyFile.generate(path)
        self.assertFalse(os.path.exists(path))
        key_file = KeyFile.generate(path)
        self.assertTrue(os.path.exists(path))

        n = self.default_key_size // 8
        self.assertEqual(len(key_file.key), n)
        with open(path, 'rb') as f:
            content = f.read()
            self.assertEqual(len(content), self.default_file_size // 8)
            self.assertEqual(key_file.key, content[:n])

        os.unlink(path)

if __name__ == '__main__':
    unittest.main()
