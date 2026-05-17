import random

class Grafo:
    def __init__(self, dirigido=True):
        self.dirigido = dirigido
        self.vertices = set()
        self.adyacentes = {}  # dict: vertice -> dict vecino -> peso

    def agregar_vertice(self, vertice):
        """Agrega un vértice al grafo si no existe."""
        if vertice not in self.vertices:
            self.vertices.add(vertice)
            self.adyacentes[vertice] = {}

    def obtener_vertices(self):
        """Devuelve la lista de vértices."""
        return list(self.vertices)

    def obtener_adyacentes(self, v):
        """Devuelve lista de vecinos de v."""
        return list(self.adyacentes.get(v, {}).keys())

    def vertice_aleatorio(self):
        """Devuelve un vértice aleatorio o None si no hay."""
        if not self.vertices:
            return None
        return random.choice(list(self.vertices))

    def estan_unidos(self, v, w):
        """Indica si hay arista de v a w."""
        return w in self.adyacentes.get(v, {})

    def peso_arista(self, v, w):
        """Devuelve el peso de la arista (v, w) o None si no existe."""
        return self.adyacentes.get(v, {}).get(w)

    def agregar_arista(self, v, w, peso=1):
        """Agrega la arista (v, w) con peso, crea vértices si no existen."""
        self.agregar_vertice(v)
        self.agregar_vertice(w)
        self.adyacentes[v][w] = peso
        if not self.dirigido:
            self.adyacentes[w][v] = peso

    def borrar_vertice(self, v):
        """Elimina el vértice v y todas sus aristas."""
        if v in self.vertices:
            self.vertices.remove(v)
            self.adyacentes.pop(v, None)
            for u in self.adyacentes:
                self.adyacentes[u].pop(v, None)

    def borrar_arista(self, v, w):
        """Elimina la arista (v, w) y (w, v) si no es dirigido."""
        if w in self.adyacentes.get(v, {}):
            del self.adyacentes[v][w]
        if not self.dirigido and v in self.adyacentes.get(w, {}):
            del self.adyacentes[w][v]
