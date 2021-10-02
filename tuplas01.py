# tupla es una lista inmutable, NO SE PUEDE MODIFICAR
# al extraer una porcion, se crea una nueva dupla
# se puede comprobar si extiste un elemento

# nombreTupla( elem1, elem2, elem3...) como la lista pero con ( )

miTupla = ("David","Eva","Luis","Carmen","Luis")
print ( miTupla ) # muestra todo
print ( miTupla[2])



#convertir Tupla en Lista

miLista = list(miTupla)

# convertir Lista en Tupla

miTupla = tuple(miLista)

# cuantos elementos tiene la Tupla LEN

print ("cuantos elementos tiene la tupla?: ", len(miTupla))

# comprobar un elemento, si existe

print ("Luis esta en la Tupla? ","Luis" in miTupla)

# indice de un elemento

print (miTupla.index("Eva"))

# cuantas veces se repite un elementos

print ("cuantes veces esta Luis: ", miTupla.count("Luis") )

# Desempaquetado de Tupla, asignar elementos a variable
miTupla2 = ("David",2,"Enero",1985)
nombre,dia,mes,anio = miTupla2 #asigna los elementos a las variables

print(nombre,"nacio el dia ",dia," de ",mes," de ",anio)