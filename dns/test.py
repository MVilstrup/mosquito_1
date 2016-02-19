#!/usr/bin/env python
# coding: utf-8

import socket


print("The domain name you want the IP Address for:")
while True:
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect(("", 1112))
    text = raw_input(b">> ")
    s.send(text)
    s.close()
# file_name = 'data/%s' % (file_name, )
# r = s.recv(9999999)
# with open(file_name, 'wb') as _file:
#     _file.write(r)
# print("The file was copied to: %s." % file_name)
