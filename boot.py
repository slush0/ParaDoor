'''
    Boot script listen on USB VCP for filesystem updates.
    See ./sync.py for client-side application for uploading files.
'''
import pyb
import os
from hashlib import sha256
from binascii import hexlify

def read_file():
    data = u.recv(9, timeout=100)
    if not data or data != b"#CONTENT\n":
        return False

    try:
        size = int(u.readline())
        sent_hash = u.readline().strip().decode('ascii')
        filename = u.readline().strip().decode('ascii')

        data = u.recv(size, timeout=1000)
        data_hash = hexlify(sha256(data).digest()).decode('ascii')

        print(filename, end=": ")

        try:
            content = open(filename, 'r').read()
            file_hash = hexlify(sha256(content).digest()).decode('ascii')
        except OSError:
            file_hash = ''
            print("File not found")

        if data_hash != sent_hash:
            # File is corrupted
            print("File is corrupted")

            u.send("#DONE\n")
            return True

        if data_hash == file_hash:
            # File is unchanged
            print ("File is unchanged")

            u.send("#DONE\n")
            return True

        f = open(filename, 'w')
        f.write(data) 
        f.flush()
        f.close()

        print("File is UPDATED")

    except Exception as e:
        f = open('error.log', 'a')
        f.write(str(e.args)) 
        f.flush()
        f.close()

        for x in range(3):
            pyb.LED(3).toggle()
            pyb.delay(100)

    u.send("#DONE\n")
    return True

pyb.LED(3).on()
u = pyb.USB_VCP()
u.send(b"#READY TO UPLOAD\n", timeout=200)

while read_file():
    pass

if pyb.Switch()():
    pyb.usb_mode('CDC+MSC') # act as a serial and a storage device
else:
    pyb.usb_mode('CDC+HID') # act as a serial device and a mouse

os.sync()

pyb.LED(3).off()
