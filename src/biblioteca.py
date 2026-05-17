import csv
import heapq
from collections import defaultdict, deque
from grafo import Grafo
from UnionFind import UnionFind

# =============================== #
#        FUNCIONES PRINCIPALES    #
# =============================== #

def camino_mas(opcion, origen, destino, grafo, ciudades):
    origen = _clave_ciudad(ciudades, origen)
    destino = _clave_ciudad(ciudades, destino)

    if origen is None or destino is None:
        return None, 0

    obtener_peso = (
        lambda info: info["costo"]
        if opcion == "barato"
        else info["tiempo"]
    )

    origenes = ciudades[origen]
    destinos = set(ciudades[destino])

    mejor_camino = None
    mejor_costo = float("inf")

    for aeropuerto_origen in origenes:
        distancias, padres = _dijkstra(
            grafo,
            aeropuerto_origen,
            obtener_peso
        )

        for aeropuerto_destino in destinos:
            if (
                aeropuerto_destino in distancias and
                distancias[aeropuerto_destino] < mejor_costo
            ):
                mejor_costo = distancias[aeropuerto_destino]
                mejor_camino = _reconstruir_camino(
                    padres,
                    aeropuerto_destino
                )

    if mejor_camino is None:
        return None, 0

    return mejor_camino, mejor_costo


def camino_escalas(grafo, origen, destino, ciudades):
    origen = _clave_ciudad(ciudades, origen)
    destino = _clave_ciudad(ciudades, destino)

    if origen is None or destino is None:
        return None, 0

    origenes = ciudades[origen]
    destinos = set(ciudades[destino])

    mejor_camino = None

    for aeropuerto_origen in origenes:
        camino = _bfs(grafo, aeropuerto_origen, destinos)

        if (
            camino and
            (
                mejor_camino is None or
                len(camino) < len(mejor_camino)
            )
        ):
            mejor_camino = camino

    if mejor_camino is None:
        return None, 0

    escalas = max(len(mejor_camino) - 2, 0)

    return mejor_camino, escalas


def centralidad(grafo, n):
    centralidades = defaultdict(float)

    for origen in grafo.obtener_vertices():

        stack = []
        padres = defaultdict(list)

        cantidad_caminos = defaultdict(int)
        cantidad_caminos[origen] = 1

        distancias = {origen: 0}

        heap = [(0, origen)]

        while heap:
            distancia_actual, vertice = heapq.heappop(heap)

            if distancia_actual > distancias[vertice]:
                continue

            stack.append(vertice)

            for vecino in grafo.obtener_adyacentes(vertice):

                info_arista = grafo.peso_arista(vertice, vecino)

                peso = 1 / max(info_arista["frecuencia"], 1)

                nueva_distancia = distancia_actual + peso

                if (
                    vecino not in distancias or
                    nueva_distancia < distancias[vecino]
                ):

                    distancias[vecino] = nueva_distancia

                    heapq.heappush(
                        heap,
                        (nueva_distancia, vecino)
                    )

                    cantidad_caminos[vecino] = (
                        cantidad_caminos[vertice]
                    )

                    padres[vecino] = [vertice]

                elif abs(
                    nueva_distancia - distancias[vecino]
                ) < 1e-9:

                    cantidad_caminos[vecino] += (
                        cantidad_caminos[vertice]
                    )

                    padres[vecino].append(vertice)

        dependencias = defaultdict(float)

        while stack:

            vertice = stack.pop()

            for predecesor in padres[vertice]:

                proporcion = (
                    cantidad_caminos[predecesor] /
                    cantidad_caminos[vertice]
                )

                dependencias[predecesor] += (
                    proporcion *
                    (1 + dependencias[vertice])
                )

            if vertice != origen:
                centralidades[vertice] += dependencias[vertice]

    resultado = sorted(
        centralidades.items(),
        key=lambda x: (-x[1], x[0])
    )

    return [vertice for vertice, _ in resultado[:n]]


def nueva_aerolinea(grafo, archivo_salida):
    mst, _ = _mst_kruskal(grafo)

    _escribir_mst(mst, archivo_salida)

    print("OK")


def procesar_itinerario(
    grafo_vuelos,
    ciudad_aeropuertos,
    ruta_archivo
):

    ciudades_a_visitar, restricciones = leer_archivo(
        ruta_archivo
    )

    grafo_restricciones = construir_grafo_restricciones(
        ruta_archivo
    )

    if len(restricciones) == 0:

        orden_ciudades = ciudades_a_visitar

    else:

        orden_total = orden_topologico(
            grafo_restricciones
        )

        orden_ciudades = [
            ciudad
            for ciudad in orden_total
            if ciudad in ciudades_a_visitar
        ]

        sin_restricciones = [
            ciudad
            for ciudad in ciudades_a_visitar
            if ciudad not in orden_ciudades
        ]

        orden_ciudades.extend(sin_restricciones)

    caminos = []

    aeropuerto_anterior = None

    for i in range(len(orden_ciudades) - 1):

        ciudad_origen = orden_ciudades[i]
        ciudad_destino = orden_ciudades[i + 1]

        if i == 0:
            aeropuertos_origen = (
                ciudad_aeropuertos[ciudad_origen]
            )
        else:
            aeropuertos_origen = [aeropuerto_anterior]

        aeropuertos_destino = (
            ciudad_aeropuertos[ciudad_destino]
        )

        mejor_camino = None
        mejor_costo = float("inf")

        for aeropuerto_origen in aeropuertos_origen:

            distancias, padres = _dijkstra(
                grafo_vuelos,
                aeropuerto_origen,
                lambda vuelo: vuelo["tiempo"]
            )

            for aeropuerto_destino in aeropuertos_destino:

                if (
                    aeropuerto_destino in distancias and
                    distancias[aeropuerto_destino] < mejor_costo
                ):

                    mejor_costo = (
                        distancias[aeropuerto_destino]
                    )

                    mejor_camino = _reconstruir_camino(
                        padres,
                        aeropuerto_destino
                    )

        if mejor_camino is None:
            raise ValueError(
                f"No se encontró camino entre "
                f"{ciudad_origen} y {ciudad_destino}"
            )

        caminos.append(mejor_camino)

        aeropuerto_anterior = mejor_camino[-1]

    return orden_ciudades, caminos


def exportar_kml(
    ultima_salida,
    aeropuertos,
    ruta_archivo
):

    if not ultima_salida:
        print("No hay ruta para exportar")
        return

    
    if isinstance(ultima_salida[0], list):
        ruta_total = []
        for subruta in ultima_salida:
            if ruta_total and ruta_total[-1] == subruta[0]:
                ruta_total.extend(subruta[1:])
            else:
                ruta_total.extend(subruta)
    else:
        ruta_total = ultima_salida

    if len(ruta_total) < 2:
        print("No hay ruta para exportar")
        return

    with open(ruta_archivo, "w", encoding="utf-8") as archivo:

        archivo.write('<?xml version="1.0" encoding="UTF-8"?>\n')
        archivo.write('<kml xmlns="http://earth.google.com/kml/2.1">\n')
        archivo.write('  <Document>\n')
        archivo.write('    <name>KML caminos minimos</name>\n')
        archivo.write('    <description>KML caminos minimos</description>\n\n')

      
        for codigo in ruta_total:
            aeropuerto = aeropuertos[codigo]

            lon = aeropuerto["longitud"]
            lat = aeropuerto["latitud"]

            archivo.write('    <Placemark>\n')
            archivo.write(f'      <name>{aeropuerto["codigo_aeropuerto"]}</name>\n')
            archivo.write('      <Point>\n')
            archivo.write(f'        <coordinates>{lon},{lat}</coordinates>\n')
            archivo.write('      </Point>\n')
            archivo.write('    </Placemark>\n\n')

       
        for i in range(len(ruta_total) - 1):

            origen = aeropuertos[ruta_total[i]]
            destino = aeropuertos[ruta_total[i + 1]]

            lon1, lat1 = origen["longitud"], origen["latitud"]
            lon2, lat2 = destino["longitud"], destino["latitud"]

            archivo.write('    <Placemark>\n')
            archivo.write('      <LineString>\n')
            archivo.write('        <coordinates>\n')
            archivo.write(f'          {lon1},{lat1} {lon2},{lat2}\n')
            archivo.write('        </coordinates>\n')
            archivo.write('      </LineString>\n')
            archivo.write('    </Placemark>\n\n')

        archivo.write('  </Document>\n')
        archivo.write('</kml>\n')

    print("OK")

# =============================== #
#         FUNCIONES AUXILIARES    #
# =============================== #

def _clave_ciudad(ciudades, nombre):

    nombre = nombre.strip().lower()

    for ciudad in ciudades:

        if ciudad.strip().lower() == nombre:
            return ciudad

    return None


def _dijkstra(grafo, inicio, obtener_peso):

    distancias = {inicio: 0}

    padres = {}

    heap = [(0, inicio)]

    while heap:

        distancia_actual, vertice = heapq.heappop(heap)

        if distancia_actual > distancias[vertice]:
            continue

        for vecino in grafo.obtener_adyacentes(vertice):

            info = grafo.peso_arista(vertice, vecino)

            nueva_distancia = (
                distancia_actual +
                obtener_peso(info)
            )

            if (
                vecino not in distancias or
                nueva_distancia < distancias[vecino]
            ):

                distancias[vecino] = nueva_distancia

                padres[vecino] = vertice

                heapq.heappush(
                    heap,
                    (nueva_distancia, vecino)
                )

    return distancias, padres


def _bfs(grafo, inicio, objetivos):

    visitados = {inicio}

    padres = {}

    cola = deque([inicio])

    while cola:

        vertice = cola.popleft()

        if vertice in objetivos:
            return _reconstruir_camino(
                padres,
                vertice
            )

        for vecino in grafo.obtener_adyacentes(vertice):

            if vecino not in visitados:

                visitados.add(vecino)

                padres[vecino] = vertice

                cola.append(vecino)

    return None


def _reconstruir_camino(padres, destino):

    camino = [destino]

    while destino in padres:

        destino = padres[destino]

        camino.append(destino)

    camino.reverse()

    return camino


def _mst_kruskal(grafo):

    union_find = UnionFind(
        grafo.obtener_vertices()
    )

    aristas = sorted(
        _obtener_aristas(grafo),
        key=lambda x: x[2]["costo"]
    )

    mst = Grafo(dirigido=False)

    costo_total = 0

    for origen, destino, info in aristas:

        if (
            union_find.find(origen) !=
            union_find.find(destino)
        ):

            mst.agregar_arista(
                origen,
                destino,
                info
            )

            union_find.union(origen, destino)

            costo_total += info["costo"]

    return mst, int(costo_total)


def _obtener_aristas(grafo):

    aristas = []

    vistos = set()

    for origen in grafo.obtener_vertices():

        for destino in grafo.obtener_adyacentes(origen):

            if (destino, origen) not in vistos:

                aristas.append(
                    (
                        origen,
                        destino,
                        grafo.peso_arista(
                            origen,
                            destino
                        )
                    )
                )

                vistos.add((origen, destino))

    return aristas


def _escribir_mst(grafo_mst, archivo_salida):

    with open(
        archivo_salida,
        "w",
        newline="",
        encoding="utf-8"
    ) as archivo:

        writer = csv.writer(archivo)

        for origen, destino, info in _obtener_aristas(
            grafo_mst
        ):

            writer.writerow([
                origen,
                destino,
                int(info["tiempo"]),
                int(info["costo"]),
                int(info["frecuencia"])
            ])


def leer_archivo(ruta):

    with open(ruta, encoding="utf-8") as archivo:

        lineas = [
            linea.strip()
            for linea in archivo
            if linea.strip()
        ]

    ciudades = [
        ciudad.strip()
        for ciudad in lineas[0].split(",")
    ]

    restricciones = []

    for linea in lineas[1:]:

        origen, destino = (
            parte.strip()
            for parte in linea.split(",")
        )

        restricciones.append((origen, destino))

    return ciudades, restricciones


def construir_grafo_restricciones(ruta_archivo):

    ciudades, restricciones = leer_archivo(
        ruta_archivo
    )

    grafo = Grafo(dirigido=True)

    for ciudad in ciudades:
        grafo.agregar_vertice(ciudad)

    for origen, destino in restricciones:
        grafo.agregar_arista(origen, destino)

    return grafo


def grados_entrada(grafo):

    grados = {
        vertice: 0
        for vertice in grafo.obtener_vertices()
    }

    for vertice in grafo.obtener_vertices():

        for vecino in grafo.obtener_adyacentes(vertice):

            grados[vecino] += 1

    return grados


def orden_topologico(grafo):

    grados = grados_entrada(grafo)

    cola = deque()

    resultado = []

    for vertice in grafo.obtener_vertices():

        if grados[vertice] == 0:
            cola.append(vertice)

    while cola:

        vertice = cola.popleft()

        resultado.append(vertice)

        for vecino in grafo.obtener_adyacentes(vertice):

            grados[vecino] -= 1

            if grados[vecino] == 0:
                cola.append(vecino)

    if len(resultado) != len(grafo.obtener_vertices()):

        raise ValueError(
            "Hay un ciclo en las restricciones"
        )

    return resultado