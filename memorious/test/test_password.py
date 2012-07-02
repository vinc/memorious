import string
import unittest

from memorious.password import Password

class TestPassword(unittest.TestCase):

    def test_init(self):
        self.assertEqual(str(Password('quo8daehaen1Uba')), 'quo8daehaen1Uba')

    def test_generate(self):
        for n in [7, 16, 20]:
            # Alphanumeric characters
            alphabet = string.ascii_letters + string.digits
            password = str(Password.generate(n, False))
            self.assertEqual(len(password), n)
            self.assertTrue(password.isalnum())
            self.assertTrue(all(c in alphabet for c in password))

            # Alphanumeric characters with punctuation symbols
            alphabet += string.punctuation
            password = str(Password.generate(n, True))
            self.assertEqual(len(password), n)
            self.assertTrue(all(c in alphabet for c in password))

if __name__ == '__main__':
    unittest.main()
