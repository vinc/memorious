Memorious
=========

Minimalist command line password manager.


Synopsis
--------

Memorious is using a SQLite database in memory to store website accounts 
when it is running and otherwise an encrypted SQL dump is stored on the disk
using AES, a block cipher encryption algorithm, operating in cipher feedback
(CFB) mode. This algorithm is implemented by PyCrypto.

Your website accounts should be safe when Memorious is not running and if your
key file is stored on multiple removable media.

This project is not mature yet so feel free to review the source code before
using it seriously. Fortunately it is less than 300 lines of Python code ;)


Installation
------------

To install Memorious from source:

    $ git clone git://github.com/vinc/memorious.git
    $ cd memorious
    $ python setup.py install


Usage
-----

Start by generating a new key file:

    $ memorious new

By default an AES 256 bits key is generated inside a 1024 bits file
located in `/tmp/memorious.key`.

Note that with this key file anyone can read all your accounts and without
it obviously no one can, not even you. So take care of this file and move
it to somewhere safe before your next reboot.


Storing a new account is easy:

    $ memorious put --domain example.org --username bob               
    Your password is: gdMPKLIJvWCZEnGS

A new password will be generated using `/dev/urandom` on UNIX-like system
and `CryptGenRandom` on Windows. You can also use `--password foo` to set
`foo` as a password or `--password` without argument to get a prompt for
typing it without echoing.

Some optional arguments allow to specify the password length or make it
more secure by adding punctuation characters.

The database is stored in an encrypted SQL text format saved by default in
`~/.memorious/store.mem` along with the initialization vector (IV) used by
the encryption algorithm.


The same arguments work for listing accounts:

    $ memorious get               
    Ids  Domains      Usernames  Passwords         Comments       
    -------------------------------------------------------
    1    example.org  bob        H7Q2qZN6cjxvTase         
    2    example.org  alice      qkUJ3WIV08ERGLov         
    3    test.com     bob        oYf9XNKe3B4U6QTV

    $ memorious get --domain example.org               
    Ids  Domains      Usernames  Passwords         Comments       
    -------------------------------------------------------
    1    example.org  bob        H7Q2qZN6cjxvTase         
    2    example.org  alice      qkUJ3WIV08ERGLov         

    $ memorious get --domain example.org --username bob  
    Ids  Domains      Usernames  Passwords         Comments       
    -------------------------------------------------------
    1    example.org  bob        H7Q2qZN6cjxvTase         


Finally you can delete a single row by its id:

    $ memorious del 2

Or a list of rows:

    $ memorious del $(seq 1 10)


Try `memorious --help` for advanced options.


License
-------

Copyright (C) 2010-2013 Vincent Ollivier. Released under GNU GPL License v3.
