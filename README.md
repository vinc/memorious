Memorious
=========

Memorious is a simple CLI to manage website accounts writen in Python (>= 2.7).

Memorious is using a SQLite database in memory to store website accounts 
when it is running and otherwize an encrypted dump is stored on the disk
using AES, a block cipher encryption algorithm, operating in cipher feedback
(CFB) mode. This algorithm is implemented by PyCrypto.

Your website accounts should be safe when Memorious is not running and if your
key file is stored on a removable media (and backed up somewhere else).

This project is very new so feel free to review the source code.

Installation
------------

Installing from source: `git clone git://github.com/vinc/memorious.git; cd memorious; python setup.py install`

Usage
-----

To use memorious you will need a key file generated by:

    $ memorious new

By default an AES 256 bits key is generated inside a 1024 bits file
located in /tmp/memorious.key.

With this key file any one can read all your website account and without
it obviously no one can, not even you. So take car of this file and move
it to somewhere safe before your next reboot.


Storing a new password is easy:

    $ memorious put --domain example.org --username bob               
    Your password is: gdMPKLIJvWCZEnGS

A new password will be generated using /dev/urandom on UNIX-like system
and CryptGenRandom on Windows. You can also use '--password foo' to use
'foo' as a password or '--password' without argument to get a prompt to
type it without echoing.

Optionnal arguments allow to choose the password lenght or make it more
secure by adding punctuation: !"#$%&\'()*+,-./:;<=>?@[\\]^_`{|}~

The database dump is stored on an encypted file in ~/.memorious/store.dump by
default.


Listing website accounts use the same arguments:

    $ memorious get --domain example.org --username bob  
    Ids  Domains                   Usernames                 Passwords                

    1    example.org               bob                       H7Q2qZN6cjxvTase         

    $ memorious get --domain example.org               
    Ids  Domains                   Usernames                 Passwords                

    1    example.org               bob                       H7Q2qZN6cjxvTase         
    2    example.org               alice                     qkUJ3WIV08ERGLov         

    $ memorious get --username bob 
    Ids  Domains                   Usernames                 Passwords                

    1    example.org               bob                       H7Q2qZN6cjxvTase         
    3    test.com                  bob                       oYf9XNKe3B4U6QTV         

    $ memorious get               
    Ids  Domains                   Usernames                 Passwords                

    1    example.org               bob                       H7Q2qZN6cjxvTase         
    2    example.org               alice                     qkUJ3WIV08ERGLov         
    3    test.com                  bob                       oYf9XNKe3B4U6QTV


Finally you can delete a row by its id:

    $ memorious del 2

Or a list of row:

    $ memorious del $(seq 1 10)
