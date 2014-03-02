Memorious
=========

Minimalist command line password manager.


Synopsis
--------

Memorious 2.0 is now just a shell script around common UNIX commands.


Installation
------------

To install Memorious from source:

    $ git clone git://github.com/vinc/memorious.git -b shell
    $ sudo cp memorious/memorious.sh /usr/local/bin/memorious2
    $ sudo chmod 555 /usr/local/bin/memorious2


Usage
-----

Start by generating a new key file:

    $ memorious2 new

By default a key file named `memorious.key` and a flat file database
named `memorious.mem` are generated in `~/.memorious`.

The database is encrypted in AES 256-bit CBC-mode with the 256-bit key file
generated from `/dev/urandom` and a random salt by OpenSSL.


License
-------

Copyright (C) 2010-2014 Vincent Ollivier. Released under GNU GPL License v3.
