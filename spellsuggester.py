# -*- coding: utf-8 -*-
import re

class SpellSuggester:

    """
    Clase que implementa el método suggest para la búsqueda de términos.
    """

    def __init__(self,
                 dist_functions,
                 vocab = [],
                 default_distance = None,
                 default_threshold = None):
        
        """Método constructor de la clase SpellSuggester

        Construye una lista de términos únicos (vocabulario),

        Args:
           dist_functions es un diccionario nombre->funcion_distancia
           vocab es una lista de palabras o la ruta de un fichero //DUDA
           default_distance debe ser una clave de dist_functions
           default_threshold un entero positivo

        """
        self.distance_functions = dist_functions        
        self.set_vocabulary(vocab)
        if default_distance is None:
            default_distance = 'levenshtein'
        if default_threshold is None:
            default_threshold = 3
        self.default_distance = default_distance
        self.default_threshold = default_threshold

    def build_vocabulary(self, vocab_file_path):
        """Método auxiliar para crear el vocabulario.

        Se tokeniza por palabras el fichero de texto,
        se eliminan palabras duplicadas y se ordena
        lexicográficamente.

        Args:
            vocab_file (str): ruta del fichero de texto para cargar el vocabulario.
            tokenizer (re.Pattern): expresión regular para la tokenización.
        """
        tokenizer=re.compile("\W+") #coincide con uno o más caracteres no alfanuméricos (como espacios, comas, puntos, etc.) y se utiliza como delimitador para dividir el texto en palabras
        with open(vocab_file_path, "r", encoding="utf-8") as fr:
            vocab = set(tokenizer.split(fr.read().lower()))
            vocab.discard("")  # por si acaso (se eliminan las posibles cadenas vacías si hay)
            return sorted(vocab)

    def set_vocabulary(self, vocabulary):
        if isinstance(vocabulary,list): #si es una lista
            self.vocabulary = vocabulary # atención! nos quedamos una referencia, a tener en cuenta
        elif isinstance(vocabulary,str): #si es un string
            self.vocabulary = self.build_vocabulary(vocabulary)  #DUDA: Este es el caso si es una ruta de fichero, ya estaría cubierto este caso?         
        else:
            raise Exception("SpellSuggester incorrect vocabulary value")

    def suggest(self, term, distance=None, threshold=None, flatten=True):
        """

        Args:
            term (str): término de búsqueda.
            distance (str): nombre del algoritmo de búsqueda a utilizar
            threshold (int): threshold para limitar la búsqueda
        """
        if distance is None:
            distance = self.default_distance
        if threshold is None:
            threshold = self.default_threshold
            
        fdist = self.distance_functions[distance]


        #resul es una lista de listas
        resul = [[] for i in range(threshold+1)] # hasta threshold inclusive
        for w in self.vocabulary: #busca en el vocab todas las palaras q estan a una distancia del term <= threshold 
            d = fdist(term,w,threshold)
            if d <= threshold:
                resul[d].append(w)#devuelve en la pos equivalente a su dist, la palabra w

        #convertimos resul en una lista, eliminamos las sublistas
        if flatten:
            resul = [word for wlist in resul for word in wlist]
            
        return resul

