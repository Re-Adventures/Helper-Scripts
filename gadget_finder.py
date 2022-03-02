#!/usr/bin/python3
import distorm3
import sys
import subprocess
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
  print(tmp)
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


# TODO: Need to implement
def check_interesting(lst):
  pass


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
      check_interesting(tmp2)
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

  for i, j, k in zip(offsets, gadgets, gadgets2):
    # Removing gadgets that only have one instruction i.e just ret instruction
    if len(j.splitlines()) == 1:
      continue
    print('-' * width)
    print_green("Offset: %s" % i)
    print(j)
    print()
    print(i, k)
    to_write += f"{i} {k}\n"
    if check_interesting(k):
      interesting_gadgets.append(f"{i} {k}\n")
    print()
    gad_count += 1

  print_green("Total %i gadgets found" % gad_count)
  print_yellow('Gadgets also written to "gadgets.asm" file')

  with open("gadgets.asm", "w") as fp:
    fp.write(("Total %i gadgets found\n" % gad_count) + to_write)

