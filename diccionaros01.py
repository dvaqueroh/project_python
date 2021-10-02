# datos con asociacion en CLAVE:VALOR
# se guardan elementos entre llaves " { }"
miDiccionario = {"España":"Madrid","Alemania":"Berlin","Francia":"Paris","Reino Unido":"Londres"}

#acceder al valor de un elemento

#print( miDiccionario["España"])

# muestra todo el diccionaro

#print ( miDiccionario )

# agregar elemento

#miDiccionario["Italia"]="CiudadMal"

#print ( miDiccionario )
# modificar un valor de una clave

miDiccionario["Italia"]="Roma"

#print ( miDiccionario )

# eliminar elemento

#del miDiccionario["Reino Unido"]

# asignar valor desde una Tupla

miTupla = ["España","Francia","Italia","Reino Unido","Alemania"]
miDiccionario2 = {miTupla[0]:"Madrid",miTupla[1]:"Paris",miTupla[4]:"Berlin"}
#print ( miDiccionario2 )

# Un diccionario almacena una tupla de valores

#miDiccionario3={ 23:"Jordan","Nombre":"Michael","Equipo":"Chicago Bulls","Anillos":[1991,1992,1993,1996,1997,1998]}
#print ( miDiccionario3)
#print ( miDiccionario3["Anillos"])

# guardar diccionario en otro diccionario
miDiccionario3={ 23:"Jordan","Nombre":"Michael","Equipo":"Chicago Bulls","Anillos":{"Temporadas":[1991,1992,1993,1996,1997,1998]}}
print ( miDiccionario3["Anillos"])

# KEYS devuelve las claves del diccionario
print ("Claves: ", miDiccionario3.keys() )
# VALUES devuelve los valores del diccionario
print ("Valores: ", miDiccionario3.values())
# LEN devuelve la longitud
print( "Longitud: ",len(miDiccionario3))