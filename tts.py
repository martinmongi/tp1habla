#!/usr/bin/env python

import sys

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

concat = ["./difonos/-" + texto[0] + ".wav"] # meto el primer difono

for i in xrange(1,len(texto)):
	concat.append("./difonos/" + texto[i-1:i+1] + ".wav")

concat.append("./difonos/" + texto[-1] + "-.wav") # meto el ultimo difono

# ==== Concateno los difonos ======================================================================

