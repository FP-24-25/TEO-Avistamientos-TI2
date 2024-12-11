'''
Módulo avistamientos
Adaptación del notebook a proyecto: Toñi Reina
'''
import csv
from datetime import date, datetime
import math
from typing import NamedTuple
from collections import Counter, defaultdict
from coordenadas import Coordenadas, distancia_harvesine, redondear, distancia
from parsers import parse_datetime
import statistics
import locale

## Definición de tipos
Avistamiento = NamedTuple('Avistamiento', [
    ('fechahora', datetime),
    ('ciudad', str),
    ('estado', str),
    ('forma', str),
    ('duracion', int),
    ('comentarios', str),
    ('ubicacion', Coordenadas)
])

## 1. Operaciones de carga de datos
### 1.1 Función de lectura de datos
# Función de lectura que crea una lista de avistamientos
def lee_avistamientos(fichero :str) -> list[Avistamiento]:
    '''
    Lee un fichero de entrada y devuelve una lista de tuplas. 
    Para convertir la cadena con la fecha y la hora al tipo datetime, usar
        datetime.strptime(fecha_hora,'%m/%d/%Y %H:%M')    
    
    @param fichero: ruta del fichero csv que contiene los datos en codificación utf-8 
    @type fichero: str
    @return: lista de tuplas con la información de los avistamientos 
    @rtype: [Avistamiento(datetime, str, str, str, str, int, str, Coordenadas(float, float))]   
    '''
    with open(fichero, encoding="utf-8") as f:
        res = []
        lector = csv.reader(f)
        next(lector)
        for fechahora, ciudad, estado, forma, duracion, comentarios, latitud, longitud in lector:
            fechahora = datetime.strptime(fechahora, "%m/%d/%Y %H:%M")
            duracion = int(duracion)
            ubicacion = Coordenadas(float(latitud), float(longitud))
            tupla = Avistamiento(fechahora, ciudad, estado, forma, duracion, comentarios, ubicacion)
            res.append(tupla)
        return res
    
### 2.1 Número de avistamientos producidos en una fecha
def numero_avistamientos_fecha(avistamientos: list[Avistamiento], fecha: datetime.date) -> int:
    ''' Avistamientos que se han producido en una fecha
    
    Toma como entrada una lista de avistamientos y una fecha.
    Devuelve el número de avistamientos que se han producido en esa fecha.

    @param avistamientos: lista de avistamientos
    @type avistamientos: [Avistamiento(datetime, str, str, str, int, str, Coordenadas(float, float))]
    @param fecha: fecha del avistamiento 
    @type fecha: datetime.date
    @return:  Número de avistamientos producidos en la fecha 
    @rtype: int
    
    '''
    contador = 0
    for a in avistamientos:
        if a.fechahora.date() == fecha:
            contador += 1
    return contador


# Por comprensión
def numero_avistamientos_fecha2(avistamientos: list[Avistamiento], fecha: datetime.date) -> int:
    return len([None for a in avistamientos if a.fechahora.date() == fecha])

### 2.2 Número de formas observadas en un conjunto de estados
### PARA CASA
def formas_estados(avistamientos: list[Avistamiento], estados: set[str]) -> int:
    ''' 
    Devuelve el número de formas distintas observadas en avistamientos 
    producidos en alguno de los estados especificados.
    @param avistamientos: lista de tuplas con la información de los avistamientos
    @type avistamientos: [Avistamiento(datetime, str, str, str, int, str, Coordenadas(float, float)))]
    @param estados: conjunto de estados para los que se quiere hacer el cálculo 
    @type estados: {str}
    @return: Número de formas distintas observadas en los avistamientos producidos
         en alguno de los estados indicados por el parámetro "estados"
    @rtype: int
    '''
    conjunto_formas = set()
    for a in avistamientos:
        if a.estado in estados:
            conjunto_formas.add(a.forma)
    return len(conjunto_formas)

def formas_estados2(avistamientos: list[Avistamiento], estados: set[str]) -> int:
    # Por comprensión
    return len({a.forma for a in avistamientos if a.estado in estados})
    
### 2.3 Duración total de los avistamientos en un estado
### PARA CASA
def duracion_total(avistamientos: list[Avistamiento], estado: str) -> int:
    ''' 
    Devuelve la duración total de los avistamientos de un estado. 
    
    @param avistamientos: lista de tuplas con la información de los avistamientos 
    @type avistamientos: [Avistamiento(datetime, str, str, str, int, str, Coordenadas(float, float)))]
    @param estado: estado para el que se quiere hacer el cálculo
    @type estado: str
    @return: duración total en segundos de todos los avistamientos del estado 
    @rtype: int
    '''
    duracion = 0
    for a in avistamientos:
        if a.estado == estado:
            duracion += a.duracion
    return duracion

def duracion_total2(avistamientos: list[Avistamiento], estado: str) -> int:
    ## Por compresión
    return sum(a.duracion for a in avistamientos if a.estado == estado)

### 2.4 Avistamientos cercanos a una ubicación
### PARA CASA
def avistamientos_cercanos_ubicacion(avistamientos: list[Avistamiento], ubicacion: Coordenadas, radio: float) -> set[Avistamiento]:
    ''' 
    Devuelve el conjunto de avistamientos cercanos a una ubicación.
    @param avistamientos: lista de tuplas con la información de los avistamientos
    @type avistamientos: [Avistamiento(datetime, str, str, str, int, str, Coordenadas(float, float)))]
    @param ubicacion: coordenadas de la ubicación para la cual queremos encontrar avistamientos cercanos 
    @type ubicacion: Coordenadas (float, float)
    @param radio: radio de distancia
    @param radio: float
    @return:Conjunto de avistamientos que se encuentran a una distancia
         inferior al valor "radio" de la ubicación dada por el parámetro "ubicacion" 
    @rtype: {Avistamiento(datetime, str, str, str, int, str, Coordenadas(float, float))}
    '''
    res = set()
    for a in avistamientos:
        if distancia(a.ubicacion, ubicacion) < radio:
            res.add(a)
    return res

def avistamientos_cercanos_ubicacion2(avistamientos: list[Avistamiento], ubicacion: Coordenadas, radio: float) -> set[Avistamiento]:
    ## Por compresión
    
    return {a for a in avistamientos if distancia(a.ubicacion, ubicacion) < radio}


## Operaciones con máximos y mínimos
### 3.1 Avistamiento de una forma con mayor duración

def avistamiento_mayor_duracion(avistamientos: list[Avistamiento], forma: str) -> Avistamiento:
    '''
    Devuelve el avistamiento de mayor duración de entre todos los
    avistamientos de una forma dada.
    @param avistamientos: lista de tuplas con la información de los avistamientos 
    @type [Avistamiento(datetime, str, str, str, int, str, Coordenadas(float, float))]
    @param forma: forma del avistamiento 
    @type forma: str
    @return:  avistamiento más largo de la forma dada
    @rtype: Avistamiento(datetime, str, str, str, int, str, Coordenadas(float, float))
    '''
    avistamientos_forma = []
    for a in avistamientos:
        if a.forma == forma:
            avistamientos_forma.append(a)

    return max(avistamientos_forma, key = lambda a:a.duracion)    

def avistamiento_mayor_duracion2(avistamientos: list[Avistamiento], forma: str) -> Avistamiento:
    # Por comprension
    return max(
        (a for a in avistamientos if a.forma == forma),
        key = lambda a:a.duracion
    )

### 3.2 Avistamiento cercano a un punto con mayor duración
### PARA CASA
def avistamiento_cercano_mayor_duracion(avistamientos: list[Avistamiento], coordenadas: Coordenadas, radio: float = 0.5) -> tuple[int, str]:
    '''
    Devuelve la duración y los comentarios del avistamiento que más 
    tiempo ha durado de aquellos situados en el entorno de las
    coordenadas que se pasan como parámetro de entrada.
    El resultado debe ser una tupla de la forma (duración, comentarios)
    
    @param avistamientos: lista de tuplas con la información de los avistamientos 
    @type [Avistamiento(datetime, str, str, str, int, str, Coordenadas(float, float))]
    @param coordenadas: tupla con latitud y longitud
    @type coordenadas: Coordenadas (float, float)
    @param radio: radio de búsqueda
    @type radio: float
    @return: duración y comentarios del avistamiento más largo en el entorno de las coordenadas comentarios del avistamiento más largo
    @rtype: int, str
    '''
    cercanos = avistamientos_cercanos_ubicacion(avistamientos, coordenadas, radio)
    if len(cercanos) > 0:
        '''aux = []
        for a in cercanos:
            aux.append((a.duracion, a.comentarios))
        return max(aux)
        '''
        return max((a.duracion, a.comentarios) for a in cercanos)
    else:
        return None




### 3.3 Avistamientos producidos entre dos fechas

def avistamientos_fechas(avistamientos: list[Avistamiento], fecha_inicial: date =None, fecha_final: date =None) -> list[Avistamiento]:
    '''
    Devuelve una lista con los avistamientos que han tenido lugar
    entre fecha_inicial y fecha_final (ambas inclusive). La lista devuelta
    estará ordenada de los avistamientos más recientes a los más antiguos.
    
    Si fecha_inicial es None se devolverán todos los avistamientos
    hasta fecha_final.
    Si fecha_final es None se devolverán todos los avistamientos desde
    fecha_inicial.
    Si ambas fechas son None se devolverá la lista de 
    avistamientos completa. 
    
    Usar el método date() para obtener la fecha de un objeto datetime.
    
    @param avistamientos: lista de tuplas con la información de los avistamientos 
    @type [Avistamiento(datetime, str, str, str, int, str, Coordenadas(float, float))]
    @param fecha_inicial: fecha a partir de la cual se devuelven los avistamientos
    @type fecha_inicial:datetime.date
    @param fecha_final: fecha hasta la cual se devuelven los avistamientos
    @type fecha_final: datetime.date
    @return: lista de tuplas con la información de los avistamientos en el rango de fechas
    @rtype: [Avistamiento(datetime, str, str, str, int, str, Coordenadas(float, float))]
    '''
    avistamientos_fechas = []
    for a in avistamientos:
        if (fecha_inicial==None or fecha_inicial<=a.fechahora.date()) and (fecha_final==None or fecha_final>=a.fechahora.date()):
            avistamientos_fechas.append(a)
    avistamientos_fechas.sort(key=lambda a:a.fechahora, reverse=True)
    return avistamientos_fechas

    
### 3.4 Avistamiento de un año con el comentario más largo
def comentario_mas_largo(avistamientos: list[Avistamiento], anyo: int, palabra: str) -> Avistamiento:
    ''' 
    Devuelve el avistamiento cuyo comentario es el más largo, de entre
    los avistamientos observados en el año dado por el parámetro "anyo"
    y cuyo comentario incluya la palabra recibida en el parámetro "palabra".
    
    @param avistamientos: lista de tuplas con la información de los avistamientos 
    @type [Avistamiento(datetime, str, str, str, int, str, Coordenadas(float, float))]
    @param anyo: año para el que se hará la búsqueda 
    @type anyo: int
    @param palabra: palabra que debe incluir el comentario del avistamiento buscado 
    @type palabra: str
    @return: avistamiento con el comentario más largo
    @rtype: Avistamiento(datetime, str, str, str, int, str, Coordenadas(float, float))
    '''    
    avistamientos_filtrado = []
    for a in avistamientos:
        if a.fechahora.year  == anyo and palabra.lower() in a.comentarios.lower():
            avistamientos_filtrado.append(a)
    return max(avistamientos_filtrado, key = lambda a:len(a.comentarios))



### 3.5 Media de días entre avistamientos consecutivos
def media_dias_entre_avistamientos(avistamientos: list[Avistamiento], anyo: int = None) -> float:
    ''' 
    Devuelve la media de días transcurridos entre dos avistamientos consecutivos.
    Si año es distinto de None, solo se contemplarán los avistamientos del año
    especificado para hacer el cálculo.
    
    @param avistamientos: lista de tuplas con la información de los avistamientos 
    @type [Avistamiento(datetime, str, str, str, int, str, Coordenadas(float, float))]
    @param anyo: año para el que se hará la búsqueda 
    @type anyo: int
    @return: media de días transcurridos entre avistamientos. Si no se puede realizar el
    cálculo, devuelve None 
    @rtype:-float
    '''    
    if anyo == None:
        avistamientos_anyo = avistamientos
    else:
        avistamientos_anyo = [a for a in avistamientos if a.fechahora.year == anyo]

    # avistamientos_anyo.sort()
    avistamientos_anyo = sorted(avistamientos_anyo) # Ordena por fecha, que es el primer campo
    
    dias = []
    # Recorre los avistamientos consecutivos de dos en dos
    for a1, a2 in zip(avistamientos_anyo, avistamientos_anyo[1:]):
        # Calcular los días entre dos date
        dias_entre_a1_a2 = (a2.fechahora.date()-a1.fechahora.date()).days
        dias.append(dias_entre_a1_a2)
    
    if len(dias) > 0:
        return sum(dias) / len(dias)
    else:
        return None



## 4 Operaciones con diccionarios

### 4.1 Avistamientos por fecha
def avistamientos_por_fecha(avistamientos: list[Avistamiento]) -> dict[datetime.date, set[Avistamiento]]:
    ''' 
    Devuelve un diccionario que indexa los avistamientos por fechas
    
    @param avistamientos: lista de tuplas con la información de los avistamientos 
    @type [Avistamiento(datetime, str, str, str, int, str, Coordenadas(float, float))]
    @return diccionario en el que las claves son las fechas de los avistamientos 
         y los valores son conjuntos con los avistamientos observados en esa fecha
    @rtype {datetime.date: {Avistamiento(datetime, str, str, str, int, str, Coordenadas(float, float))}}
    '''
    # Con dict
    res = {}
    for a in avistamientos:
        if a.fechahora.date() not in res:
            res[a.fechahora.date()] = set()
        res[a.fechahora.date()].add(a)
    return res


def avistamientos_por_fecha2(avistamientos: list[Avistamiento]) -> dict[datetime.date, set[Avistamiento]]:
    # Con defaultdict
    res = defaultdict(set)
    for a in avistamientos:
        # defaultdict se encarga de crear un set() y meterlo en el diccionario si la clave
        # no existe
        res[a.fechahora.date()].add(a)
    return res


### 4.2 Formas de avistamientos por mes
def formas_por_mes(avistamientos: list[Avistamiento]) -> dict[str, set[str]]:
    ''' 
    Devuelve un diccionario que indexa las distintas formas de avistamientos
    por los nombres de los meses en que se observan.
    Por ejemplo, para el mes "Enero" se asociará un conjunto con todas las
    formas distintas observadas en dicho mes.
    
    
    @param avistamientos: lista de tuplas con la información de los avistamientos 
    @type [Avistamiento(datetime, str, str, str, int, str, Coordenadas(float, float))]
    @return: diccionario en el que las claves son los nombres de los meses 
         y los valores son conjuntos con las formas observadas en cada mes
    @rtype {str: {str}}
    '''
    meses = ["Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio", "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"]
    res = defaultdict(set)
    for a in avistamientos:
        mes = meses[a.fechahora.month - 1]
        res[mes].add(a.forma)
    return res

def formas_por_mes2(avistamientos: list[Avistamiento]) -> dict[str, set[str]]:
    # Con defaultdict    
    # Establecemos la configuración local de la hora al formato
    # que esté definido en el ordenador del usuario
    locale.setlocale(locale.LC_TIME, '')

    pass

### 4.3 Número de avistamientos por año
def numero_avistamientos_por_año(avistamientos: list[Avistamiento]) -> dict[int, int]:
    '''
    Devuelve el número de avistamientos observados en cada año.
             
    @param avistamientos: lista de tuplas con la información de los avistamientos 
    @type [Avistamiento(datetime, str, str, str, int, str, Coordenadas(float, float))]
    @return: diccionario en el que las claves son los años
         y los valores son el número de avistamientos observados en ese año
    @rtype: {int: int}
    '''
    res = {}
    for a in avistamientos:
        if a.fechahora.year not in res:
            res[a.fechahora.year] = 0
        res[a.fechahora.year] += 1
    return res

def numero_avistamientos_por_año2(avistamientos: list[Avistamiento]) -> dict[int, int]:
    return Counter(a.fechahora.year for a in avistamientos)

def numero_avistamientos_por_año3(avistamientos: list[Avistamiento]) -> dict[int, int]:
    # Con defaultdict
    res = defaultdict(int)
    for a in avistamientos:
        res[a.fechahora.year] += 1
    return res

### 4.4 Número de avistamientos por mes del año
# PARA CASA
def num_avistamientos_por_mes(avistamientos: list[Avistamiento]) -> dict[str, int]:
    '''
    Devuelve el número de avistamientos observados en cada mes del año.
    
    Usar la expresión .date().month para obtener el número del mes de un objeto datetime.
    
    Usar como claves los nombres de los doce meses con la inicial en mayúsculas:

    @param avistamientos: lista de tuplas con la información de los avistamientos 
    @type [Avistamiento(datetime, str, str, str, int, str, Coordenadas(float, float))]
    @return:diccionario en el que las claves son los nombres de los meses y 
         los valores son el número de avistamientos observados en ese mes
    @rtype: {str: int}
    '''
    meses = ["Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio", "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"]
    res = defaultdict(int)
    for av in avistamientos:
        clave = meses[av.fechahora.month-1]
        res[clave] +=1
    return res       

    # con Counter
    # return Counter(meses[av.fechahora.month-1] for av in avistamientos) 

### 4.5 Estado con mayor número de avistamientos

def estado_mas_avistamientos(avistamientos: list[Avistamiento]) -> str: 
    '''
    Devuelve el estado donde más avistamientos se han observado.
    
    @param avistamientos: lista de tuplas con la información de los avistamientos 
    @type [Avistamiento(datetime, str, str, str, int, str, Coordenadas(float, float))]

    @return: estado con más avistamientos
    @rtype: str
    '''   
    # Primero, contamos avistamientos por estado
    # estados = []
    # for a in avistamientos:
    #     estados.append(a.estado)
    # conteo_por_estado = Counter(estados)

    # Otra forma:
    conteo_por_estado = Counter(a.estado for a in avistamientos)

    # # Otra forma:
    # conteo_por_estado = defaultdict(int)
    # for a in avistamientos:
    #     conteo_por_estado[a.estado] += 1
    
    #return max(conteo_por_estado.items(), key = lambda t:t[1])[0]
    estado, _ = max(conteo_por_estado.items(), key = lambda t:t[1])
    return estado

### 4.6 Hora del día con mayor número de avistamientos
### PARA CASA
def hora_mas_avistamientos(avistamientos: list[Avistamiento]) -> int:
    ''' 
    Devuelve la hora del día (de 0 a 23) con mayor número de avistamientos
    
    @param avistamientos: lista de tuplas con la información de los avistamientos 
    @type [Avistamiento(datetime, str, str, str, int, str, Coordenadas(float, float))]
    @return: hora del día en la que se producen más avistamientos
    @rtype: int
       
    En primer lugar construiremos un diccionario cuyas claves sean las horas del
    día en las que se han observado avistamientos, y cuyos valores sean el número
    de avistamientos observados en esa hora.
    Después obtendremos el máximo de los elementos del diccionario según el valor
    del elemento.
    '''
    c = Counter(a.fechahora.hour for a in avistamientos)
    return c.most_common(1)[0][0]

    # O usando max:
    # return max(c.items(), key = lambda t:t[1])[0]
    # return max(c, key = c.get)



### 4.7 Longitud media de los comentarios por estado

def longitud_media_comentarios_por_estado(avistamientos: list[Avistamiento]) -> dict[str, float]:
    '''
    
    Devuelve un diccionario en el que las claves son los estados donde se
    producen los avistamientos y los valores son la longitud media de los
    comentarios de los avistamientos en cada estado.
    
    @param avistamientos: lista de tuplas con la información de los avistamientos 
    @type [Avistamiento(datetime, str, str, str, int, str, Coordenadas(float, float))]
    @return: diccionario que almacena la longitud media de los comentarios (valores)
         por estado (claves)
    @rtype: {str: float}
            
    En primer lugar creamos un diccionario que agrupe los avistamientos por estado.
    Esto lo hacemos usando una función auxiliar.
    En segundo lugar, creamos un diccionario a partir del primero, en el que se
    calcule la media. Para definir este diccionario usamos una función
    auxiliar que calcule la media de una lista de Avistamientos
    '''
    # ¿Se puede hacer esto con DOS diccionarios de int?
    longitudes_comentarios_por_estado = defaultdict(list)
    for a in avistamientos:
        longitudes_comentarios_por_estado[a.estado].append(len(a.comentarios))
    
    res = {}
    for estado, longitudes in longitudes_comentarios_por_estado.items():
        res[estado] = sum(longitudes)/len(longitudes)
    return res

    #return {estado:sum(longitudes)/len(longitudes) 
    #       for estado, longitudes in longitudes_comentarios_por_estado.items()}


### 4.8 Porcentaje de avistamientos por forma
def porc_avistamientos_por_forma(avistamientos: list[Avistamiento]) -> dict[str, float]:
    '''
    Devuelve un diccionario en el que las claves son las formas de los
    avistamientos, y los valores los porcentajes de avistamientos con cada forma.
    
    @param avistamientos: lista de tuplas con la información de los avistamientos 
    @type [Avistamiento(datetime, str, str, str, int, str, Coordenadas(float, float))]
    @return:  diccionario que almacena los porcentajes de avistamientos (valores)
         por forma (claves)
    @rtype: {str: float}
            
    En primer lugar crearemos un diccionario cuyas claves sean las formas
    y cuyos valores sean el número de avistamientos de esa forma.
    Después crearemos un segundo diccionario con las mismas claves y cuyos valores
    resulten de dividir los valores del diccionario anterior por el número
    total de avistamientos, para obtener los porcentajes.
    '''  
    conteo_por_formas = Counter(a.forma for a in avistamientos)
    total_avistamientos = len(avistamientos)
    res = {}
    for forma, conteo in conteo_por_formas.items():
        res[forma] = 100 * conteo / total_avistamientos
    return res
    # OTRA FORMA:
    # return {forma:100*conteo/total_avistamientos 
    #            for forma, conteo in conteo_por_formas.items()}

### 4.8 BIS Porcentaje de avistamientos por forma en año
def porc_avistamientos_por_forma(avistamientos: list[Avistamiento], año: int) -> dict[str, float]:
    '''
    Igual que el anterior, pero sólo para los avistamientos del año indicado
    '''
    conteo_por_formas = Counter(a.forma 
                                    for a in avistamientos 
                                    if a.fechahora.year == año)
    total_avistamientos = sum(conteo_por_formas.values())
    res = {}
    for forma, conteo in conteo_por_formas.items():
        res[forma] = 100 * conteo / total_avistamientos
    return res

### 4.9 Avistamientos de mayor duración por estado
def avistamientos_mayor_duracion_por_estado(avistamientos: list[Avistamiento], n: int=3) -> dict[str, list[Avistamiento]]:
    '''
    Devuelve un diccionario que almacena los n avistamientos de mayor duración 
    en cada estado, ordenados de mayor a menor duración.
    
    @param avistamientos: lista de tuplas con la información de los avistamientos 
    @type avistamientos: [Avistamiento(datetime, str, str, str, int, str, Coordenadas(float, float))]
    @param n: número de avistamientos a almacenar por cada estado 
    @type n: int
    @return: diccionario en el que las claves son los estados y los valores son listas 
         con los "n" avistamientos de mayor duración de cada estado,
         ordenados de mayor a menor duración
            -> {str: [Avistamiento(datetime, str, str, str, int, str, Coordenadas(float, float))]}
            
    En primer lugar crearemos un diccionario de agrupación cuyas claves sean los estados
    y cuyos valores sean listas con los avistamientos observados en ese estado.
    Para ello usamos la función auxiliar que definimos en el apartado 4.7.
    Después crearemos un segundo diccionario cuyas claves sean los estados
    y cuyos valores sean las mismas listas, pero en orden de mayor a menor
    duración y recortadas a "limite" elementos.
    '''
    avistamientos_por_estados = defaultdict(list)
    for av in avistamientos:
        avistamientos_por_estados[av.estado].append(av)
    
    for estado, avistamientos_estado in avistamientos_por_estados.items():
        avistamientos_estado.sort(key = lambda a:a.duracion, reverse=True)
        avistamientos_por_estados[estado] = avistamientos_estado[:n]

    return avistamientos_por_estados


### 4.10 Año con más avistamientos de una forma
# PARA CASA
def año_mas_avistamientos_forma(avistamientos: list[Avistamiento], forma: str) -> int:
    '''
    Devuelve el año en el que se han observado más avistamientos
    de una forma dada.
    
    @param avistamientos: lista de tuplas con la información de los avistamientos 
    @type avistamientos: [Avistamiento(datetime, str, str, str, int, str, Coordenadas(float, float))]
    @param forma: forma del avistamiento 
    @type: str
    @return: año con mayor número de avistamientos de la forma dada
    @rtype: int
            
    
    En primer lugar se crea un diccionario con filtro cuyas claves sean los años
    y cuyos valores sean el número de avistamientos observados en ese año,
    utilizando la función ya definida numero_avistamientos_por_año.
    Luego, se calcula el máximo del diccionario según los valores.
    '''
    pass


### 4.11 Estados con mayor número de avistamientos
# PARA CASA
def estados_mas_avistamientos(avistamientos: list[Avistamiento], n: int=5) -> list[tuple[str, int]]:
    '''
    Devuelve una lista con los estados en los que se han observado
    más avistamientos, junto con el número de avistamientos,
    ordenados de mayor a menor número de avistamientos.
    
    @param avistamientos: lista de tuplas con la información de los avistamientos 
    @type avistamientos: [Avistamiento(datetime, str, str, str, int, str, Coordenadas(float, float))]
    @param n: número de estados a devolver 
    @type n: int  
    @return: lista con los estados donde se han observado más avistamientos,
         junto con el número de avistamientos, en orden decreciente
         del número de avistamientos y con un máximo de "limite" estados.
    @rtype: [(str, int)]
            
    En primer lugar crearemos un diccionario cuyas claves sean los estados
    y cuyos valores sean el número de avistamientos observados en ese estado.
    Después crearemos una lista con las claves del diccionario, ordenadas según
    sus respectivos valores en orden decreciente. Finalmente, recortaremos
    esta lista a "limite" elementos.
    '''
    pass

      
### 4.12 Duración total de los avistamientos de cada año en un estado dado
# PARA CASA
def duracion_total_avistamientos_año(avistamientos: list[Avistamiento], estado: str) -> dict[int, int]:
    '''
    Devuelve un diccionario que almacena la duración total de los avistamientos 
    en cada año, para un estado dado.
    
    @param avistamientos: lista de tuplas con la información de los avistamientos 
    @type avistamientos: [Avistamiento(datetime, str, str, str, int, str, Coordenadas(float, float))]
    @param estado: nombre del estado
    @type estado: str
    @return: diccionario en el que las claves son los años y los valores son números 
         con la suma de las duraciones de los avistamientos observados ese año
         en el estado dado
    @rtype: {int: int}

    Se crea un diccionario con filtro cuyas claves sean los años
    y cuyos valores sean la suma de las duraciones de todos los avistamientos
    observados en ese año.
    '''
    pass



### 4.13 Fecha del avistamiento más reciente de cada estado
def avistamiento_mas_reciente_por_estado(avistamientos: list[Avistamiento]) -> dict[str, datetime]:
    '''
    Devuelve un diccionario que almacena la fecha del último avistamiento
    observado en cada estado.
    
    @param avistamientos: lista de tuplas con la información de los avistamientos 
    @type avistamientos: [Avistamiento(datetime, str, str, str, int, str, Coordenadas(float, float))]
    @return:  diccionario en el que las claves son los estados y los valores son 
         las fechas del último avistamientos observado en ese estado.
    @rtype: {str: datetime.datetime}
            
    En primer lugar crearemos un diccionario cuyas claves sean los estados
    y cuyos valores sean listas con los avistamientos observados en ese estado.
    Para ello usamos la función auxiliar  definida en el apartado 4.7
    Después crearemos un segundo diccionario cuyas claves sean los estados y
    cuyos valores sean los valores máximos de las listas, según el campo fechahora.
    '''
    avistamientos_por_estados = defaultdict(list)
    for av in avistamientos:
        avistamientos_por_estados[av.estado].append(av)
    
    for estado, avistamientos_estado in avistamientos_por_estados.items():
        # Calcular la fecha del avistamiento más reciente
        avistamientos_por_estados[estado] = max(avistamientos_estado, key = lambda a:a.fechahora).fechahora

    return avistamientos_por_estados