#!/usr/bin/python3

import os
import sys

from grafo import Grafo
from biblioteca import (
    camino_mas,
    camino_escalas,
    centralidad,
    nueva_aerolinea,
    procesar_itinerario,
    exportar_kml
)


def cargar_aeropuertos(archivo):
    ciudad_aeropuertos = {}
    codigo_aeropuerto = {}

    with open(archivo, encoding="utf-8") as f:
        for linea in f:
            ciudad, codigo, lat, lon = linea.strip().split(",")

            datos = {
                "ciudad": ciudad,
                "codigo_aeropuerto": codigo,
                "latitud": lat,
                "longitud": lon
            }

            codigo_aeropuerto[codigo] = datos

            if ciudad not in ciudad_aeropuertos:
                ciudad_aeropuertos[ciudad] = []

            ciudad_aeropuertos[ciudad].append(codigo)

    return ciudad_aeropuertos, codigo_aeropuerto


def cargar_vuelos(archivo):
    vuelos = []

    with open(archivo, encoding="utf-8") as f:
        for linea in f:
            origen, destino, tiempo, precio, frecuencia = (
                linea.strip().split(",")
            )

            vuelos.append({
                "aeropuerto_i": origen,
                "aeropuerto_j": destino,
                "tiempo": int(tiempo),
                "costo": int(precio),
                "frecuencia": int(frecuencia)
            })

    return vuelos


def construir_grafo(vuelos):
    grafo = Grafo(dirigido=False)

    for vuelo in vuelos:

        origen = vuelo["aeropuerto_i"]
        destino = vuelo["aeropuerto_j"]

        datos_arista = {
            "tiempo": vuelo["tiempo"],
            "costo": vuelo["costo"],
            "frecuencia": vuelo["frecuencia"]
        }

        grafo.agregar_arista(
            origen,
            destino,
            datos_arista
        )

    return grafo


def main():

    if len(sys.argv) != 3:
        print("Uso: ./flycombi aeropuertos.csv vuelos.csv")
        sys.exit(1)

    archivo_aeropuertos = sys.argv[1]
    archivo_vuelos = sys.argv[2]

    ciudad_aeropuertos, codigo_aeropuerto = (
        cargar_aeropuertos(archivo_aeropuertos)
    )

    vuelos = cargar_vuelos(archivo_vuelos)

    grafo = construir_grafo(vuelos)

    ultima_ruta = []

    os.makedirs("output", exist_ok=True)

    while True:

        try:
            linea = input().strip()

        except EOFError:
            break

        if not linea:
            continue

        partes = linea.split()

        comando = partes[0]

        try:

            if comando == "camino_mas":

                resto = linea[len("camino_mas "):]

                tipo, ciudades = resto.split(",", 1)

                ciudad_origen, ciudad_destino = [
                    c.strip()
                    for c in ciudades.split(",")
                ]

                ruta, _ = camino_mas(
                    tipo.strip(),
                    ciudad_origen,
                    ciudad_destino,
                    grafo,
                    ciudad_aeropuertos
                )

                if ruta is None:
                    print("No se encontro recorrido")
                    continue

                print(" -> ".join(ruta))

                ultima_ruta = [ruta]

            elif comando == "camino_escalas":

                resto = linea[len("camino_escalas "):]

                ciudad_origen, ciudad_destino = [
                    c.strip()
                    for c in resto.split(",")
                ]

                ruta, _ = camino_escalas(
                    grafo,
                    ciudad_origen,
                    ciudad_destino,
                    ciudad_aeropuertos
                )

                if ruta is None:
                    print("No se encontro recorrido")
                    continue

                print(" -> ".join(ruta))

                ultima_ruta = [ruta]

            elif comando == "centralidad":

                n = int(partes[1])

                resultado = centralidad(grafo, n)

                print(", ".join(resultado))

            elif comando == "nueva_aerolinea":

                archivo_salida = (
                    f"output/{partes[1]}"
                )

                nueva_aerolinea(
                    grafo,
                    archivo_salida
                )

            elif comando == "itinerario":

                ruta_archivo = partes[1]

                ciudades, rutas = procesar_itinerario(
                    grafo,
                    ciudad_aeropuertos,
                    ruta_archivo
                )

                print(", ".join(ciudades))

                for ruta in rutas:
                    print(" -> ".join(ruta))

                ultima_ruta = rutas

            elif comando == "exportar_kml":

                archivo_kml = (
                    f"output/{partes[1]}"
                )

                if not ultima_ruta:
                    print("No hay ruta para exportar")
                    continue

                exportar_kml(
                    ultima_ruta,
                    codigo_aeropuerto,
                    archivo_kml
                )

            else:
                print("Comando desconocido")

        except Exception:
            print("Error en comando")


if __name__ == "__main__":
    main()