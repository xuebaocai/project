# -*- coding=utf-8 -*-


"""

file: send_img.py
socket client
11/25 11:10
"""
import socket
import os
import sys
import struct

def socket_client():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect(('10.164.18.203', 6666))
    except socket.error as msg:
        print(msg)
        sys.exit(1)
    print(s.recv(1024).decode("utf-8"))

    while 1:
        filepath = '/home/mengjun/data/VOCdevkit/MyDataSet/JPEGImages/1.jpg'
        if os.path.isfile(filepath):
            # 定义定义文件信息。128s表示文件名为128bytes长，l表示一个int或log文件类型，在此为文件大小
            fileinfo_size = struct.calcsize('128sl')
            # 定义文件头信息，包含文件名和文件大小
            fhead = struct.pack(
                '128sl',
                os.path.basename(filepath).encode(encoding="utf-8"),
                os.stat(filepath).st_size
            )
            print('client filepath: {0}'.format(filepath))
            s.send(fhead)
            fp = open(filepath, 'rb')
            while 1:
                data = fp.read(1024)
                if not data:
                    print('{0} file send over...'.format(filepath))
                    break
                s.send(data)
        print(s.recv(1024).decode("utf-8"))
        print(s.recv(1024).decode("utf-8"))
        s.close()
        break

if __name__ == '__main__':
    socket_client()
