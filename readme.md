#  FlyCombi

Sistema basado en grafos para modelar rutas aéreas entre aeropuertos.

---

# Funcionalidades

- Caminos mínimos (tiempo o costo)
- Menor cantidad de escalas
- Centralidad de aeropuertos
- Árbol de expansión mínima (nueva aerolínea)
- Itinerarios con restricciones
- Exportación KML

---
---

# Complejidades
Todas usando la implementacion de grafo.py como diccionario de diccionarios:

| Funcionalidad | Algoritmo | Complejidad |
|---|---|---|
| camino_mas | Dijkstra | O(F log A) |
| camino_escalas | BFS | O(A + F) |
| centralidad | Brandes + Dijkstra | O(A × F log A) |
| nueva_aerolinea | Kruskal | O(F log A) |
| itinerario | Topológico + Dijkstra | O(I + R + I × F log A) |
| exportar_kml | Recorrido | O(A + F) |

---

# Comandos

## camino_mas

Busca el mejor camino entre dos ciudades según criterio.

- Puede ser **rapido (tiempo)** o **barato (costo)**
- Considera todos los aeropuertos de origen y destino

```text
camino_mas rapido,San Diego,New York
```

---

## camino_escalas

Encuentra el camino con menor cantidad de escalas entre dos ciudades.

```text
camino_escalas San Diego,New York
```

---

## centralidad

Devuelve los aeropuertos más importantes del sistema según centralidad de intermediación.

```text
centralidad 5
```

---

## nueva_aerolinea

Genera una red mínima de vuelos que conecta todos los aeropuertos con el menor costo total.

```text
nueva_aerolinea mst.csv
```

📁 Salida: `output/mst.csv`

---

## itinerario

Calcula un orden válido de ciudades respetando restricciones y luego rutas mínimas entre ellas.

```text
itinerario itinerario_ejemplo.csv
```

---

## exportar_kml

Exporta la última ruta calculada a formato KML para visualizar en Google Earth.

```text
exportar_kml mapa.kml
```

📁 Salida: `output/mapa.kml`

---

# Ejecución
Parado en la carpeta source del proyecto:

```bash
python3 src/flycombi.py data/aeropuertos.csv data/vuelos.csv < data/entrada.txt
```

---

# entrega.mk

```makefile
flycombi: flycombi.py
	cp flycombi.py flycombi
	chmod +x flycombi
```
