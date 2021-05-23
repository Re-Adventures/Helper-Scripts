import socket
import telnetlib
import json
import sys
import hashlib
import time

Host, Port = '', 1000

byte  = lambda v: struct.pack("<B", v)
word  = lambda v: struct.pack("<H", v)
dword = lambda v: struct.pack("<I", v)
qword = lambda v: struct.pack("<Q", v)

pattern = lambda: ''.join([chr(x)*8 for x in range(0x41, 0x5B)])

# Interactive shell
def interact():
  t = telnetlib.Telnet()
  t.sock = s
  t.interact()

# Terminating connection
def terminate():
  s.shutdown(socket.SHUT_RDWR)

def json_recv(v):
  data = get(v)
  return json.loads(data.decode())

def json_send(v):
  request = json.dumps(v).encode()
  put(request)

# Receiving data
def get(v):
  if not isinstance(v, bytes) and not isinstance(v, bytearray):
    v = v.encode('charmap')

  o = b''
  while 1:
    o += s.recv(1)
    if v in o:
      return o

# Sending data
def put(v):
  if isinstance(v, int):
    v = str(v)
  if not isinstance(v, bytes) and not isinstance(v, bytearray):
    v = v.encode('charmap')

  s.send(v + b'\n')

def connect(timeout=0):
  s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
  s.connect((Host, Port))
  if timeout:
    s.settimeout(timeout)

connect()

# Code here

interact()
# terminate()
