#!/usr/bin/python3
'''
    Client side for synchronizing pyboard's filesystem with current directory.
    Just upload boot.py to your board and run ./sync.py on computer.
'''
import pyboard
import os
import codecs
import time
from sh import pkill
from hashlib import sha256

def log(text):
    for line in text.decode('ascii').strip().split("\n"):

        if line.startswith('#'):
             # Skip flow commands
             continue

        print(line)

def copy(filename):
    data = open(filename, 'r').read().encode('ascii')
    length = str(len(data)).encode('ascii')
    data_hash = sha256(data).hexdigest()

    p.serial.write(b"#CONTENT\n" + length + b"\n" + \
                   data_hash.encode('ascii') + b"\n" + \
                   filename.encode('ascii') + b"\n")
    p.serial.flush()

    while data:
        to_write = data[:1000]
        data = data[1000:]
        p.serial.write(to_write)
        p.serial.flush()

    log(p.read_until(1, b"#DONE\n"))

device = '/dev/ttyACM0'

try:
    # Close all processes talking to such device
    pkill("-f", device)
except:
    pass

p = pyboard.Pyboard(device)

p.serial.write(b'\r\x03\x03') # ctrl-C twice: interrupt any running program
p.serial.write(b'\x04') # ctrl-D: soft reset

log(p.read_until(1, b"#READY TO UPLOAD\n"))

for f in os.listdir('.'):
    if not f.endswith('.py'):
        continue

    copy(f)

p.serial.write(b'\x04') # ctrl-D: soft reset
