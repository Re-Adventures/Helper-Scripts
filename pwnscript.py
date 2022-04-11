#!/usr/bin/python3
import subprocess
import telnetlib
import socket
import struct
import json
import sys

Host, Port = '127.0.0.1', 1234
process = 'a.exe'

byte  = lambda v: struct.pack("<B", v)
word  = lambda v: struct.pack("<H", v)
dword = lambda v: struct.pack("<I", v)
qword = lambda v: struct.pack("<Q", v)

pattern =  ''.join([chr(x)*8 for x in range(0x41, 0x5B)]).encode()
pattern += ''.join([chr(x)*8 for x in range(0x61, 0x7B)]).encode()

pattern32 =  ''.join([chr(x)*4 for x in range(0x41, 0x5B)]).encode()
pattern32 += ''.join([chr(x)*4 for x in range(0x61, 0x7B)]).encode()


def CreateFile(data=""):
  tmp = pattern
  if data:
    if isinstance(data, str):
      data = str(data).encode('charmap')
    tmp = data

  with open('tmp', 'wb') as fp:
    if isinstance(tmp, str):
      tmp = tmp.encode()
    fp.write(tmp)

  return tmp


class Remote:
  def __init__(this):
    '''Initiates the connection'''
    this.conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    this.conn.connect((Host, Port))

  def get(this, data):
    '''Used for receiving data'''

    # Some checks to convert the data to bytes
    if isinstance(data, int):
      data = str(data).encode('charmap')

    if not isinstance(data, bytes) and not isinstance(data, bytearray):
      data = data.encode('charmap')

    # TODO: Implement timeout mechanism
    o = b''
    while 1:
      o += this.conn.recv(1)
      if data in o:
        return o

  def put(this, data):
    '''Used for sending data'''

    # TODO: Implement timeout mechanism
    # TODO: Logging Mechanisms

    # Some checks to convert the data to bytes before sending
    if isinstance(data, int):
      data = str(data).encode('charmap')

    if not isinstance(data, bytes) and not isinstance(data, bytearray):
      data = data.encode('charmap')

    # TODO: Implement timeout mechanism
    this.conn.send(data)

  def json_send(this, v):
    # TODO: Logging Mechanisms
    request = json.dumps(v).encode('charmap')
    this.put(request)

  def json_recv(this, data):
    dat = this.get(data)
    return json.loads(dat.decode('charmap'))

  def interact(this):
    '''Interactive shell'''
    t = telnetlib.Telnet()
    t.sock = this.conn
    t.interact()

  def terminate(this):
    '''Shutting down the connection'''
    this.conn.shutdown(socket.SHUT_RDWR)

class Local:
  def __init__(this):
    '''Starting the process'''
    this.proc = subprocess.Popen(process.split(), stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    this.stdin  = this.proc.stdin
    this.stdout = this.proc.stdout
    this.stderr = this.proc.stderr


  def get(this, data):
    '''Receiving data'''
    # TODO: Implement timeout mechanism
    # Flush might be required
    if isinstance(data, int):
      data = str(data).encode('charmap')

    if not isinstance(data, bytes) and not isinstance(data, bytearray):
      data = data.encode('charmap')

    o = b''
    while 1:
      this.stdout.flush()      # Might slow down the script
      o += this.stdout.read(1)
      if data in o:
        return o

  def put(this, data):
    '''Sending data'''
    # TODO: Implement timeout mechanism
    # Dont forget to flush data
    if isinstance(data, int):
      data = str(data).encode('charmap')

    if not isinstance(data, bytes) and not isinstance(data, bytearray):
      data = data.encode('charmap')

    this.stdin.write(data)
    this.stdin.flush()

  def terminate(this):
    this.proc.terminate()
