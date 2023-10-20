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
        elif a == min(a,b,c): # caso de Borrado
            #eliminar pasa de arriba a bajo (se resta 1 fila)
            aux = (x[i-1], "")
            camino.append(aux)
            i -= 1
        else:# b == min(a,b,c): # caso de Inserción
            #insertar pasa de izq a der(se resta una columna)
            aux = ("",y[j-1])
            camino.append(aux)
            j -= 1
        

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
        for i in range(1, lenX + 1): #la palabra x en el eje x
            cost = 0 if x[i - 1] == y[j - 1] else 1
            current[i] = min(
                prev[i] + 1, #coste de eliminación
                current[i - 1] + 1, #coste de inserción
                prev[i - 1] + cost # coste de no edición
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

        # no da bien pero es porque el profe ha hecho las pruebas con >= que es lo que ponía en las traspas
        if threshold is not None and min(prev) > threshold: 
            return threshold + 1
    # tenemos que comprobar si el valor del último pudiera superar el threshold+1, tenemos que poner esto en todos los lugares que utilicemos threshold
    return min(prev[lenX],threshold+1)
    

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

# no da bien pero es porque el profe ha hecho las pruebas con >= que es lo que ponía en las traspas 
    if (max(abs(valneg),valpos)) > threshold: 
        return threshold+1
    else: return levenshtein(x,y,threshold)

def damerau_restricted_matriz(x, y, threshold=None):
    # completar versión Damerau-Levenstein restringida con matriz

    lenX, lenY = len(x), len(y)
    D = np.zeros((lenX + 1, lenY + 1), dtype=np.int64)
    for i in range(1, lenX + 1):
        D[i][0] = D[i - 1][0] + 1
    for j in range(1, lenY + 1):
        D[0][j] = D[0][j - 1] + 1
        for i in range(1, lenX + 1):
            if i > 1 and j > 1 and (x[i-2] == y[j-1] and x[i-1] == y[j-2]):
                D[i][j] = min(
                D[i - 1][j] + 1, #ELIMINACIÓN (pasa de arriba a abajo)
                D[i][j - 1] + 1, #INSERCIÓN (pasa de izq a der ->)
                D[i - 1][j - 1] + (x[i - 1] != y[j - 1]), #SUSTITUCIÓN (pasa en diagonal)
                D[i-2][j-2] + 1
                )
            else:
                D[i][j] = min(
                D[i - 1][j] + 1, #ELIMINACIÓN (pasa de arriba a abajo)
                D[i][j - 1] + 1, #INSERCIÓN (pasa de izq a der ->)
                D[i - 1][j - 1] + (x[i - 1] != y[j - 1]), #SUSTITUCIÓN (pasa en diagonal)
            )

    # COMPLETAR
    return D[lenX, lenY]

def damerau_restricted_edicion(x, y, threshold=None):
    # partiendo de damerau_restricted_matriz añadir recuperar
    # secuencia de operaciones de edición

    lenX, lenY = len(x), len(y)
    D = np.zeros((lenX + 1, lenY + 1), dtype=np.int64)
    for i in range(1, lenX + 1):
        D[i][0] = D[i - 1][0] + 1
    for j in range(1, lenY + 1):
        D[0][j] = D[0][j - 1] + 1
        for i in range(1, lenX + 1):
            if i > 1 and j > 1 and (x[i-2] == y[j-1] and x[i-1] == y[j-2]):
                D[i][j] = min(
                D[i - 1][j] + 1, #ELIMINACIÓN (pasa de arriba a abajo)
                D[i][j - 1] + 1, #INSERCIÓN (pasa de izq a der ->)
                D[i - 1][j - 1] + (x[i - 1] != y[j - 1]), #SUSTITUCIÓN (pasa en diagonal)
                D[i-2][j-2] + 1
                )
            else:
                D[i][j] = min(
                D[i - 1][j] + 1, #ELIMINACIÓN (pasa de arriba a abajo)
                D[i][j - 1] + 1, #INSERCIÓN (pasa de izq a der ->)
                D[i - 1][j - 1] + (x[i - 1] != y[j - 1]), #SUSTITUCIÓN (pasa en diagonal)
            )
    
    camino = []
    i, j = lenX, lenY
    while i > 0 or j > 0:
        a = D[i-1][j]
        b = D[i][j-1]
        c =  D[i-1][j-1]
        d = D[i-2][j-2]

        #DUDA: MAL no hay q usar el mínimo, mejor comprobar lo de arriba la der y despues diag
        if i > 1 and j > 1 and (x[i-2] == y[j-1] and x[i-1] == y[j-2]):
            if d == min(a, b, c, d):
                aux = ((x[i-2]+x[i-1]) , (y[j-2]+y[j-1])) #NOTA PARA MARTA DE ADRIÁN: no tendría sentido poner todas las x en un lado y las y en otro? aunque son equivalentes x-->y
                camino.append(aux)
                i-=2; j-=2
                continue

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


def damerau_restricted(x, y, threshold=None):
    # versión con reducción coste espacial y parada por threshold
    lenX, lenY = len(x), len(y) #calcula la longitud de las palabras
    prev_2 = np.zeros(lenX + 1, dtype=np.int64) #relleno a 0
    prev = np.zeros(lenX + 1, dtype=np.int64) #relleno a 0
    current = np.zeros(lenX + 1, dtype=np.int64) #relleno a 0

    for i in range(1, lenX + 1):
        prev[i] = prev[i - 1] + 1 # inicializa a 1,2,3,4... los posiciones 
                                  # menos la 0 qua ya estaba rellenada por np.zeros

    for j in range(1, lenY + 1): #la palabra y en el eje y
        current[0] = prev[0] + 1 
        for i in range(1, lenX + 1): #la plabra x en el eje x

            cost = 0 if x[i - 1] == y[j - 1] else 1
            
            if i > 1 and j > 1 and (x[i-2] == y[j-1] and x[i-1] == y[j-2]):
                current[i] = min(
                    prev[i] + 1, #coste de eliminacion
                    current[i - 1] + 1, #coste de insercion
                    prev[i - 1] + cost, # coste de no edicion
                    prev_2[i-2] + cost
                )
            else:
                current[i] = min(
                    prev[i] + 1, #coste de eliminacion
                    current[i - 1] + 1, #coste de insercion
                    prev[i - 1] + cost # coste de no edicion
                )
        #print(prev_2)
        #print(prev)
        #print(current)
        #print("-----------\n")
        
        prev_2 = prev
        prev = current
        if j < lenY: current = np.zeros(lenX + 1, dtype=np.int64)

        if threshold is not None and min(prev) > threshold:
            return threshold + 1
    
    return min(prev[lenX],threshold+1) # COMPLETAR Y REEMPLAZAR ESTA PARTE

def damerau_intermediate_matriz(x, y, threshold=None):
    # completar versión Damerau-Levenstein intermedia con matriz
    """
        D(i, j) = min(
                        D(i - 1, j) + 1,               # Deletión
                        D(i, j - 1) + 1,               # Inserción
                        D(i - 1, j - 1) + cost(x[i], y[j]),  # Sustitución

                        D(i - 2, j - 2) + 1,           # Transposición (ab ↔ ba)  +1
                        D(i - 1, j - 2) + 2,           # Transposición (acb ↔ ba)  del+trans +2
                        D(i - 2, j - 1) + 2,           # Transposición (ab ↔ bca)  trans+ins +2
                    )

    """
    lenX, lenY = len(x), len(y)
    D = np.zeros((lenX + 1, lenY + 1), dtype=np.int64)
    for i in range(1, lenX + 1):
        D[i][0] = D[i - 1][0] + 1

    for j in range(1, lenY + 1):
        D[0][j] = D[0][j - 1] + 1
        for i in range(1, lenX + 1):
            if i > 1 and j > 1 and (x[i-2] == y[j-1] and x[i-1] == y[j-2]):
                D[i][j] = min(
                D[i - 1][j] + 1, #ELIMINACIÓN (pasa de arriba a abajo)
                D[i][j - 1] + 1, #INSERCIÓN (pasa de izq a der ->)
                D[i - 1][j - 1] + (x[i - 1] != y[j - 1]), #SUSTITUCIÓN (pasa en diagonal)
                D[i-2][j-2] + 1 #trasposicion consecutiva
                )
            elif i >= 2 and j >= 2 and ((x[i-1] == y[j-3] and x[i-2] == y[j-1])):
                D[i][j] = min(
                D[i - 1][j] + 1, #ELIMINACIÓN (pasa de arriba a abajo)
                D[i][j - 1] + 1, #INSERCIÓN (pasa de izq a der ->)
                D[i - 1][j - 1] + (x[i - 1] != y[j - 1]), #SUSTITUCIÓN (pasa en diagonal)
                D[i-2][j-3] + 2 #trasposicion ab ↔ bca coste 2
                )
            elif i >= 2 and j >= 2 and ((x[i-1] == y[j-2] and x[i-3] == y[j-1])):
                D[i][j] = min(
                D[i - 1][j] + 1, #ELIMINACIÓN (pasa de arriba a abajo)
                D[i][j - 1] + 1, #INSERCIÓN (pasa de izq a der ->)
                D[i - 1][j - 1] + (x[i - 1] != y[j - 1]), #SUSTITUCIÓN (pasa en diagonal)
                D[i-3][j-2] + 2 #trasposicion acb ↔ ba coste 2
                )
            else:
                D[i][j] = min(
                D[i - 1][j] + 1, #ELIMINACIÓN (pasa de arriba a abajo)
                D[i][j - 1] + 1, #INSERCIÓN (pasa de izq a der ->)
                D[i - 1][j - 1] + (x[i - 1] != y[j - 1]), #SUSTITUCIÓN (pasa en diagonal)
            )
        # Comprobar el umbral 
        # **************************************************
        # #DUDA CUANDO PONGO LO DEL THERSHOLD DA BIEN LO QUE PASA ES QUE TENGO QUE PREGUNTARLE AL PROFE PORQUE EN SU SOLUCION NO SALE TENIENDO CUENTA EL THERSHOLD
        # Recordar que si se modifica esto, hay que modificar el método de abajo
        # **************************************************
        #if threshold is not None and min(row[j] for row in D) > threshold:
        #   return threshold + 1
    #if x=="algoritmo" and y=="algortximo": print(D)
    return D[lenX][lenY]


def damerau_intermediate_edicion(x, y, threshold=None):
    # partiendo de matrix_intermediate_damerau añadir recuperar
    # secuencia de operaciones de edición
    # completar versión Damerau-Levenstein intermedia con matriz    

    lenX, lenY = len(x), len(y)
    D = np.zeros((lenX + 1, lenY + 1), dtype=np.int64)
    for i in range(1, lenX + 1):
        D[i][0] = D[i - 1][0] + 1

    for j in range(1, lenY + 1):
        D[0][j] = D[0][j - 1] + 1
        for i in range(1, lenX + 1):
            if i > 1 and j > 1 and (x[i-2] == y[j-1] and x[i-1] == y[j-2]):
                D[i][j] = min(
                D[i - 1][j] + 1, #ELIMINACIÓN (pasa de arriba a abajo)
                D[i][j - 1] + 1, #INSERCIÓN (pasa de izq a der ->)
                D[i - 1][j - 1] + (x[i - 1] != y[j - 1]), #SUSTITUCIÓN (pasa en diagonal)
                D[i-2][j-2] + 1 #trasposicion consecutiva
                )
            elif i >= 2 and j >= 2 and ((x[i-1] == y[j-3] and x[i-2] == y[j-1])):
                D[i][j] = min(
                D[i - 1][j] + 1, #ELIMINACIÓN (pasa de arriba a abajo)
                D[i][j - 1] + 1, #INSERCIÓN (pasa de izq a der ->)
                D[i - 1][j - 1] + (x[i - 1] != y[j - 1]), #SUSTITUCIÓN (pasa en diagonal)
                D[i-2][j-3] + 2 #trasposicion ab ↔ bca coste 2
                )
            elif i >= 2 and j >= 2 and ((x[i-1] == y[j-2] and x[i-3] == y[j-1])):
                D[i][j] = min(
                D[i - 1][j] + 1, #ELIMINACIÓN (pasa de arriba a abajo)
                D[i][j - 1] + 1, #INSERCIÓN (pasa de izq a der ->)
                D[i - 1][j - 1] + (x[i - 1] != y[j - 1]), #SUSTITUCIÓN (pasa en diagonal)
                D[i-3][j-2] + 2 #trasposicion acb ↔ ba coste 2
                )
            else:
                D[i][j] = min(
                D[i - 1][j] + 1, #ELIMINACIÓN (pasa de arriba a abajo)
                D[i][j - 1] + 1, #INSERCIÓN (pasa de izq a der ->)
                D[i - 1][j - 1] + (x[i - 1] != y[j - 1]), #SUSTITUCIÓN (pasa en diagonal)
            )

    camino = []

    i, j = lenX, lenY
    while i > 0 or j > 0:

        a = D[i-1][j]       #borrado
        b = D[i][j-1]       #insercion
        c = D[i-1][j-1]    #sustitucion

        d = D[i-2][j-2]     #ab ↔ ba coste 1
        e = D[i-2][j-1]     #acb ↔ ba coste 2
        f = D[i-1][j-2]     #ab ↔ bca coste 2


        #DUDA: MAL no hay q usar el mínimo, mejor comprobar lo de arriba la der y despues diag #DUDA x2
        if i > 1 and j > 1 and (x[i-2] == y[j-1] and x[i-1] == y[j-2]) and d == min(a, b, c, d): #ab ↔ ba coste 1
            aux = ((x[i-2]+x[i-1]) , (y[j-2]+y[j-1])) 
            camino.append(aux)
            i-=2; j-=2
            continue

        if i > 2 and j > 1 and (x[i-3] == y[j-1] and x[i-1] == y[j-2]) and e == min(a, b, c, e): #acb ↔ ba coste 2
            aux = ((x[i-3]+x[i-2]+x[i-1]) , (y[j-2]+y[j-1])) 
            camino.append(aux)
            i-=3; j-=2
            continue

        if i > 1 and j > 2 and (x[i-2] == y[j-1] and x[i-1] == y[j-3]) and  f == min(a, b, c, f): #ab ↔ bca coste 2
            aux = ((x[i-2]+x[i-1]) , (y[j-3]+y[j-2]+y[j-1])) 
            camino.append(aux)
            i-=2; j-=3
            continue

        if c == min(a,b,c): # caso de sustitución
            aux = (x[i-1], y[j-1])   
            camino.append(aux)
            i-= 1; j-=1 

        elif a == min(a,b,c): # caso de Borrado
            aux = (x[i-1], "")
            camino.append(aux)
            i -= 1
        else: # b == min(a,b,c): # caso de Inserción
            aux = ("",y[j-1])
            camino.append(aux)
            j -= 1    
   
    camino.reverse()
    
    return D[lenX][lenY],camino # COMPLETAR Y REEMPLAZAR ESTA PARTE
    
def damerau_intermediate(x, y, threshold=None):
      # versión con reducción coste espacial y parada por threshold
    
    #TIENE QUE ESTAR INSPIRADO EN EL CODIGO DE MARTA:
    lenX, lenY = len(x), len(y)
    prev = np.zeros(lenX + 1, dtype=np.int64)
    current = np.zeros(lenX + 1, dtype=np.int64)
    prev2 = np.zeros(lenX + 1, dtype=np.int64)
    prev3 = np.zeros(lenX + 1, dtype=np.int64)

    for i in range(1, lenX + 1):
        prev[i] = prev[i - 1] + 1

    for j in range(1, lenY + 1):
        current[0] = prev[0] + 1
        for i in range(1, lenX + 1):
            cost = 0 if x[i - 1] == y[j - 1] else 1
            deletion = prev[i] + 1
            insertion = current[i - 1] + 1
            substitution = prev[i - 1] + cost
            current[i] = min(deletion, insertion, substitution)

            if i > 1 and j > 1 and x[i - 1] == y[j - 2] and x[i - 2] == y[j - 1]:
                transposition = prev2[i - 2] + 1
                current[i] = min(current[i], transposition)

            #TRANSPOSICION 1: DEL-TRAS
            if i > 2 and j > 1 and x[i - 1] == y[j - 2] and x[i - 3] == y[j - 1]:
                transposition1 = prev2[i - 3] + 2
                current[i] = min(current[i], transposition1)

            #TRANSPOSICION 2: TRAS-INS
            if i > 1 and j > 2 and x[i - 1] == y[j - 3] and x[i - 2] == y[j - 1]:
                transposition2 = prev3[i - 2] + 2
                current[i] = min(current[i], transposition2)          

        prev3, prev2, prev, current = prev2, prev, current, prev3
        #prev2, prev, current = prev, current, prev2

        if threshold is not None and min(prev) > threshold:
            return threshold + 1

    return prev[lenX]

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

#damerau_restricted("acb", "ba")