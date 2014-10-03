#!/usr/bin/env python

import sys
import os

# ==== Parseo los argumentos ======================================================================
args = sys.argv
texto = args[1]
out = args[2]

print 'Texto de entrada:', texto
print 'Archivo de salida:', out

# ==== Me fijo si es pregunta, me voy a ocupar mas tarde ==========================================

es_pregunta = (texto[-1] == '?')

if es_pregunta: # si es pregunta, le saco el simbolo
	texto = texto[:-1]

# ==== Para cada par de letras, busco el difono ===================================================

concat = ["-" + texto[0]] # meto el primer difono

for i in xrange(1,len(texto)):
	concat.append(texto[i-1:i+1])

concat.append(texto[-1] + "-") # meto el ultimo difono
print concat
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

print "Script de concatenacion creado"
os.system('praat concat.praat')
print "Concatenacion hecha"
# os.system('rm concat.praat')
# print "Script borrado"

# ==== Tengo que manipular la prosodia ============================================================
