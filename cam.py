import sys
from xml.dom import minidom#for svg
from svg.path import Path, Line, Arc, CubicBezier, QuadraticBezier, parse_path#for svg
import numpy as np#for stl


def TranslateSVG(inputname, settings):
	print("Translating from SVG")
	inputfile = minidom.parse(inputname)
	rawpaths = [path.getAttribute('d') for path in inputfile.getElementsByTagName('path')]
	inputfile.unlink()

	gcodepaths = [[]]

	for rawpath in rawpaths:
		path = parse_path(rawpath)
		for element in path:
			if(len(gcodepaths[-1]) != 0):
				if(gcodepaths[-1][-1] != (element.start.real, element.start.imag)):
					gcodepaths.append([])
					gcodepaths[-1].append((element.start.real, element.start.imag))
			else:
				gcodepaths[-1].append((element.start.real, element.start.imag))
			if(isinstance(element, Line)):
				gcodepaths[-1].append((element.end.real, element.end.imag))
			else:
				length = element.length()
				n = int(length // settings["segment length"]) + 1
				segprop = 1 / n
				for i in range(n):
					point = element.point(segprop*i)
					gcodepaths[-1].append((point.real, point.imag))
				gcodepaths[-1].append((element.end.real, element.end.imag))

	gcode = "G90\n"#sets absolute position mode
	gcode = gcode + "G92 X0 Y0 Z0\n"#sets current position to be the origin
	gcode = gcode + "G1 Z5 F" + settings["move speed"] + "\n"#moves, sets speed for current and future moves
	gcode = gcode + "M03 S" + settings["spindle speed"] + "\n"#sets spindle speed
	gcode = gcode + "\n"

	for gcodepath in gcodepaths:
		if(len(gcodepath) >= 2):
			gcode = gcode + "G1 X" + str(gcodepath[0][0]) + " Y" + str(gcodepath[0][1]) + "\n"
			gcode = gcode + "G1 Z" + settings["depth"] + " F" + settings["cut speed"] + "\n"
			for i in range(1,len(gcodepath)):
				gcode = gcode + "G1 X" + str(gcodepath[i][0]) + " Y" + str(gcodepath[i][1]) + "\n"
			gcode = gcode + "G1 Z" + "5" + " F" + settings["move speed"] + "\n"

	gcode = gcode + "M5\n"
	print("Done")
	return gcode


def TranslateSTL(inputname, settings):
	print("Translating from STL")
	print("WIP")
	print("Done")
	return ""


Settings = {
"misc":{},
"svg":{"depth":"-0.2", "cut speed":"200", "move speed":"500", "spindle speed":"1000", "segment length":1},
"stl":{"cut speed":"100", "spindle speed":"1000", "grid size":1}
}

if(len(sys.argv) >= 2):
	InputName = sys.argv[1]
else:
	InputName = input("File name? ")

splitname = InputName.split(".")
extension = splitname[-1].lower()
OutputName = "".join(element+"." for element in splitname[:-1]) + "nc"

if(extension == "svg"):
	GCode = TranslateSVG(InputName, Settings["svg"])
elif(extension == "stl"):
	GCode = TranslateSTL(InputName, Settings["stl"])
else:
	print("Extension not recognized")
	quit()

print("Writing to \"" + OutputName + "\"")
OutputFile = open(OutputName, "w")
OutputFile.write(GCode)
OutputFile.close()
print("Done")
