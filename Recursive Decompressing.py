#PLEASE Make copy of files inside the directory you're using this script on.
import os
ignore = ['Recursive Decompressing.py'] # change
otherFiles = []
while 1:
	temp = os.listdir()  # listing all files in current directory
	files = []
	for x in temp:
		if x not in ignore:
			files.append(x)  # creating list of files to be unpacked
	if not files:
		break              # if all files have been decompressed
	else:
		for i in files:
			ignore.append(i)
			res = os.system('file ' + i).read()
			if res.lower() in types:
				os.system('7z -y e ' + i).read()
			else:
				otherFiles.append(res)
if otherFiles:
	print('Other file types in this directory')
		for x in otherFiles:
			print(x)
print("------------------------DONE------------------------")
