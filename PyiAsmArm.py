import os
import sys

class malloc:
	def __init__(self, sz):
		assert (sz > 0), "Memory size can't be 0 or less"
		self.size = 2 ** (sz * 8)
		self.data = 0

	def set(self, val):
		if (type(val) != int):
			self.data = (val.data % (self.size))
		else:
			self.data = (val % (self.size))

	def add(self, val):
		if (type(val) != int):
			self.data += val.data
			self.data %= (self.size)
		else:
			self.data += val
			self.data %= (self.size)
		return self

	def sub(self, val):
		if (type(val) != int):
			self.data -= val.data
			self.data %= (self.size)
		else:
			self.data -= val
			self.data %= (self.size)
		return self


KWS = [
	"MEM", # Memory allocation
	"SET", # Memory setting
	"IOUT", # Integer output
	"IIN", # Integer input
	"COUT", # Char output
	"ADD", # Add two numbers
	"SUB", # Subtract two numbers
	"EXIT", # Exit the program
	"GOTO", # Go to label (unconditionally)
	"RET", # Return from return stack
	"RETCL", # Clear the return stack
	"IEQ", # If ==
	"IGT", # If >
	"GOTOC" # Conditional jump
]

def lex(code):
	code = list((code + "\0").replace("\0", " \0"))
	pos = 0

	buf = ["", ""]
	tokens = []

	while (code[pos] != "\0"):
		if (code[pos] in "0123456789"):
			while (code[pos] in "0123456789"):
				buf[0] += code[pos]
				pos += 1
			tokens.append({"type": "int", "value": buf[0]})
			buf[0] = ""
		elif (code[pos] in " \n\t"):
			pos += 1
		else:
			while (code[pos] not in " \n"):
				buf[1] += code[pos]
				pos += 1
			if (buf[1][0] == "<" and buf[1][-1] == ">" and buf[1]):
				tokens.append({"type": "label", "value": buf[1][1:-1]})
			elif (buf[1][0] == "$"):
				tokens.append({"type": "box", "value": buf[1]})

			elif (buf[1] in KWS):
				tokens.append({"type": "keyword", "value": buf[1]})
			else:
				tokens.append({"type": "ident", "value": buf[1]})
			buf[1] = ""

	return tokens


def parse(toks):
	lnt = len(toks)
	retStack = []
	mems = {}
	cmpreg = 0
	try:
		pos = toks.index({"type": "label", "value": "0"})
	except:
		pos = 0

	while (pos < lnt):
		if (toks[pos]["type"] == "keyword"):
			if (toks[pos]["value"] == "EXIT"):
				assert (toks[pos+1]["type"] in ["int", "box"]), f"Trying to exit with non-integer value `{toks[pos+1]['type']}`"
				if (toks[pos+1]["type"] == "int"):
					exit(int(toks[pos+1]["value"]))
				elif (toks[pos+1]["type"] == "box"):
					exit(mems[toks[pos+1]["value"][1:]].data)

			elif (toks[pos]["value"] == "MEM"):
				assert (toks[pos+1]["type"] == "ident") and (toks[pos+2]["type"] == "int"), f"Parse error in MEM bolar"
				if (mems.get(toks[pos+1]["value"]) is None):
					mems[toks[pos+1]["value"]] = malloc(int(toks[pos+2]["value"]))
				else:
					assert False, f"Parse error, trying to redefine box identifier"
				pos += 2

			elif (toks[pos]["value"] == "SET"):
				assert (toks[pos+1]["type"] == "box") and (toks[pos+2]["type"] == "int"), f"Parse error in SET bolar"
				if (mems.get(toks[pos+1]["value"][1:]) is not None):
					mems[toks[pos+1]["value"][1:]].data = int(toks[pos+2]["value"])
				else:
					assert False, "Parse error in SET bolar"
				pos += 2

			elif (toks[pos]["value"] == "IOUT"):
				assert (toks[pos+1]["type"] in ["int", "box"]), f"Parse error in IOUT function"
				if (toks[pos+1]["type"] == "int"):
					print(toks[pos+1]["value"], end = "")
				else:
					print(mems.get(toks[pos+1]["value"][1:]).data, end  = "")
				pos += 1

			elif (toks[pos]["value"] == "IIN"):
				assert (toks[pos+1]["type"] == "box"), f"Parse error in IIN function"
				if (mems.get(toks[pos+1]["value"][1:]) is not None):
					mems.get(toks[pos+1]["value"][1:]).set(int(input()))
				else:
					assert False, "Parse error in IIN"

			elif (toks[pos]["value"] == "COUT"):
				assert (toks[pos+1]["type"] in ["int", "box"]), f"Parse error in IOUT function"
				if (toks[pos+1]["type"] == "int"):
					print(chr(int(toks[pos+1]["value"])), end = "")
				else:
					print(chr(mems.get(toks[pos+1]["value"][1:]).data, end  = ""))
				pos += 1

			elif (toks[pos]["value"] == "GOTO"):
				assert (toks[pos+1]["type"] == "int"), f"Parse error in GOTO"
				retStack.append(pos)
				pos = toks.index({"type": "label", "value": toks[pos+1]["value"]})

			elif (toks[pos]["value"] == "GOTOC"):
				assert (toks[pos+1]["type"] == "int"), f"Parse error in GOTOC"
				if (cmpreg):
					retStack.append(pos)
					pos = toks.index({"type": "label", "value": toks[pos+1]["value"]})

			elif (toks[pos]["value"] == "RET"):
				if (len(retStack) > 0):
					pos = retStack.pop()

			elif (toks[pos]["value"] == "RETCL"):
				retStack = []

			elif (toks[pos]["value"] == "ADD"):
				assert (toks[pos+1]["type"] == "box") and (toks[pos+2]["type"] in ["int", "box"]) and (toks[pos+3]["type"] == "box"), f"Parse error in ADD"
				if (toks[pos+2]["type"] == "box"):
					mems.get(toks[pos+3]["value"][1:]).set(mems.get(toks[pos+1]["value"][1:]).add(mems.get(toks[pos+2]["value"][1:])))
				else:
					mems.get(toks[pos+3]["value"][1:]).set(mems.get(toks[pos+1]["value"][1:]).add(int(toks[pos+2]["value"])))
				pos += 3

			elif (toks[pos]["value"] == "SUB"):
				assert (toks[pos+1]["type"] == "box") and (toks[pos+2]["type"] in ["int", "box"]) and (toks[pos+3]["type"] == "box"), f"Parse error in SUB"
				if (toks[pos+2]["type"] == "box"):
					mems.get(toks[pos+3]["value"][1:]).set(mems.get(toks[pos+1]["value"][1:]).sub(mems.get(toks[pos+2]["value"][1:])))
				else:
					mems.get(toks[pos+3]["value"][1:]).set(mems.get(toks[pos+1]["value"][1:]).sub(int(toks[pos+2]["value"])))
				pos += 3

			elif (toks[pos]["value"] == "IGT"):
				assert (toks[pos+1]["type"] == "box") and (toks[pos+2]["type"] in ["int", "box"]), f"Parse error in IGT"
				if (toks[pos+1]["type"] == "box" and toks[pos+2]["type"] == "box"):
					if (mems.get(toks[pos+1]["value"][1:]).data > mems.get(toks[pos+2]["value"][1:]).data):
						cmpreg = 1
					else:
						cmpreg = 0
				elif (toks[pos+1]["type"] == "box" and toks[pos+2]["type"] == "int"):
					if (mems.get(toks[pos+1]["value"][1:]).data > int(toks[pos+2]["value"])):
						cmpreg = 1
					else:
						cmpreg = 0
				pos += 2

			elif (toks[pos]["value"] == "IEQ"):
				assert (toks[pos+1]["type"] == "box") and (toks[pos+2]["type"] in ["int", "box"]), f"Parse error in IEQ"
				if (toks[pos+1]["type"] == "box" and toks[pos+2]["type"] == "box"):
					if (mems.get(toks[pos+1]["value"][1:]).data == mems.get(toks[pos+2]["value"][1:]).data):
						cmpreg = 1
					else:
						cmpreg = 0
				elif (toks[pos+1]["type"] == "box" and toks[pos+2]["type"] == "int"):
					if (mems.get(toks[pos+1]["value"][1:]).data == int(toks[pos+2]["value"])):
						cmpreg = 1
					else:
						cmpreg = 0
				pos += 2


#			elif (toks[pos]["value"] == "")

#		print(toks[pos], cmpreg)
		pos += 1


cdr = """
<0>
  MEM bound 2
  MEM n 2
  SET $n 0

  IIN $bound
  SUB $bound 1 $bound
  GOTO 1
<1>
  COUT 69
  IGT $bound $n
  GOTOC 2
  GOTO 3
<2>
  ADD $n 1 $n
  GOTO 1
<3>
  RETCL
  EXIT 0

"""
toks = lex(cdr)
parse(toks)
