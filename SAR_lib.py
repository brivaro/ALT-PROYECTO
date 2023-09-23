import json
from nltk.stem.snowball import SnowballStemmer
import os
import re
import sys
import math
from pathlib import Path
from typing import Optional, List, Union, Dict
import pickle

##### AUTORES #####
# Brian Valiente Ródenas
# Adrián Camacho García
# Ana Gutiérrez Mandingorra 
# Marta Jimenez Montalva 
# Luis Miguel Carmona Pérez

class SAR_Indexer:
    """
    Prototipo de la clase para realizar la indexacion y la recuperacion de artículos de Wikipedia
        
        Preparada para todas las ampliaciones:
          parentesis + multiples indices + posicionales + stemming + permuterm

    Se deben completar los metodos que se indica.
    Se pueden añadir nuevas variables y nuevos metodos
    Los metodos que se añadan se deberan documentar en el codigo y explicar en la memoria
    """

    # lista de campos, el booleano indica si se debe tokenizar el campo
    # NECESARIO PARA LA AMPLIACION MULTIFIELD
    fields = [
        ("all", True), ("title", True), ("summary", True), ("section-name", True), ('url', False),
    ]
    
    def_field = fields[0] #fija el def field a la tupla dentro de fields "all"
    PAR_MARK = '%'
    # numero maximo de documento a mostrar cuando self.show_all es False
    SHOW_MAX = 10

    all_atribs = ['urls', 'index', 'sindex', 'ptindex', 'docs', 'weight', 'articles',
                  'tokenizer', 'stemmer', 'show_all', 'use_stemming']

    def __init__(self):
        """
        Constructor de la classe SAR_Indexer.
        NECESARIO PARA LA VERSION MINIMA

        Incluye todas las variables necesaria para todas las ampliaciones.
        Puedes añadir más variables si las necesitas 

        """
        self.urls = set() # hash para las urls procesadas,
        self.index = {} # hash para el indice invertido de terminos --> clave: termino, valor: posting list
        '''
        self.index = { 'all': {},
                       'tittle': {},
                       'summary': {},
                       'section_name': {},
                       
        }'''
        self.sindex = {} # hash para el indice invertido de stems --> clave: stem, valor: lista con los terminos que tienen ese stem
        '''
        self.sindex = {'all': {},
                       'tittle': {},
                       'summary': {},
                       'section_name': {},
                       
        }'''
        self.ptindex = {} # hash para el indice permuterm.
        '''
        self.ptindex = {'all': {},
                       'tittle': {},
                       'summary': {},
                       'section_name': {},
                       
        }'''
        self.docs = {} # diccionario de terminos --> clave: entero(docid),  valor: ruta del fichero.
        self.weight = {} # hash de terminos para el pesado, ranking de resultados.
        self.articles = {} # hash de articulos --> clave entero (artid), valor: la info necesaria para diferencia los artículos dentro de su fichero
        self.tokenizer = re.compile("\W+") # expresion regular para hacer la tokenizacion
        self.stemmer = SnowballStemmer('spanish') # stemmer en castellano
        self.show_all = False # valor por defecto, se cambia con self.set_showall()
        self.show_snippet = False # valor por defecto, se cambia con self.set_snippet()
        self.use_stemming = False # valor por defecto, se cambia con self.set_stemming()
        self.use_ranking = False  # valor por defecto, se cambia con self.set_ranking()

        self.use_positional = False

        #AÑADIDOS POR NOSOTROS:
        self.docid = 0
        self.artid = 0
        self.lini = 0
        self.fin = 0
        self.urlRepetida = False
        self.primeraiteracion = 0
        
        
    ###############################
    ###                         ###
    ###      CONFIGURACION      ###
    ###                         ###
    ###############################


    def set_showall(self, v:bool):
        """

        Cambia el modo de mostrar los resultados.
        
        input: "v" booleano.

        UTIL PARA TODAS LAS VERSIONES

        si self.show_all es True se mostraran todos los resultados el lugar de un maximo de self.SHOW_MAX, no aplicable a la opcion -C

        """
        self.show_all = v


    def set_snippet(self, v:bool):
        """

        Cambia el modo de mostrar snippet.
        
        input: "v" booleano.

        UTIL PARA TODAS LAS VERSIONES

        si self.show_snippet es True se mostrara un snippet de cada noticia, no aplicable a la opcion -C

        """
        self.show_snippet = v


    def set_stemming(self, v:bool):
        """

        Cambia el modo de stemming por defecto.
        
        input: "v" booleano.

        UTIL PARA LA VERSION CON STEMMING

        si self.use_stemming es True las consultas se resolveran aplicando stemming por defecto.

        """
        self.use_stemming = v



    #############################################
    ###                                       ###
    ###      CARGA Y GUARDADO DEL INDICE      ###
    ###                                       ###
    #############################################


    def save_info(self, filename:str):
        """
        Guarda la información del índice en un fichero en formato binario
        
        """
        info = [self.all_atribs] + [getattr(self, atr) for atr in self.all_atribs]
        with open(filename, 'wb') as fh:
            pickle.dump(info, fh)

    def load_info(self, filename:str):
        """
        Carga la información del índice desde un fichero en formato binario
        
        """
        #info = [self.all_atribs] + [getattr(self, atr) for atr in self.all_atribs]
        with open(filename, 'rb') as fh:
            info = pickle.load(fh)
        atrs = info[0]
        for name, val in zip(atrs, info[1:]):
            setattr(self, name, val)

    ###############################
    ###                         ###
    ###   PARTE 1: INDEXACION   ###
    ###                         ###
    ###############################

    def already_in_index(self, article:Dict) -> bool:
        """

        Args:
            article (Dict): diccionario con la información de un artículo

        Returns:
            bool: True si el artículo ya está indexado, False en caso contrario
        """
        return article['url'] in self.urls


    def index_dir(self, root:str, **args):
        """
        
        Recorre recursivamente el directorio o fichero "root" 
        NECESARIO PARA TODAS LAS VERSIONES
        
        Recorre recursivamente el directorio "root"  y indexa su contenido
        los argumentos adicionales "**args" solo son necesarios para las funcionalidades ampliadas

        """
        self.multifield = args['multifield']
        self.positional = args['positional']
        self.stemming = args['stem']
        self.permuterm = args['permuterm']

        file_or_dir = Path(root)
        
        if file_or_dir.is_file():
            # is a file
            self.index_file(root)
        elif file_or_dir.is_dir():
            # is a directory
            for d, _, files in os.walk(root):
                for filename in files:
                    if filename.endswith('.json'):
                        fullname = os.path.join(d, filename)
                        self.index_file(fullname)
        else:
            print(f"ERROR:{root} is not a file nor directory!", file=sys.stderr)
            sys.exit(-1)

        ##########################################
        ## COMPLETAR PARA FUNCIONALIDADES EXTRA ##
        ##########################################

        # si se activa la función de stemming
        if self.stemming:
            self.make_stemming()
        # si se activa la función de permuterm
        if self.permuterm:
            self.make_permuterm()
        
        
        
    def parse_article(self, raw_line:str) -> Dict[str, str]:
        """
        Crea un diccionario a partir de una linea que representa un artículo del crawler

        Args:
            raw_line: una linea del fichero generado por el crawler

        Returns:
            Dict[str, str]: claves: 'url', 'title', 'summary', 'all', 'section-name'
        """
        
        article = json.loads(raw_line)
        sec_names = []
        txt_secs = ''
        for sec in article['sections']:            
            txt_secs += sec['name'] + '\n' + sec['text'] + '\n'
            txt_secs += '\n'.join(subsec['name'] + '\n' + subsec['text'] + '\n' for subsec in sec['subsections']) + '\n\n'
            sec_names.append(sec['name'])
            sec_names.extend(subsec['name'] for subsec in sec['subsections'])
        article.pop('sections') # no la necesitamos 
        article['all'] = article['title'] + '\n\n' + article['summary'] + '\n\n' + txt_secs
        article['section-name'] = '\n'.join(sec_names)

        return article
                
    
    def index_file(self, filename:str):
        """

        Indexa el contenido de un fichero.
        
        input: "filename" es el nombre de un fichero generado por el Crawler cada línea es un objeto json
            con la información de un artículo de la Wikipedia

        NECESARIO PARA TODAS LAS VERSIONES

        dependiendo del valor de self.multifield y self.positional se debe ampliar el indexado


        """
        #DICT DOCS:
        self.docs[self.docid] = filename  
        self.use_positional = self.positional      

        

        for i, line in enumerate(open(filename)):
            j = self.parse_article(line)
             #j es un diccionario con todo el contenido de un articulo: 
            '''
            j = {
                "url" : "",
                "title": "",
                "summary": "",
                "all": "", titulo + resumen + secciones + subsecciones
                "section-name": "", nombre de todas las secciones y subsecciones
            }            
            '''

                
            #Rellenamos todas las estructuras de arriba:

            #SET URLS:            
            self.lini = len(self.urls)
            self.urls.add(j["url"]) #como es un set de conjuntos al hacer el add no repite url   (en el json hay urls repes entonces el add las obvia)
            self.fin = len(self.urls)

            
            #Identificar si hay url repetidas
            if self.lini == self.fin: self.urlRepetida = True
            else: self.urlRepetida = False
            
            #DICT ARTICLES:
            #hash de articulos --> clave entero (artid)
            # valor: la info necesaria para diferencia los artículos dentro de su fichero (la url, ya que no pueden haber urls repetidas en el mismo json)        
            
             
            if self.urlRepetida == False:
                """
                articles = {artid: docid,url,titulo,summary,all,section-name} #lo voy a guardar todo por si acaso
                """
                
               
                self.articles[self.artid] = {"docid": self.docid, "url": j['url'], "title": j["title"], "summary": j["summary"], "all": j["all"], "section-names": j["section-name"]}
                
            
                #DICT INDEX:
                #hash para el indice invertido de terminos --> clave: termino, valor: posting list (artids)
            
                # si se activa la función multifield
                if self.multifield: #todos los field se analizan
                    multifield = self.fields #inicializamos a una lista de tuplas con (field,bool)...
                else:          
                    multifield = [self.def_field]
            
                for (field, tokbool) in multifield: 
                    if tokbool: #comprobamos si este field se debe tokenizar
                        # extraemos todos los tokens de ese campo: obtenemos una lista de todas las palabras
                        tokensfield = self.tokenize(j[field])
                    else:
                        tokensfield = [j[field]] #el campo url no se tokeniza, pasamos la url tal cual metida en una lista
                        
                        
                    postoken = 0
                    for termino in tokensfield:
                        if field not in self.index:
                            self.index[field] = {} #creamos un diccionario para ese multifield
                        #si el token no esta en el diccionario del field
                        if termino not in self.index[field]:
                            if not self.positional:
                                self.index[field][termino] = {self.artid: 1} # si no estamos en posicional contamos ocurrencias 
                            else:
                                self.index[field][termino] = {self.artid: [postoken]} #si estamos en posicional, creamos una lista de postings (posiciones donde aparece el token)
                        
                        else: # si no existe la noticia en el token, se añade
                            if self.artid not in self.index[field][termino]:
                                if not self.positional:
                                    self.index[field][termino][self.artid] = 1
                                else:
                                    self.index[field][termino][self.artid] = [postoken]
                                    
                            else: # si no, se añade a la entrada del token-noticia la posición donde se ha encontrado
                                if not self.positional:
                                    self.index[field][termino][self.artid] += 1 #si no estamos en posicional, aumentamos en uno la ocurrencia del termino
                                else:
                                    self.index[field][termino][self.artid] += [postoken]   #si estamos en posicional, añadimos a la lista de posiciones la nueva posicion
                                                                
                        postoken += 1

            
            self.artid += 1
        
        self.docid += 1


    def set_stemming(self, v:bool):
        """

        Cambia el modo de stemming por defecto.
        
        input: "v" booleano.

        UTIL PARA LA VERSION CON STEMMING

        si self.use_stemming es True las consultas se resolveran aplicando stemming por defecto.

        """
        self.use_stemming = v


    def tokenize(self, text:str):
        """
        NECESARIO PARA TODAS LAS VERSIONES

        Tokeniza la cadena "texto" eliminando simbolos no alfanumericos y dividientola por espacios.
        Puedes utilizar la expresion regular 'self.tokenizer'.

        params: 'text': texto a tokenizar

        return: lista de tokens

        """
        return self.tokenizer.sub(' ', text.lower()).split()
    
        #self.tokenizer = re.compile("\W+") # expresion regular para hacer la tokenizacion
        #hace matching con los caracteres no alfabeticos, los sustituye con el sub por " ", lo pasa a minuscula y hace split obteniendo en un array las palabras


    def make_stemming(self):
        """

        Crea el indice de stemming (self.sindex) para los terminos de todos los indices.

        NECESARIO PARA LA AMPLIACION DE STEMMING.

        "self.stemmer.stem(token) devuelve el stem del token"


        """
        
        ####################################################
        ## COMPLETAR PARA FUNCIONALIDAD EXTRA DE STEMMING ##
        ####################################################

        # si se activa la función multifield
        if self.multifield:
            multifield = self.fields
        else:
            multifield = [self.def_field]

        for (field, tokbool) in multifield:
            # Se aplica stemming a cada token del self.index[field] y se añade al indice de stems
            # En este caso solo se guarda la noticia, no la posición
            #if tokbool: #si se ha tokenizado, el campo estará en self.index
            for token in self.index[field].keys():
                tokenStem = self.stemmer.stem(token) 
                # si el stem no esta en el diccionario de stemming creo entrada con ese token
                if field not in self.sindex:
                    self.sindex[field] = {}
                if tokenStem not in self.sindex[field]:
                    self.sindex[field][tokenStem] = [token]
                # si ya esta en el diccionario de stemming meto ese token
                elif token not in self.sindex[field][tokenStem]:
                    self.sindex[field][tokenStem].append(token)

    
    
    def make_permuterm(self):
        """

        Crea el indice permuterm (self.ptindex) para los terminos de todos los indices.

        NECESARIO PARA LA AMPLIACION DE PERMUTERM


        """
        
        ####################################################
        ## COMPLETAR PARA FUNCIONALIDAD EXTRA DE STEMMING ##
        ####################################################

        # si se activa la función multifield
        if self.multifield:
            multifield = self.fields
        else:
            multifield = [self.def_field]

        for (field, tokbool) in multifield:
            
            
                # se crea la lista de permuterms de un token
                # en este caso solo se guarda la noticia, no la posición
            for token in self.index[field]:
                tokenPermutado = token + '$'
                permuterm = []
                for i in range(len(tokenPermutado)):
                    tokenPermutado = tokenPermutado[1:] + tokenPermutado[0]
                    permuterm.append(tokenPermutado)

                # cuando tengo la lista de permutaciones itero sobre cada una
                for permut in permuterm:  
                    if field not in self.ptindex:
                        self.ptindex[field] = {}
                    # si esa permutacion no esta en el dicc de permuterm creo entrada y meto el token
                    if permut not in self.ptindex[field]:
                        self.ptindex[field][permut] = [token]
                    # si esa permutacion esta en el dicc de permuterm meto el token
                    else:
                        if token not in self.ptindex[field][permut]:
                            self.ptindex[field][permut].append(token)




    def show_stats(self):
        """
        NECESARIO PARA TODAS LAS VERSIONES
        
        Muestra estadisticas de los indices
        
        """
        if self.multifield:
            multifield = self.fields
        else:
            multifield = [self.def_field]
        print("\n" + '='*40)
        print("Number of indexed files: {}".format(len(self.docs)))
        
        print('-'*40)
        print("Number of indexed articles: {}".format(len(self.articles)))
        print('-'*40)
        print("TOKENS:")
        for (field,tokbool) in multifield:
           
            print('\t # of tokens in \'{}\': {}'.format(
            field, len(self.index[field])))
        print('-'*40)
        print("PERMUTERMS:")
        if self.permuterm:
            for (field,tokbool) in multifield:                
                print('\t # of permuterms in \'{}\': {}'.format(
                field, len(self.ptindex[field])))
        print('-'*40)
        print("STEMS:")
        if self.stemming:
            for (field, tokbool) in multifield:                
                print('\t # of stems in \'{}\': {}'.format(
                field, len(self.sindex[field])))
        print('-'*40)
        if self.use_positional: print("Positional queries are allowed.")
        else: print("Positional queries are NOT allowed")
        print('='*40)
        
        ########################################
        ## COMPLETAR PARA TODAS LAS VERSIONES ##
        ########################################

        



    #################################
    ###                           ###
    ###   PARTE 2: RECUPERACION   ###
    ###                           ###
    #################################

    ###################################
    ###                             ###
    ###   PARTE 2.1: RECUPERACION   ###
    ###                             ###
    ###################################


    def solve_query(self, query:str, prev:Dict={}):
        """
        NECESARIO PARA TODAS LAS VERSIONES

        Resuelve una query.
        Debe realizar el parsing de consulta que sera mas o menos complicado en funcion de la ampliacion que se implementen


        param:  "query": cadena con la query
                "prev": incluido por si se quiere hacer una version recursiva. No es necesario utilizarlo.


        return: posting list con el resultado de la query

        """

        if query is None or len(query) == 0:
            return []

        ########################################
        ## COMPLETAR PARA TODAS LAS VERSIONES ##
        ########################################

        if self.primeraiteracion == 0:
            self.queryInicial = query

        res = []
        # preproceso de la consulta para dejarla como quiero
        # meto espacios para partir y hacer una lista
        query = query.replace('"', '')                      
        query = query.replace('(', ' ( ')
        query = query.replace(')', ' ) ')
        
        lista = query.split() #aqui tengo la lista de la consulta que me dan

        # bucle con los extra
        i = 0 #iteramos
        while i < len(lista):
            self.primeraiteracion = 1
            terminoProcesado = lista[i]
            # consultas con parentesis de forma iterativa
            if terminoProcesado == '(':
                i += 1 # miramos el siguiente elemento de la consulta guardar su contenido haciendo iteraciones
                query2 = '' # la consulta que formas cuando procesas los parentesis de aperturas y cierres
                aux = 0 # para contar cuando se cierran los parentesis
                while aux >= 0:
                    if lista[i] == '(':
                        aux += 1 # otro parentesis de apertura
                    if lista[i] == ')':
                        aux -= 1 # otro parentesis de cierre
                    query2 += lista[i] + ' ' # guardo subconsulta
                    i += 1
                query2 = query2.strip() # quito el ultimo espacio
                query2 = query2[0:len(query2) - 1] # QUITO EL ULTIMO PARENTESIS DEL FINAL PARA QUE ME QUEDE LA CONSULTA LIMPIA
                res.append(self.solve_query(query2)) # llamada recursiva
            else:
                # multifield
                if ':' in terminoProcesado:
                    multifield = terminoProcesado[0:terminoProcesado.find(':')] # en que parte busco, ejemplo: en el title, summary, section...
                    terminoProcesado = terminoProcesado[terminoProcesado.find(':') + 1:] # actualizo temino a procesar 
                    # "tittle: pepe"     multifield = tittle     terminoProcesado = pepe
                else:
                    multifield = self.def_field[0]

                # distinguir para luego hacer las funciones básicas (CODIFICACION DE LOS OPERADORES)
                if terminoProcesado == 'AND':
                    res.append(0)
                    i += 1
                elif terminoProcesado == 'OR':
                    res.append(1)
                    i += 1
                elif terminoProcesado == 'NOT':
                    res.append(2)
                    i += 1
                else:
                    # permuterm
                    terminoProcesado = terminoProcesado.lower() # pasar a minus
                    if '*' in terminoProcesado or '?' in terminoProcesado:
                        res.append(self.get_permuterm(terminoProcesado, multifield))
                        i += 1                    
                    else:
                        # consultas posicionales
                        aux = 0
                        frase = [] # EJEMPLO "fin de semana" busca todo eso en ese orden
                        while (i + aux) < len(lista) and lista[i + aux] != 'AND' and lista[i + aux] != 'OR' and lista[i + aux] != 'NOT':
                            frase.append(lista[i + aux])
                            aux += 1
                            # de esta manera nos quedamos con la frase entera a buscar
                        if len(frase) == 1:
                            palabra = '"' + frase[0] + '"'
                            if palabra in self.queryInicial: #si es posicional de una palabra se comprueba si estaba en la query inicial, cuentas los artid que haya en ese termino
                                res.append(list(self.index[multifield][terminoProcesado].keys()))
                                i += 1
                                # uso de stemming no se aplica a las busquedas posicionales
                            else:
                                res.append(self.get_posting(terminoProcesado, multifield))
                                i += 1
                        else:
                            res.append(self.get_positionals(frase, multifield))
                            i += aux


        # bucle con funcionalidades básicas
        sol = [] # resultados finales de la consulta
        i = 0
        while i < len(res): #lista de resultados
            # iteramos sobre la lista res de resultados para hacer las funciones correspondientes
            if res[i] == 0: #AND
                if res[i + 1] == 2: # si tenemos el caso AND NOT
                    next = self.reverse_posting(res[i + 2])
                    i += 3 # adelanto tres pos
                else:
                    next = res[i + 1]
                    i += 2 # adelanto dos pos
                
                sol = self.and_posting(sol, next)

            elif res[i] == 1: #OR
                if res[i + 1] == 2: # si tenemos el caso OR NOT
                    next = self.reverse_posting(res[i + 2])
                    i += 3 # adelanto tres pos
                else:
                    next = res[i + 1]
                    i += 2 # adelanto dos pos

                sol = self.or_posting(sol, next)

            elif res[i] == 2: #NOT
                sol = self.reverse_posting(res[i + 1])
                i += 2 # adelanto dos pos

            else:
                sol = res[i] # si no es operador sigues al siguiente termino
                i += 1

        self.primeraiteracion = 0
        return sol




    def get_posting(self, term:str, field:Optional[str]=None):
        """

        Devuelve la posting list asociada a un termino. 
        Dependiendo de las ampliaciones implementadas "get_posting" puede llamar a:
            - self.get_positionals: para la ampliacion de posicionales
            - self.get_permuterm: para la ampliacion de permuterms
            - self.get_stemming: para la amplaicion de stemming


        param:  "term": termino del que se debe recuperar la posting list.
                "field": campo sobre el que se debe recuperar la posting list, solo necesario si se hace la ampliacion de multiples indices

        return: posting list
        
        NECESARIO PARA TODAS LAS VERSIONES

        """
        ########################################
        ## COMPLETAR PARA TODAS LAS VERSIONES ##
        ########################################
        posting = []

        # posting permuterm
        if '*' in term or '?' in term:
            posting = self.get_permuterm(term, field)
        # posting stem
        elif self.use_stemming:
            posting = self.get_stemming(term, field)
        # posting positional
        elif self.use_positional:
            posting = self.get_positionals(term, field)
        else:
            if term in self.index[field]:
                posting = list(self.index[field][term].keys())

        return posting



    def get_positionals(self, terms:list, field): #hemos modificado (terms:str --> terms:list)
        """

        Devuelve la posting list asociada a una secuencia de terminos consecutivos.
        NECESARIO PARA LA AMPLIACION DE POSICIONALES

        param:  "terms": lista con los terminos consecutivos para recuperar la posting list.
                "field": campo sobre el que se debe recuperar la posting list, solo necesario se se hace la ampliacion de multiples indices

        return: posting list

        """
        ########################################################
        ## COMPLETAR PARA FUNCIONALIDAD EXTRA DE POSICIONALES ##
        ########################################################

        if ':' in terms[0]:
            terms[0]=str.split(terms[0],':')[-1]
        
        '''
        aux = {
            artId1: {
                pos_0[0]
                pos_0[1]
                ...
            }
            artId2:
            ...
        }
        '''
        
        # lista de posting en la que aparecen todos los términos de la frase
        postings = list(self.index[field][terms[0]].keys())
        for i in range(1,len(terms)):
            p2 = list(self.index[field][terms[i]].keys())
            postings = self.and_posting(postings,p2)

        res = []
        for artId in postings:
            aux = list(self.index[field][terms[0]][artId])
            for i in range(1,len(terms)):
                aux = self.and_posting(aux, [x - i for x in self.index[field][terms[i]][artId]])
            if len(aux) != 0:
                res.append(artId) 
            
        return res

    def get_stemming(self, term:str, field: Optional[str]=None):
        """

        Devuelve la posting list asociada al stem de un termino.
        NECESARIO PARA LA AMPLIACION DE STEMMING

        param:  "term": termino para recuperar la posting list de su stem.
                "field": campo sobre el que se debe recuperar la posting list, solo necesario se se hace la ampliacion de multiples indices
        
        return: posting list

        """
        
        stem = self.stemmer.stem(term)

        ####################################################
        ## COMPLETAR PARA FUNCIONALIDAD EXTRA DE STEMMING ##
        ####################################################

        posting = []

        # unión de las posting de cada termino que contenga la entrada en el indice de stems
        if stem in self.sindex[field]:

            for token in self.sindex[field][stem]:
                posting = self.or_posting(posting,list(self.index[field][token].keys()))
        return posting
    

    def get_permuterm(self, term:str, field:Optional[str]=None):
        """

        Devuelve la posting list asociada a un termino utilizando el indice permuterm.
        NECESARIO PARA LA AMPLIACION DE PERMUTERM

        param:  "term": termino para recuperar la posting list, "term" incluye un comodin (* o ?).
                "field": campo sobre el que se debe recuperar la posting list, solo necesario se se hace la ampliacion de multiples indices

        return: posting list

        """
        def postinglist(term:str,field:str):
            posting = list(self.index[field][term].keys())
            return posting

        ##################################################
        ## COMPLETAR PARA FUNCIONALIDAD EXTRA PERMUTERM ##
        ##################################################
        posting = []

        term += '$'
        while term[-1] != '*' and term[-1] != '?':
            term = term[1:] + term[0]

        simbolo = term[-1]
        term = term[:-1]

        for permuterm in self.ptindex[field].keys():
            if permuterm.startswith(term) and (simbolo == '*' or len(permuterm) == len(term) + 1): # se comprueba que sea ese el permuterm y que el simb sea o * o ?
                for token in self.ptindex[field][permuterm]:
                    posting = self.or_posting(posting, postinglist(token, field))
        
        return posting



    def reverse_posting(self, p:list):
        """
        NECESARIO PARA TODAS LAS VERSIONES

        Devuelve una posting list con todas las noticias excepto las contenidas en p.
        Util para resolver las queries con NOT.


        param:  "p": posting list


        return: posting list con todos los artid exceptos los contenidos en p

        """
        
        #esta operación sería equivalente a p1 AND (NOT P2)
        p1 = list(self.articles.keys()) #lista de todos los articulos
        res=[]
        p2 = p #lista de los articulos que no tienen q aparecer
        i = j = 0
        while i < len(p1) and j < len(p2): #mientras no llegamos al final de las dos listas a la vez
            if p1[i] == p2[j]: #si los artid son iguales, avanzamos los 2 punteros
                i += 1
                j += 1
            elif p1[i] < p2[j]: #si el artid de p1 es menor que el de p2, añadimos el artid a res y avanzamos el puntero de p1
                res.append(p1[i])
                i += 1
            else: #si el artid de p1 es mayor que el de p2, ya sabemos que en p2 no habrá ningun artid que nos interese (las posting lists estan ordenadas de menor a mayor artid)
                j += 1
        
        while i < len(p1): # acabamos de volcar los artid de p1 sobre res
            res.append(p1[i])
            i += 1

        return res
        
        ########################################
        ## COMPLETAR PARA TODAS LAS VERSIONES ##
        ########################################



    def and_posting(self, p1:list, p2:list):
        """
        NECESARIO PARA TODAS LAS VERSIONES

        Calcula el AND de dos posting list de forma EFICIENTE

        param:  "p1", "p2": posting lists sobre las que calcular


        return: posting list con los artid incluidos en p1 y p2

        """
        
        #COMPLETAR
        respuesta = []
        i = j = 0
        while i < len(p1) and j < len(p2):  # mientras que el indice de busqueda sea menor a la longitud de las listas continuar
            if p1[i] == p2[j]:
                respuesta.append(p1[i])
                i += 1  # si son iguales se guardan en la lista "respuesta" y se avanzan los indices de ambas listas p1 y p2
                j += 1
            elif p1[i] < p2[j]: # en caso de que ser un valor menor el docID(p1) se avanza el indice de la lista p1
                i += 1
            else:  # en caso contrario se avanza el indice de la lista p2
                j += 1

        return respuesta
        #COMPLETADO



    def or_posting(self, p1:list, p2:list):
        """
        NECESARIO PARA TODAS LAS VERSIONES
        Calcula el OR de dos posting list de forma EFICIENTE
        param:  "p1", "p2": posting lists sobre las que calcular
        return: posting list con los artid incluidos de p1 o p2
        """

        ## COMPLETAR PARA TODAS LAS VERSIONES
        respuesta = []
        i = j = 0
        while i < len(p1) and j < len(p2):
            if p1[i] == p2[j]:
                respuesta.append(p1[i])
                i += 1
                j += 1
            elif p1[i] < p2[j]:
                respuesta.append(p1[i])
                i += 1
            else:
                respuesta.append(p2[j])
                j += 1

        while i < len(p1):
            respuesta.append(p1[i])
            i += 1

        while j < len(p2):
            respuesta.append(p2[j])
            j += 1

        return respuesta
        # COMPLETADO


    def minus_posting(self, p1, p2):
        """
        OPCIONAL PARA TODAS LAS VERSIONES

        Calcula el except de dos posting list de forma EFICIENTE.
        Esta funcion se incluye por si es util, no es necesario utilizarla.

        param:  "p1", "p2": posting lists sobre las que calcular


        return: posting list con los artid incluidos de p1 y no en p2

        """
        result = []
        i = j = 0
        while i < len(p1) and j < len(p2):
            if p1[i] < p2[j]:
                result.append(p1[i])
                i += 1
            elif p1[i] > p2[j]:
                j += 1
            else:
                i += 1
                j += 1
        while i < len(p1):
            result.append(p1[i])
            i += 1
        return result
            
        ########################################################
        ## COMPLETAR PARA TODAS LAS VERSIONES SI ES NECESARIO ##
        ########################################################





    #####################################
    ###                               ###
    ### PARTE 2.2: MOSTRAR RESULTADOS ###
    ###                               ###
    #####################################

    def solve_and_count(self, ql:List[str], verbose:bool=True) -> List:
        results = []
        for query in ql:
            if len(query) > 0 and query[0] != '#':
                r = self.solve_query(query)
                results.append(len(r))
                if verbose:
                    print(f'{query}\t{len(r)}')
            else:
                results.append(0)
                if verbose:
                    print(query)
        return results


    def solve_and_test(self, ql:List[str]) -> bool:
        errors = False
        for line in ql:
            if len(line) > 0 and line[0] != '#':
                query, ref = line.split('\t')
                reference = int(ref)
                result = len(self.solve_query(query))
                if reference == result:
                    print(f'{query}\t{result}')
                else:
                    print(f'>>>>{query}\t{reference} != {result}<<<<')
                    errors = True                    
            else:
                print(line)
        return not errors


    def solve_and_show(self, query:str):
        """
        NECESARIO PARA TODAS LAS VERSIONES

        Resuelve una consulta y la muestra junto al numero de resultados 

        param:  "query": query que se debe resolver.

        return: el numero de artículo recuperadas, para la opcion -T

        """
        
        
        
        result = self.solve_query(query)
        print('QUERY:{} | NÚMERO RESULTADOS:{}'.format(query,len(result)))

        
    
        ########################################
        ## COMPLETAR PARA TODAS LAS VERSIONES ##
        ########################################
        
        print("=" * 40)
        
        if self.show_all:
            nr = 1
            for r in result:
                print("\n")
                print(str(nr) + "->" + "\t Identificador del artículo: " + str(r) + "\t url:" + str(self.articles[r]["url"]))
                print("Título del artículo: " + self.articles[r]["title"])
                
                if self.show_snippet:
                    print("Snippets:")
                    print(self.get_snippets(query,r))
                
                nr = nr + 1
        else:
            nr = 1
            for r in result[:min(self.SHOW_MAX,len(result))]:
                print("\n")
                print(str(nr) + "->" + "\t Identificador del artículo: " + str(r) + "\t url:" + str(self.articles[r]["url"]))
                print("Título del artículo: " + self.articles[r]["title"])
                
                if self.show_snippet:
                    print("Snippets:")
                    print(self.get_snippets(query,r))
                
                nr = nr + 1
                
        print("=" * 40)
        

    def get_snippets(self, terms, artid):
        """
        Método auxiliar usado

        """

        # Dividir el texto en palabras individuales
        tokens = self.tokenize(self.articles[artid]["all"])
        words = tokens

        # Encontrar la posición de la consulta en el texto
        
        posiciones = []
        pos=0
        terms = terms.split()
        for t in terms:           
            if t not in {"AND","NOT","OR"}: 
                for i,tok in enumerate(tokens):
                    if tok == t:
                        pos = i
                        posiciones.append(pos)                 
        
        snippet = "... "
        for p in posiciones:  
            for j in range(max((p - 5), 0), min(p + 5, len(tokens) - 1)):
                snippet += words[j] + " "        
            snippet += "... "         
            
        return snippet

        






            

