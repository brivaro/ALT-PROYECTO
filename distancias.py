import numpy as np

def levenshtein_matriz(x, y, threshold=None):
    # esta versión no utiliza threshold, se pone porque se puede
    # invocar con él, en cuyo caso se ignora
    lenX, lenY = len(x), len(y)
    D = np.zeros((lenX + 1, lenY + 1), dtype=np.int)
    for i in range(1, lenX + 1):
        D[i][0] = D[i - 1][0] + 1
    for j in range(1, lenY + 1):
        D[0][j] = D[0][j - 1] + 1
        for i in range(1, lenX + 1):
            D[i][j] = min(
                D[i - 1][j] + 1,
                D[i][j - 1] + 1,
                D[i - 1][j - 1] + (x[i - 1] != y[j - 1]),
            )
    return D[lenX, lenY]

def levenshtein_edicion(x, y, threshold=None):
    # a partir de la versión levenshtein_matriz
    lenX, lenY = len(x), len(y)
    D = np.zeros((lenX + 1, lenY + 1))
    for i in range(1, lenX + 1):
        D[i][0] = D[i - 1][0] + 1
    for j in range(1, lenY + 1):
        D[0][j] = D[0][j - 1] + 1
        for i in range(1, lenX + 1):
            D[i][j] = min(
                D[i - 1][j] + 1,
                D[i][j - 1] + 1,
                D[i - 1][j - 1] + (x[i - 1] != y[j - 1]),
            )
    print(D)
    camino = []
    i, j = lenX, lenY
    while i > 0 or j > 0:
        a = D[i-1][j]
        b = D[i][j-1]
        c =  D[i-1][j-1]

        if a == min(a,b,c): # caso de Borrado
            print("Entra borrado")
            aux = (x[i-1], "")
            camino.append(aux)
            i -= 1
            print(camino)

        if b == min(a,b,c): # caso de Inserción
            print("Entra insercion")
            aux = ("",y[j-1])
            camino.append(aux)
            j -= 1
            print(camino)

        if c == min(a,b,c): # caso de sustitución
            print("Entra sustitucion")
            aux = (x[i-1], y[j-1])
            camino.append(aux)
            i-= 1; j-=1 
            print(camino)
            
            """también se podía así pero a marta le gusta más como arriba

            if i > 0 and D[i][j] == D[i - 1][j] + 1:
                camino.append((x[i - 1], ''))  # Eliminación
                i -= 1
            elif j > 0 and D[i][j] == D[i][j-1] + 1:
                camino.append(('', y[j - 1]))  # Inserción
                j -= 1
            else:
                camino.append((x[i - 1], y[j - 1]))  # Sustitución o igualdad
                i -= 1
                j -= 1
            """

    camino.reverse()  # Revertir la secuencia de edición

    return D[lenX, lenY],camino

def levenshtein_reduccion(x, y, threshold=None):
    # completar versión con reducción coste espacial
    lenX, lenY = len(x), len(y) #calcula la longitud de las palabras
    prev = np.zeros(lenX + 1) #relleno a 0
    current = np.zeros(lenX + 1) #relleno a 0

    for i in range(1, lenX + 1):
        prev[i] = prev[i - 1] + 1 # inicializa a 1,2,3,4... los posiciones 
                                  # menos la 0 qua ya estaba rellenada por np.zeros
    #REPRESENTACIÓN caas y casa
    # (eje y)
    #  prev  current
    # s   4     
    # a   3     
    # a   2     
    # c   1     0
    #     0     1 
    #           c      a      s      a    (eje x)
    #aqui abajo empezare con lo de levenstein

    camino = []  # para almacenar la secuencia de edición

    for j in range(1, lenY + 1): #la palabra y en el eje y
        current[0] = prev[0] + 1 
        for i in range(1, lenX + 1): #la plabra x en el eje x
            cost = 0 if x[i - 1] == y[j - 1] else 1
            current[i] = min(
                prev[i] + 1, #coste de eliminacion
                current[i - 1] + 1, #coste de insercion
                prev[i - 1] + cost # coste de no edicion
            )
        prev, current = current, prev  # Intercambiar los vectores

    return prev[lenX]


# Ejemplo de uso:
distancia1,camino = levenshtein_edicion("ejemplo", "campos")
distancia = levenshtein_reduccion("caas", "casa")
print("-------------------------\n\r-------------------------")
print("Levenstein EDICION (matriz con camino)")
print("Distancia de Levenshtein: ejemplo, campos", distancia1)
print("Secuencia de edición:", camino)
print("-------------------------")
print("Levenstein REDUCCION (vectores)")
print("Distancia de Levenshtein: caas, casa", distancia)



def levenshtein(x, y, threshold):
    # completar versión reducción coste espacial y parada por threshold
    lenX, lenY = len(x), len(y) #calcula la longitud de las palabras
    prev = np.zeros(lenX + 1) #relleno a 0
    current = np.zeros(lenX + 1) #relleno a 0

    for i in range(1, lenX + 1):
        prev[i] = prev[i - 1] + 1 # inicializa a 1,2,3,4... los posiciones 
                                  # menos la 0 qua ya estaba rellenada por np.zeros

    for j in range(1, lenY + 1): #la palabra y en el eje y
        current[0] = prev[0] + 1 
        for i in range(1, lenX + 1): #la plabra x en el eje x
            cost = 0 if x[i - 1] == y[j - 1] else 1
            current[i] = min(
                prev[i] + 1, #coste de eliminacion
                current[i - 1] + 1, #coste de insercion
                prev[i - 1] + cost # coste de no edicion
            )
        prev, current = current, prev  # Intercambiar los vectores

        if threshold is not None and prev[lenX] > threshold:
            return threshold + 1

    return prev[lenX]

dis = levenshtein("ejemplo", "campos", 4)
print(dis)


def levenshtein_cota_optimista(x, y, threshold):
    return 0 # COMPLETAR Y REEMPLAZAR ESTA PARTE

def damerau_restricted_matriz(x, y, threshold=None):
    # completar versión Damerau-Levenstein restringida con matriz
    lenX, lenY = len(x), len(y)
    # COMPLETAR
    return D[lenX, lenY]

def damerau_restricted_edicion(x, y, threshold=None):
    # partiendo de damerau_restricted_matriz añadir recuperar
    # secuencia de operaciones de edición
    return 0,[] # COMPLETAR Y REEMPLAZAR ESTA PARTE

def damerau_restricted(x, y, threshold=None):
    # versión con reducción coste espacial y parada por threshold
     return min(0,threshold+1) # COMPLETAR Y REEMPLAZAR ESTA PARTE

def damerau_intermediate_matriz(x, y, threshold=None):
    # completar versión Damerau-Levenstein intermedia con matriz
    return D[lenX, lenY]

def damerau_intermediate_edicion(x, y, threshold=None):
    # partiendo de matrix_intermediate_damerau añadir recuperar
    # secuencia de operaciones de edición
    # completar versión Damerau-Levenstein intermedia con matriz
    return 0,[] # COMPLETAR Y REEMPLAZAR ESTA PARTE
    
def damerau_intermediate(x, y, threshold=None):
    # versión con reducción coste espacial y parada por threshold
    return min(0,threshold+1) # COMPLETAR Y REEMPLAZAR ESTA PARTE

opcionesSpell = {
    'levenshtein_m': levenshtein_matriz,
    'levenshtein_r': levenshtein_reduccion,
    'levenshtein':   levenshtein,
    'levenshtein_o': levenshtein_cota_optimista,
    'damerau_rm':    damerau_restricted_matriz,
    'damerau_r':     damerau_restricted,
    'damerau_im':    damerau_intermediate_matriz,
    'damerau_i':     damerau_intermediate
}

opcionesEdicion = {
    'levenshtein': levenshtein_edicion,
    'damerau_r':   damerau_restricted_edicion,
    'damerau_i':   damerau_intermediate_edicion
}

