#! -*- encoding: utf8 -*-
import heapq as hq

from typing import Tuple, List, Optional, Dict, Union

import requests
import bs4
import re
from urllib.parse import urljoin
import json
import math
import os

##### AUTORES #####
# Brian Valiente Ródenas
# Adrián Camacho García
# Ana Gutiérrez Mandingorra 
# Marta Jimenez Montalva 
# Luis Miguel Carmona Pérez


#EJECUTAR:
# python SAR_Crawler.py --out-base-filename ana.json --batch-size 50 --initial-url https://es.wikipedia.org/wiki/Videojuego --document-limit 200 --max-depth-level 3
# python SAR_Crawler.py --out-base-filename ana.json --batch-size 50 --initial-url https://es.wikipedia.org/wiki/1982 --document-limit 200 --max-depth-level 3

class SAR_Wiki_Crawler:

    def __init__(self):
        # Expresión regular para detectar si es un enlace de la Wikipedia
        self.wiki_re = re.compile(r"(http(s)?:\/\/(es)\.wikipedia\.org)?\/wiki\/[\w\/_\(\)\%]+")
        # Expresión regular para limpiar anclas de editar
        self.edit_re = re.compile(r"\[(editar)\]")
        # Formato para cada nivel de sección
        self.section_format = {
            "h1": "##{}##",
            "h2": "=={}==",
            "h3": "--{}--"
        }

        # Expresiones regulares útiles para el parseo del documento
        self.title_sum_re = re.compile(r"##(?P<title>.+)##\n(?P<summary>((?!==.+==).+|\n)+)(?P<rest>(.+|\n)*)")
        self.sections_re = re.compile(r"==.+==\n")
        self.section_re = re.compile(r"==(?P<name>.+)==\n(?P<text>((?!--.+--).+|\n)*)(?P<rest>(.+|\n)*)")
        self.subsections_re = re.compile(r"--.+--\n")
        self.subsection_re = re.compile(r"--(?P<name>.+)--\n(?P<text>(.+|\n)*)")
        
        #REGEX CREADOS POR NOSOTROS:       
        self.sections2_re = re.compile(r"==(?P<name>.+)==\n(?P<rest>((?!==.+==).+|\n)*)")        
        self.subsections2_re = re.compile(r"--(?P<name>.+)--\n(?P<rest>((?!--.+--).+|\n)*)")
        


    def is_valid_url(self, url: str) -> bool:
        """Verifica si es una dirección válida para indexar

        Args:
            url (str): Dirección a verificar

        Returns:
            bool: True si es valida, en caso contrario False
        """
        return self.wiki_re.fullmatch(url) is not None


    def get_wikipedia_entry_content(self, url: str) -> Optional[Tuple[str, List[str]]]:
        """Devuelve el texto en crudo y los enlaces de un artículo de la wikipedia

        Args:
            url (str): Enlace a un artículo de la Wikipedia

        Returns:
            Optional[Tuple[str, List[str]]]: Si es un enlace correcto a un artículo
                de la Wikipedia en inglés o castellano, devolverá el texto y los
                enlaces que contiene la página.

        Raises:
            ValueError: En caso de que no sea un enlace a un artículo de la Wikipedia
                en inglés o español
        """
        if not self.is_valid_url(url):
            raise ValueError((
                f"El enlace '{url}' no es un artículo de la Wikipedia en español"
            ))

        try:
            req = requests.get(url)
        except Exception as ex:
            print(f"ERROR: - {url} - {ex}")
            return None


        # Solo devolvemos el resultado si la petición ha sido correcta
        if req.status_code == 200:
            soup = bs4.BeautifulSoup(req.text, "lxml")
            urls = set()

            for ele in soup.select((
                'div#catlinks, div.printfooter, div.mw-authority-control'
            )):
                ele.decompose()

            # Recogemos todos los enlaces del contenido del artículo
            for a in soup.select("div#bodyContent a", href=True):
                href = a.get("href")
                if href is not None:
                    urls.add(href)

            # Contenido del artículo
            content = soup.select((
                "h1.firstHeading,"
                "div#mw-content-text h2,"
                "div#mw-content-text h3,"
                "div#mw-content-text h4,"
                "div#mw-content-text p,"
                "div#mw-content-text ul,"
                "div#mw-content-text li,"
                "div#mw-content-text span"
            ))

            dedup_content = []
            seen = set()

            for element in content:
                if element in seen:
                    continue

                dedup_content.append(element)

                # Añadimos a vistos, tanto el elemento como sus descendientes
                for desc in element.descendants:
                    seen.add(desc)

                seen.add(element)

            text = "\n".join(
                self.section_format.get(element.name, "{}").format(element.text)
                for element in dedup_content
            )

            # Eliminamos el texto de las anclas de editar
            text = self.edit_re.sub('', text)

            return text, sorted(list(urls))

        return None


    def parse_wikipedia_textual_content(self, text: str, url: str) -> Optional[Dict[str, Union[str,List]]]:
        """Devuelve una estructura tipo artículo a partir del text en crudo

        Args:
            text (str): Texto en crudo del artículo de la Wikipedia
            url (str): url del artículo, para añadirlo como un campo

        Returns:

            Optional[Dict[str, Union[str,List[Dict[str,Union[str,List[str,str]]]]]]]:

            devuelve un diccionario con las claves 'url', 'title', 'summary', 'sections':
                Los valores asociados a 'url', 'title' y 'summary' son cadenas,
                el valor asociado a 'sections' es una lista de posibles secciones.
                    Cada sección es un diccionario con 'name', 'text' y 'subsections',
                        los valores asociados a 'name' y 'text' son cadenas y,
                        el valor asociado a 'subsections' es una lista de posibles subsecciones
                        en forma de diccionario con 'name' y 'text'.

            en caso de no encontrar título o resúmen del artículo, devolverá None

        """
        def clean_text(txt):
            return '\n'.join(l for l in txt.split('\n') if len(l) > 0)

        document = None

        # COMPLETAR
        
        document = {
            "url" : "",
            "title" : "",
            "summary" : "",
            "sections" : []
        }

        '''
        section = {
            "name" : "",
            "text" : "",
            "subsections" : []
        }

        subsection = {
            "name" : "",
            "text" : ""
        }
        '''
        
        # limpiamos el texto para pasarlo al formato que queremos
        #quitamos las lineas en blanco        
        doclimpio = clean_text(text)

            
        document['url'] = url

        # Sacamos del texto limpio las demas secciones       
        
        match = self.title_sum_re.search(doclimpio) #title - sum - rest
        
        document['title'] = match.group('title') if match else None
        summary = match.group("summary")
        document['summary'] = match.group('summary') if summary else None        
        rest = match.group('rest')
        
        #Sacamos las sections
        nombres_sections = self.sections_re.findall(rest) #sacamos todos los nombres de las secciones
        
        sections = self.sections2_re.findall(rest) 
        
        #sect es una tupla (name, rest)
        for i,sect in enumerate(sections):
            
            
            #esto es para emplear section_r en el regex anterior
            s = self.section_re.search("=="+sect[0]+"==\n"+sect[1]) #aquí le pasas que busque la estructura name - text - res en todo el texto de la seccion
            document['sections'].append({
                "name" : s.group('name'),
                "text" : s.group('text'),
                "subsections" : []
            })

            #buscamos subsections de esta seccion
            subsections = self.subsections2_re.findall(s.group('rest')) 
            for j,subsec in enumerate(subsections):
                ss = self.subsection_re.search("--"+subsec[0]+"--\n"+subsec[1]) #aquí le pasas que busque la estructura name - text en todo el resto de la seccion
                document['sections'][i]['subsections'].append({
                    "name" : ss.group('name'),
                    "text" : ss.group('text')
                })
                
        # fin de COMPLETAR

        return document


    def save_documents(self,
        documents: List[dict], base_filename: str,
        num_file: Optional[int] = None, total_files: Optional[int] = None
    ):
        """Guarda una lista de documentos (text, url) en un fichero tipo json lines
        (.json). El nombre del fichero se autogenera en base al base_filename,
        el num_file y total_files. Si num_file o total_files es None, entonces el
        fichero de salida es el base_filename.

        Args:
            documents (List[dict]): Lista de documentos.
            base_filename (str): Nombre base del fichero de guardado.
            num_file (Optional[int], optional):
                Posición numérica del fichero a escribir. (None por defecto)
            total_files (Optional[int], optional):
                Cantidad de ficheros que se espera escribir. (None por defecto)
        """
        assert base_filename.endswith(".json")

        if num_file is not None and total_files is not None:
            # Separamos el nombre del fichero y la extensión
            base, ext = os.path.splitext(base_filename)
            # Padding que vamos a tener en los números
            padding = len(str(total_files))

            out_filename = f"{base}_{num_file:0{padding}d}_{total_files}{ext}"            

        else:
            out_filename = base_filename

        with open(out_filename, "w", encoding="utf-8", newline="\n") as ofile:
            for doc in documents:
                print(json.dumps(doc, ensure_ascii=True), file=ofile)


    def start_crawling(self, 
                    initial_urls: List[str], document_limit: int,
                    base_filename: str, batch_size: Optional[int], max_depth_level: int,
                    ):        
         

        """Comienza la captura de entradas de la Wikipedia a partir de una lista de urls válidas, 
            termina cuando no hay urls en la cola o llega al máximo de documentos a capturar.
        
        Args:
            initial_urls: Direcciones a artículos de la Wikipedia
            document_limit (int): Máximo número de documentos a capturar
            base_filename (str): Nombre base del fichero de guardado.
            batch_size (Optional[int]): Cada cuantos documentos se guardan en
                fichero. Si se asigna None, se guardará al finalizar la captura.
            max_depth_level (int): Profundidad máxima de captura.
        """

        # URLs válidas, ya visitadas (se hayan procesado, o no, correctamente)
        #en visited nosotros guardamos SOLO aquellas url que han sido procesadas
        visited = set()  
        # URLs en cola (procesadas y no procesadas aun)
        to_process = set(initial_urls)
        # Direcciones a visitar'''
        queue = [(0, "", url) for url in to_process] #asigna la misma prioridad a todos los elementos
        hq.heapify(queue)
        # Buffer de documentos capturados
        documents: List[dict] = []
        # Contador del número de documentos capturados
        total_documents_captured = 0 
        # Contador del número de ficheros escritos
        files_count = 0

        
        # En caso de que no utilicemos bach_size, asignamos None a total_files
        # así el guardado no modificará el nombre del fichero base
        if batch_size is None:
            total_files = None
        else:
            # Suponemos que vamos a poder alcanzar el límite para la nomenclatura
            # de guardado
            total_files = math.ceil(document_limit / batch_size)

        # COMPLETAR
        # Tiene que cumplirse esto: len(initial_urls) >= document_limit and len(initial_urls) not 0

        
        unaURL = len(queue) == 1  # si solamente se tiene que procesar una url

        while total_documents_captured < document_limit and len(queue) != 0:  # se procesan tantos documentos como limite de documentos se haya establecido
            profundidad, sep, urlAprocesar = hq.heappop(queue)  # coger url de mayor prioridad y guardarte en variables dichos datos
            #print("Profundidad actual: ", profundidad)

            if urlAprocesar not in visited: #si la url no se ha procesado antes               
                text, enlaces = self.get_wikipedia_entry_content(urlAprocesar)  # se procesa la url: devuelve el texto y los enlaces de esa pagina
                visited.add(urlAprocesar)  #guardas la url procesada en visited (en las ya procesadas)

                if unaURL and profundidad < max_depth_level:  # si initialurls solo tiene 1 url y la prof es menor que el max hacer esto -> si solo se le pasa una url tiene que buscar por profundidad, 
                    #si se le pasa un archivo de urls no busca solo crawlea las del archivo
                    for e in enlaces:  # recorro lista de enlaces del url en cuestion
                        #if self.is_valid_url(e): 
                            #print("La url es válida") # hay que comprobar que sea una url válida
                        if e not in to_process and self.is_valid_url(e):  # si la nueva url no esta en la lista a procesar, entonces se añade a ella
                            # PROBLEMA: hay algunas URLs que son válidas pero no tienen el formato correcto para ser procesadas (el formato correcto es con el prefijo de wiki delante),
                            # entonces lo que hacemos es normalizarlas si no lo están (añadirle el prefijo https://es.wikipedia.org), porque sino no se puede hacer la busqueda
                            if 'https://es.wikipedia.org' not in e:  
                               # print("Sin normalizar: ", e)
                                e = 'https://es.wikipedia.org' + e
                               # print("Normalizada: ", e)
                            #print("Se añade una url con profundidad: ", profundidad + 1)
                            to_process.add(e)  # añado url a la lista a procesar
                            hq.heappush(queue, ((profundidad + 1), "", e))  # se transforma la url a meter en la lista de prioridad al formato (profundidad, separador, url) y se introduce en la cola de prioridad
            else:
                print("Esta url ya ha sido procesada con antelación: ", urlAprocesar)

            documents.append(self.parse_wikipedia_textual_content(text, urlAprocesar))  # le añades el diccionario
            total_documents_captured = total_documents_captured + 1

        self.save_documents(documents, base_filename, total_files)  # se pasa la lista de diccionarios, el nombre de fichero, el indice del nombre del archivo, el numero total de archivos json a crear/almacenar
        files_count = total_files 

        ##finde COMPLETAR


    def wikipedia_crawling_from_url(self,
        initial_url: str, document_limit: int, base_filename: str,
        batch_size: Optional[int], max_depth_level: int
    ):
        """Captura un conjunto de entradas de la Wikipedia, hasta terminar
        o llegar al máximo de documentos a capturar.
        
        Args:
            initial_url (str): Dirección a un artículo de la Wikipedia
            document_limit (int): Máximo número de documentos a capturar
            base_filename (str): Nombre base del fichero de guardado.
            batch_size (Optional[int]): Cada cuantos documentos se guardan en
                fichero. Si se asigna None, se guardará al finalizar la captura.
            max_depth_level (int): Profundidad máxima de captura.
        """
        if not self.is_valid_url(initial_url) and not initial_url.startswith("/wiki/"):
            raise ValueError(
                "Es necesario partir de un artículo de la Wikipedia en español"
            )

        self.start_crawling(initial_urls=[initial_url], document_limit=document_limit, base_filename=base_filename,
                            batch_size=batch_size, max_depth_level=max_depth_level)



    def wikipedia_crawling_from_url_list(self,
        urls_filename: str, document_limit: int, base_filename: str,
        batch_size: Optional[int]
    ):
        """A partir de un fichero de direcciones, captura todas aquellas que sean
        artículos de la Wikipedia válidos

        Args:
            urls_filename (str): Lista de direcciones
            document_limit (int): Límite máximo de documentos a capturar
            base_filename (str): Nombre base del fichero de guardado.
            batch_size (Optional[int]): Cada cuantos documentos se guardan en
                fichero. Si se asigna None, se guardará al finalizar la captura.

        """

        urls = []
        with open(urls_filename, "r", encoding="utf-8") as ifile:
            for url in ifile:
                url = url.strip()

                # Comprobamos si es una dirección a un artículo de la Wikipedia
                if self.is_valid_url(url):
                    if not url.startswith("http"):
                        raise ValueError(
                            "El fichero debe contener URLs absolutas"
                        )

                    urls.append(url)

        urls = list(set(urls)) # eliminamos posibles duplicados

        self.start_crawling(initial_urls=urls, document_limit=document_limit, base_filename=base_filename,
                            batch_size=batch_size, max_depth_level=0)





if __name__ == "__main__":
    raise Exception(
        "Esto es una librería y no se puede usar como fichero ejecutable"
    )
