gweb2py
=======

A web2py editor. It is a highly experimental editor/ide for web2py.
Q: Why I made it?
A: First, I am a vim addicted, a console guy and a Linux user, but
I was feeling lost editing all the files need it for web development.

So I need a solution, and quickly.
I want to continue using vim to edit my files, I want something
that did not change my way of doing it.

So gweb2py is a simple editor/ide with a messy/shitty code (you been warned).
But I need something quickly, so I start coding like a monkey without
design it first and without any care about the design.


Running
=======

    $ cd to_gweb2py_dir
    $ ./gweb2py /path/to/web2py_folder

it will then ask you the web2py admin pass.
the webserver runs on port 8000


Main Features
=============
    - Own httpserver (single process/thread)
    - debugger
    - logs http request with different colours
    depending on http status code
    - logs full http request and response
    - web2py tracebacks available without
    the need to open web2py admin.
    - vim has the editor. it is vim not gvim embedded.
    - image viewer

    - In mac/windows the editor is a basic scintilla control.
    (But I do not know if gweb2py works in this platforms.)


Requirements
============

- Linux:
    - Python 2.6 (probably will work with 2.5)
    - wxPython 2.8
    - python-vte
    - vim

    I am using it in Ubuntu 10.04.

- Mac/Windows (I do not even no if it will work on this platforms):

    - Python 2.6 (probably will work with 2.5)
    - wxPython 2.8



vim configuration
=================

You can have whatever configuration you want.
I am using the following vim plugins:
 - pathogen
 - snipmate
 - supertab
 - pep8

Instructions to install them are in the  excelent John Anderson article:
http://sontek.net/turning-vim-into-a-modern-python-ide


Note
====
Most likely I will not put much more efforts on this, I do not have
the motivation or time to do it.


