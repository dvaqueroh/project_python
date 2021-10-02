# lista es como un ARRAY (java) pero puede contener diferentes tipos de variables
# sintaxis - nombreLista = [elemento1, elemento2, elemento3...]

milista=["david","Luis","Oscar","Edu"]

#print( milista[:]) # ":" imprime toda la lista
#print( milista[1])
#print ( milista[0:3]) # muestra del 0 al 2
#print ( milista[1:]) # desde el indice 2 hasta el final

#agregar elementos a la lista

milista.append( "Roberto")

# insertar elemento en una posicion : posicion,elemento

milista.insert(4,"Nacho")

# insertar varios elementos al final

milista.extend(["Deivid","Juanito"])

# devolver un indice de un elemento

#print (milista.index("Edu"))

# comprobar si existe un elemento en la lista

print ("se encuentra el elemento Luis en la lista: " , "Luis" in milista)

# eliminar elementos REMOVE

#milista.remove("Juanito")

# eliminar el ultimo elemento agregado a la lista POP

milista.pop()

# sumar listas

#milista2 = [2,34,False,"Azul"]

#milista3 = milista+milista2

# repetir lista ' * '  REPETIDOR


print (milista[:]*3)