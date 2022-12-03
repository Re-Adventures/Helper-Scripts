import subprocess
import telnetlib
import socket
import struct
import json
import sys

byte  = lambda v: struct.pack("<B", v)
word  = lambda v: struct.pack("<H", v)
dword = lambda v: struct.pack("<I", v)
qword = lambda v: struct.pack("<Q", v)

pattern  = ''.join([chr(x)*8 for x in range(0x41, 0x5B)])
pattern += ''.join([chr(x)*8 for x in range(0x61, 0x7B)])

pattern32  = ''.join([chr(x)*4 for x in range(0x41, 0x5B)]).encode()
pattern32 += ''.join([chr(x)*4 for x in range(0x61, 0x7B)]).encode()

def CreateFile(s=""):
  tmp = pattern
  if s:
    if isinstance(data, str):
      data = str(data).encode('charmap')
    tmp = s

  with open('tmp', 'wb') as fp:
    fp.write(tmp.encode())

  return tmp

def convert_to_bytes(data = ""):
  if not data:
    return b""

  if isinstance(data, int):
    data = str(data).encode('charmap')

  if not isinstance(data, bytes) and not isinstance(data, bytearray):
    data = data.encode('charmap')

  return data


class Remote:
  limit = None
  def __init__(this, host, port, limit=None):
    '''Initiates the connection'''
    this.conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    this.conn.connect((host, port))
    if limit:
      this.limit = limit

  def get(this, data):
    '''Used for receiving data'''
    data = convert_to_bytes(data)

    o = b''
    while 1:
      o += this.conn.recv(1)
      if data in o:
        return o

  def getline(this, data=""):
    this.get(convert_to_bytes(data) + b'\n')

  def put(this, data):
    '''Used for sending data'''
    this.conn.send(convert_to_bytes(data))

  def putline(this, data):
    this.put(convert_to_bytes(data) + b'\n')

  def json_send(this, v):
    request = json.dumps(v).encode('charmap')
    this.put(request)

  def json_recv(this, data):
    dat = this.get(data)
    return json.loads(dat.decode('charmap'))

  def interactive(this):
    '''Interactive shell'''
    t = telnetlib.Telnet()
    t.sock = this.conn
    if this.limit:
      t.timeout = this.limit
    t.interact()

  def terminate(this):
    '''Shutting down the connection'''
    this.conn.shutdown(socket.SHUT_RDWR)

class Local:
  def __init__(this, process):
    '''Starting the process'''
    this.proc = subprocess.Popen(process.split(), stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    this.stdin  = this.proc.stdin
    this.stdout = this.proc.stdout
    this.stderr = this.proc.stderr

  def get(this, data):
    '''Receiving data'''
    data = convert_to_bytes(data)

    o = b''
    while 1:
      this.stdout.flush()      # Might slow down the script
      o += this.stdout.read(1)
      if data in o:
        return o

  def getline(this, data=""):
    this.get(convert_to_bytes(data) + b'\n')

  def put(this, data):
    '''Sending data'''
    this.stdin.write(convert_to_bytes(data))
    this.stdin.flush()

  def putline(this, data):
    this.put(convert_to_bytes(data) + b'\n')

  def terminate(this):
    this.proc.terminate()


