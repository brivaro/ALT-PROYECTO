import numpy as np

def levenshtein_matriz(x, y, threshold=None):
    # esta versión no utiliza threshold, se pone porque se puede invocar con él, en cuyo caso se ignora
    lenX, lenY = len(x), len(y)
    D = np.zeros((lenX + 1, lenY + 1), dtype=np.int64)
    for i in range(1, lenX + 1):
        D[i][0] = D[i - 1][0] + 1
    for j in range(1, lenY + 1):
        D[0][j] = D[0][j - 1] + 1
        for i in range(1, lenX + 1):
            D[i][j] = min(
                D[i - 1][j] + 1, #ELIMINACIÓN (pasa de arriba a abajo)
                D[i][j - 1] + 1, #INSERCIÓN (pasa de izq a der ->)
                D[i - 1][j - 1] + (x[i - 1] != y[j - 1]), #SUSTITUCIÓN (pasa en diagonal)
                #la letra en x y en y en la pos actual, será en la -1 de la pos de la matriz
                #si es !=  +1
            )
    #print("\n", D)
    ## EJEMPLO:  dist(x,y) = dist(camarero, caramelos)
    #      c a r a m e l o s
    #  [[0 1 2 3 4 5 6 7 8 9]
    # c [1 0 1 2 3 4 5 6 7 8]
    # a [2 1 0 1 2 3 4 5 6 7]
    # m [3 2 1 1 2 2 3 4 5 6]
    # a [4 3 2 2 1 2 3 4 5 6]
    # r [5 4 3 2 2 2 3 4 5 6]
    # e [6 5 4 3 3 3 2 3 4 5]
    # r [7 6 5 4 4 4 3 3 4 5]
    # o [8 7 6 5 5 5 4 4 3 4]] 

    # 1º se inicializa la primera columna
    # 2º se va haciendo columna a col de arriba a abajo
    # #
    
    return D[lenX, lenY]



def levenshtein_edicion(x, y, threshold=None):
    # a partir de la versión levenshtein_matriz
    """
    Devuelve la distancia y la secuencia de edición

    AYUDA: Se obtiene la secuencia de operaciones de edición en sentido inverso.
    Es más eficiente guardarlos con append y hacer un solo reverse al
    finalizar (insertarlos al inicio es más ineficiente).

    """

    ## EJEMPLO BACKTRACKING
    # 
    #      c a m p o s
    #  [[0 1 2 3 4 5 6]
    # e [1 1 2 3 4 5 6]
    # j [2 2 2 3 4 5 6]
    # e [3 3 3 3 4 5 6]
    # m [4 4 4 3 4 5 6]
    # p [5 5 5 4 3 4 5]
    # l [6 6 6 5 4 4 5]
    # o [7 7 7 6 5 4 5]]
    # 
    #(orig, nueva)
    #aplicar_edicion("ejemplo",[(’e’,’c’),(’j’,’a’),(’e’,’’),(’m’,’m’),(’p’,’p’),(’l’,’’),(’o’,’o’),(’’,’s’)]
    # ##
    lenX, lenY = len(x), len(y)
    D = np.zeros((lenX + 1, lenY + 1), dtype=np.int64)
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
    
    camino = []
    i, j = lenX, lenY
    while i > 0 or j > 0:
        a = D[i-1][j]
        b = D[i][j-1]
        c =  D[i-1][j-1]

        #DUDA: MAL no hay q usar el mínimo, mejor comprobar lo de arriba la der y despues diag
        if c == min(a,b,c): # caso de sustitución
            aux = (x[i-1], y[j-1])
            camino.append(aux)
            i-= 1; j-=1 
            #print(camino)
        elif a == min(a,b,c): # caso de Borrado
            #eliminar pasa de arriba a bajo (se resta 1 fila)
            aux = (x[i-1], "")
            camino.append(aux)
            i -= 1
            #print(camino)
        else:# b == min(a,b,c): # caso de Inserción
            #insertar pasa de izq a der(se resta una columna)
            aux = ("",y[j-1])
            camino.append(aux)
            j -= 1
            #print(camino)
        

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
   
    camino.reverse()
    return D[lenX, lenY], camino # COMPLETAR Y REEMPLAZAR ESTA PARTE

def levenshtein_reduccion(x, y, threshold=None):
    lenX, lenY = len(x), len(y) #calcula la longitud de las palabras
    prev = np.zeros(lenX + 1, dtype=np.int64) #relleno a 0
    current = np.zeros(lenX + 1, dtype=np.int64) #relleno a 0

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

def levenshtein(x, y, threshold):
    # completar versión reducción coste espacial y parada por threshold
    lenX, lenY = len(x), len(y) #calcula la longitud de las palabras
    prev = np.zeros(lenX + 1, dtype=np.int64) #relleno a 0
    current = np.zeros(lenX + 1, dtype=np.int64) #relleno a 0

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

        if threshold is not None and min(prev) > threshold:
            return threshold + 1

    return prev[lenX]
    

def levenshtein_cota_optimista(x, y, threshold):
    
    dic = {}
    for i in x:
        if i not in dic: dic[i] = 1
        else: dic[i]+=1
    for i in y:
        if i not in dic: dic[i] = -1
        else: dic[i]-=1

    valores = dic.values()
    valpos = 0
    valneg = 0 
    for i in valores:
        if i > 0:
            valpos += i
        else:
            valneg += i

    if (max(abs(valneg),valpos)) > threshold: 
        return threshold+1
    else: return levenshtein(x,y,threshold)

def damerau_restricted_matriz(x, y, threshold=None):
    # completar versión Damerau-Levenstein restringida con matriz
    lenX, lenY = len(x), len(y)
    # COMPLETAR
    return 0#D[lenX, lenY]

def damerau_restricted_edicion(x, y, threshold=None):
    # partiendo de damerau_restricted_matriz añadir recuperar
    # secuencia de operaciones de edición
    return 0,[] # COMPLETAR Y REEMPLAZAR ESTA PARTE

def damerau_restricted(x, y, threshold=None):
    # versión con reducción coste espacial y parada por threshold
     return min(0,threshold+1) # COMPLETAR Y REEMPLAZAR ESTA PARTE

def damerau_intermediate_matriz(x, y, threshold=None):
    # completar versión Damerau-Levenstein intermedia con matriz
    lenX, lenY = len(x), len(y)
    # Definir los cuatro vectores columna en lugar de tres    
    prev = np.zeros((lenY + 1), dtype=np.int64)
    current = np.zeros((lenY + 1), dtype=np.int64)
    prev_prev = np.zeros((lenY + 1), dtype=np.int64)
    prev_prev_prev = np.zeros((lenY + 1), dtype=np.int64)

    for i in range(1, lenY + 1):
        prev[i] = prev[i - 1] + 1
    
    for i in range(1, lenX + 1):
        current[0] = prev[0] + 1
        for j in range(1, lenY + 1):
            cost = 0 if x[i - 1] == y[j - 1] else 1
            cost2 = 2  # Costo de transposición
            current[j] = min(
                prev[j] + 1,                        # Eliminación
                current[j - 1] + 1,                 # Inserción
                prev[j - 1] + cost,                 # Sustitución o coincidencia
                prev_prev_prev[j - 2] + cost2 if i > 1 and j > 1 and x[i - 1] == y[j - 2] and x[i - 2] == y[j - 1] else float('inf')  # Transposición
            )
        prev_prev_prev, prev_prev, prev, current = prev_prev, prev, current, prev_prev_prev  # Actualizar los vectores

        # Comprobar el umbral
        if threshold is not None and min(prev) > threshold:
            return threshold + 1

    return prev[lenY]

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

