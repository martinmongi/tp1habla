#!/usr/bin/env python

import sys
import os

# ==== Parseo los argumentos ======================================================================
args = sys.argv
texto = args[1]
out = args[2]

# ==== Me fijo si es pregunta, me voy a ocupar mas tarde ==========================================

es_pregunta = (texto[-1] == '?')

if es_pregunta: # si es pregunta, le saco el simbolo
	texto = texto[:-1]

# ==== Chequeo que sea una cadena valida ==========================================================

for i in range(0,len(texto),2):
	if not texto[i] in ['k', 'l', 'm', 'p', 's']:
		print "El caracter " + texto[i] + " no esta en el diccionario."
		sys.exit(0)

for i in range(1,len(texto),2):
	if not texto[i] in ['A', 'a']:
		print "El caracter " + texto[i] + " no esta en el diccionario."
		sys.exit(0)

# ==== Para cada par de letras, busco el difono ===================================================

concat = ["-" + texto[0]] # meto el primer difono

for i in xrange(1,len(texto)):
	concat.append(texto[i-1:i+1])

concat.append(texto[-1] + "-") # meto el ultimo difono

# ==== Concateno los difonos ======================================================================

concat_script = open('concat.praat','w')
concat_script.write("#!/usr/bin/env praat\n")

for i in xrange(0,len(concat)):
	concat_script.write("Read from file: \"./difonos/difonos-" + concat[i] + ".wav\"\n")
	concat_script.write("selectObject: \"Sound difonos-" + concat[i] + "\"\n")
	concat_script.write("Rename: \"difono" + str(i) + "\"\n")

concat_script.write("selectObject: \"Sound difono0\"\n")
for i in xrange(1,len(concat)):
	concat_script.write("plusObject: \"Sound difono" + str(i) + "\"\n")

concat_script.write("""Concatenate recoverably
selectObject: \"Sound chain\"
Save as WAV file: \"""" + out + """\"
selectObject: "TextGrid chain"
Save as text file: \"""" + out + """.TextGrid\"""")

concat_script.close()

os.system('praat concat.praat')
os.system('rm concat.praat')

# ==== Tengo que manipular la prosodia ============================================================
