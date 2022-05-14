#!/usr/bin/python3
import distorm3
import sys
import subprocess
import re
import os

# We can manually set it too
MODE = None  # "32" or "64"
START = None # Start of text section or executable section
END = None   # End of text section or executable section
VA = None

if VA: # If VA is manually set
  VA -= START

def set_mode():
  # Getting the arch of file
  # Currently can be 32bit or 64bit
  global MODE
  P = subprocess.Popen(["file", fname], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
  ret, _ = P.communicate()
  ret = ret.decode('charmap')
  # ret = ret.replace('; ', ',').split(',')

  # input(ret)
  if "ELF" not in ret:
    return None
  MODE = ret.split("ELF ")[1].split("-bit")[0]
  if "32" == MODE:
    print_green("Mode: 32-bits\n")
    MODE = distorm3.Decode32Bits

  if "64" == MODE:
    print_green("Mode: 64-bits\n")
    MODE = distorm3.Decode64Bits

# Getting Virtual Address and File offset of .text section
def get_offsets():
  global START
  global END
  global VA
  P = subprocess.Popen(["readelf", "-SW", fname], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
  ret, _ = P.communicate()
  ret = ret.decode('charmap')

  # ret = subprocess.getoutput(f"readelf -SW {fname}")
  ret = ret.replace("[ ", "[").splitlines()
# 0x011d0
# 0x03d71
  for i in range(len(ret)):
    if ".text" in ret[i]:
      START = ret[i] # Start of text section
      END = ret[i+1] # End of text section
      # print(START)
      # print(END)
      break

  START = START.strip()
  # input(START)
  tmp = START.split()
  # print(tmp)
  # input(tmp)
  START, VA = int(tmp[4], 16), int(tmp[3], 16)

  # This is because when calculating again, it adds the START again
  VA -= START

  END = END.strip()
  tmp = END.split()
  END = int(tmp[4], 16)

  print_green(f"START: {VA + START:#010x}")
  print_green(f"END: {VA + END:#010x}")
  print_green(f"VA: {VA:#010x}")


def MakeFunction(address, inst, pattern):
  if distorm3.Decode32Bits == MODE:
    decoding = "dword"
  if distorm3.Decode64Bits == MODE:
    decoding = "qword"

  regs = ""
  toWrite = f"#{address} {inst}\n"

  if "pop" in pattern:
    # Scarry string parsing
    funcName = '_'.join(''.join(inst.split("; ")).split("pop ")[1:]).replace("ret", "")
    regs = funcName.split("_")

    params = ''.join([f"{i} = 0, " for i in regs])[:-2]

    toWrite += f"def pop_{funcName}({params}):\n"

  elif "mov " in pattern:
    inst = inst.replace("; ret", "").replace("mov ", "")
    inst = inst.replace("[", "").replace("]", "")
    inst = inst.split(", ")

    funcName = '_'.join(inst)

    toWrite += f"def write_into_{funcName}():\n"
    print(toWrite)

  else:
    return ""

  toWrite += f"  return {decoding}({address[:-1]})"

  if regs:
    for reg in regs:
      toWrite += f" + {decoding}({reg})"

  return toWrite

uniq = []
def check_interesting(address, inst):
  inst = inst.lower()
  if inst in uniq:
    return False

  patterns32Bit = ["(pop e.*?; )+ret", "(push e.*?; )+ret", "mov \[e\w+\], e..; ret"]
  patterns64Bit = ["(pop r\w+; )+ret", "(push r\w+; )+ret", "mov \[r\w+\], [r,e]\w+; ret"]

  if distorm3.Decode32Bits == MODE:
    patterns = patterns32Bit
  elif distorm3.Decode64Bits == MODE:
    patterns = patterns64Bit

  if not patterns:
    return None

  for pattern in patterns:
    if re.match(pattern, inst):
      uniq.append(inst)
      return MakeFunction(address, inst, pattern)

def get_gadgets():
  gadget = []
  gadget2 = []
  interesting_gadgets = []
  # chain = []
  off = [] # address of gadget
  for i in range(START, END):
    lst1 = []
    lst2 = []
    flag = 0
    # change i+20 if gadgets not found
    decoded = distorm3.Decode(VA+i, data[i:i+20], MODE)
    addr = []
    inst = []
    for x in decoded:
      addr.append(x[0])
      inst.append(x[2])
    for x, y in zip(inst, addr):
      lst1.append("0x%.4x:  %s" % (y, x))
      lst2.append(x)
      if "RET" in x:
        flag = 1
        break
    if flag:
      tmp = "\n".join(lst1)
      tmp2 = "; ".join(lst2)
      if "DB " in tmp:   # If the disassembly process failed
        continue
      if tmp in gadget:  # Checking if its not already found
        continue
      off.append(lst1[0].split()[0])
      gadget.append(tmp)
      gadget2.append(tmp2) # gadgets in a single line

  return off, gadget, gadget2

def print_red(s):
  print(f"\x1b[31m[!] {s}\x1b[0m")

def print_green(s):
  print(f"\x1b[32m[*] {s}\x1b[0m")

def print_yellow(s):
  print(f"\x1b[33m[*] {s}\x1b[0m")

if  '__main__' == __name__:
  if len(sys.argv) != 2:
    print_red("Input file not provided. Exiting")
    print_green(f"Usage: ./{__file__} <binary>")
    exit()

  fname = sys.argv[1]

  if not MODE:
    print_yellow("Finding Mode")
    set_mode()

  if not MODE:
    print_red("ERROR: Unknown Architecture\nThis tool currently supports only ELF Files")
    exit()

  if not START or not END:
    print_yellow("Find the START and END offsets")
    get_offsets()

  # input()
  with open(fname, "rb") as fp:
    data = fp.read()

  # gadgets is multilined output, gadgets2 is single line output
  offsets, gadgets, gadgets2 = get_gadgets()
  gad_count = 0
  to_write = ''

  width = os.get_terminal_size()[0]
  interesting_gadgets = []

  # Dynamically create python functions
  FunctionForROP = ['''import struct
byte  = lambda v: struct.pack("<B", v)
word  = lambda v: struct.pack("<H", v)
dword = lambda v: struct.pack("<I", v)
qword = lambda v: struct.pack("<Q", v)''']

  for address, j, k in zip(offsets, gadgets, gadgets2):
    # Removing gadgets that only have one instruction i.e just ret instruction
    if len(j.splitlines()) == 1:
      continue
    print('-' * width)
    print_green("Offset: %s" % address)
    print(j)
    print()
    print(address, k)
    to_write += f"{address} {k}\n"
    funcDef = check_interesting(address, k)
    if funcDef:
      FunctionForROP.append(funcDef)
      interesting_gadgets.append(f"{address} {k}")
    print()
    gad_count += 1

  print_green("Total %i gadgets found" % gad_count)
  print_yellow('Gadgets also written to "gadgets.asm" file')

  with open("gadgets.asm", "w") as fp:
    fp.write("# File auto generated by gadget_finder (https://github.com/DaBaddest/Helper-Scripts/edit/master/gadget_finder.py)\n")
    fp.write("# Author DaBaddest\n")
    fp.write(("Total %i gadgets found\n" % gad_count) + to_write)

  if len(FunctionForROP) > 5:
    print_yellow('Writing Useful Function to "usefulFunction.py" file')
    with open("usefulFunction.py", 'w') as fp:
      fp.write("# File auto generated by gadget_finder (https://github.com/DaBaddest/Helper-Scripts/edit/master/gadget_finder.py)\n")
      fp.write("# Author DaBaddest\n")
      fp.write('\n\n'.join(FunctionForROP) + "\n\n")


  if interesting_gadgets:
    print_yellow("****List Of Interesting Gadgets****")
    for i in interesting_gadgets:
      print_green(i)
