#!/usr/bin/env python

import sys
import os
import re

# Configurar path a praat
praat = './praat'

def getTextGridIntervals(filename):
    # Leo los contenidos del archivo
    tgfile = open(filename,'r')
    contents = tgfile.read()
    tgfile.close()
    
    # Compilo la regexp y matcheo todos los grupos
    prog = re.compile('^ *x(min|max) = (\d*(.\d*)?)', re.MULTILINE)
    gss = prog.findall(contents)
    
    # Solamente me quedo con los segundos grupos que son los que tienen el numero
    # Y solamente me quedo con el correspondiente valor al minimo
    result = []
    for gs in gss:
        if gs[0] == 'min':
            result.append(float(gs[1]))
    # Agrego el maximo del ultimo grupo para tener el limite final        
    result.append(float(gss[len(gss)-1][1]))
    
    return result[2:len(result)]

def incrementPitch(filename, ofilename, start_val, end_val, pinc):
    # Leo los contenidos del archivo
    ptfile = open(filename,'r')
    contents = ptfile.read()
    ptfile.close()
    
    # Compilo las regexp
    prog_max = re.compile('^xmax = (\d*(.\d*)?)', re.MULTILINE)
    prog_numb = re.compile('^ *number = (\d*(.\d*)?)', re.MULTILINE)
    prog_val = re.compile('^ *value = (\d*(.\d*)?)', re.MULTILINE)
    
    # Matcheo todos los grupos
    xmaxs = prog_max.findall(contents)
    nss = prog_numb.findall(contents)
    vss = prog_val.findall(contents)
    
    # Guardo el valor de xmax
    xmax = xmaxs[0][0]
    
    # Busco donde tengo que comenzar a cambiar el pitch
    pointi = 0
    while float(nss[pointi][0]) < (start_val-0.025):
        pointi += 1
        
    # Calculo el avg pitch
    inc_pitch = 0
    for i in range(0, len(nss)):
        inc_pitch += float(vss[i][0])
    
    inc_pitch = (inc_pitch/len(vss))*pinc
    
    # Calculo el incremento
    inc = float(inc_pitch)/float((len(nss)-pointi))
    
    # Defino los nuevos valores
    nvs = []
    ni = 1
    for i in range(0, len(vss)):
        if i < pointi:
            nvs.append(float(vss[i][0]))
        else:
            nvs.append(float(vss[i][0])+inc*ni)
            ni += 1
    
    # Escribo el archivo
    ofile = open(ofilename,'w')
    ofile.write('File type = "ooTextFile"\nObject class = "PitchTier"\n\n')
    ofile.write('xmin = 0\nxmax = ' + str(xmax) + '\n')
    ofile.write('points: size = ' + str(len(nss)) + '\n')
    
    for i in range(0, len(nss)):
        ofile.write('points [' + str(i+1) + ']:' + '\n')
        ofile.write('    number = ' + nss[i][0] + '\n')
        ofile.write('    value = ' + str(nvs[i]) + '\n')
        
    ofile.close()
    
    return inc_pitch

# ==== Parseo los argumentos ======================================================================
args = sys.argv

if len(args) < 3:
    print "El uso correcto es ./tss.py secuencia salida.wav"
    sys.exit(0)

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

if es_pregunta:
    # Busco la ultima a acentuada
    la = 0
    for i in range(0,len(texto)):
        if texto[i] == 'A':
            la = i
            
    # Si no hay ninguna o esta muy lejos del final, agrego al final
    if la == 0 or (len(texto)-la-1) > 3:
        la = len(texto)-1
        textom = list(texto)
        textom[la] = 'A'
        texto = ''.join(textom)

concat = ["-" + texto[0]] # meto el primer difono

for i in xrange(1,len(texto)):
	concat.append(texto[i-1:i+1])

concat.append(texto[-1] + "-") # meto el ultimo difono

# ==== Concateno los difonos ======================================================================

concat_script = open('./concat.praat','w')
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

os.system(praat + ' concat.praat')
#os.system('rm concat.praat')

# ==== Tengo que manipular la prosodia ============================================================
if es_pregunta:
    
    # Limites del pitch
    min_pitch = 50
    max_pitch = 150

    # Extraemos el pitch track
    os.system(praat + ' extraer-pitch-track.praat ' + out + ' pitch-track.praat ' + str(min_pitch) + ' ' + str(max_pitch))

    # Cargamos los intervalos del textgrid
    intvals = getTextGridIntervals(out + '.TextGrid')

    # Marco los indices para incrementar el pitch en ese difono
    # Nota: En el pitch track no le pega bien a los difonos, ademas
    # es necesario incrementar desde antes y un poco despues, por eso
    # el intervalo esta agrandado.
    si = la-2
    ei = la+3
    
    # Acotamos si estamos fuera de lo admisible
    if si < 0:
        si = 0
    if len(intvals) <= ei:
        ei = len(intvals)-1
    
    # Definimos el intervalo
    print la, len(intvals), si, ei
    start_val = intvals[si]
    end_val = intvals[ei]

    # Incremento el pitch del archivo desde ese punto
    # pinc: Cuanto se incrementa en porcentaje con respecto al pitch promedio.
    # Ejemplo: Si el pitch promedio es 100 y pinc esta definido en .5, se incrementara el pitch en 50.
    pinc = 0.50
    inc_pitch = incrementPitch('pitch-track.praat', 'mod-pitch-track.praat', start_val, end_val, pinc)

    # Creo el nuevo wav con el pitch modificado
    os.system(praat + ' reemplazar-pitch-track.praat ' + out + ' mod-pitch-track.praat mod-' + out + ' ' + str(min_pitch) + ' ' + str(max_pitch+inc_pitch))

    # Renombro y elimino basura
    os.system('rm ' + out)
    os.system('mv mod-' + out + ' ' + out)
    os.system('rm pitch-track.praat')
    os.system('rm mod-pitch-track.praat')
