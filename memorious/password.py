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

import string

from random import SystemRandom

class Password(object):
    def __init__(self, password):
        self.password = password

    def __repr__(self):
        return self.password

    def is_strong(self):
        raise NotImplementedError

    @classmethod
    def generate(cls, length, secure):
        alphabet = string.ascii_letters + string.digits
        if secure:
            alphabet += string.punctuation

        # Uses the os.urandom() function for random numbers generator source
        rand = SystemRandom()

        # Shuffle the alphabet a random number of times
        perm_list = list(alphabet)
        for i in range(rand.randint(128, 256)):
            rand.shuffle(perm_list)

        # Randomly choose the password in this alphabet
        password = ''.join(rand.sample(perm_list, length))

        return cls(password)
