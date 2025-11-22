# Proyecto 2 - Escapa del laberinto
#Autores:
#Efran Matarrita Sanabria 2025112541
#Gabriel Zuñiga Duran 2025099243

#---------------------------IMPORTS---------------------------
import tkinter as tk
import json
import os

#---------------------------VARIABLES GLOBALES---------------------------
RUTA_PUNTAJES = "datos/puntajes.json"

#---------------------------CLASES DEL TERRENO---------------------------

class Casilla:
    def __init__(self):
        pass

    def permite_jugador(self):
        return False

    def permite_enemigo(self):
        return False

#---------------------------CLASES PARA LOS 4 TIPOS DE CASILLA---------------------------
class Camino(Casilla):
    def permite_jugador(self):
        return True

    def permite_enemigo(self):
        return True


class Muro(Casilla):
    def permite_jugador(self):
        return False

    def permite_enemigo(self):
        return False


class Tunel(Casilla):
    def permite_jugador(self):
        return True

    def permite_enemigo(self):
        return False


class Liana(Casilla):
    def permite_jugador(self):
        return False

    def permite_enemigo(self):
        return True


#---------------------------CLASES DEL MAPA Y ENTIDADES---------------------------

class Mapa:
    def __init__(self, matriz):
        self.matriz = matriz

    def obtener(self, f, c):
        return self.matriz[f][c]

    def dimensiones(self):
        return len(self.matriz), len(self.matriz[0])


class GeneradorMapa:
    def generar(self):
        # Mapa temporal 10x10 solo con caminos
        matriz = [[Camino() for _ in range(10)] for _ in range(10)]
        return matriz


class Jugador:
    def __init__(self, fila, col):
        self.fila = fila
        self.col = col
        self.energia = 100

    def mover(self, df, dc):
        self.fila += df
        self.col += dc


class Enemigo:
    def __init__(self, fila, col):
        self.fila = fila
        self.col = col

    def mover(self, df, dc):
        self.fila += df
        self.col += dc


class Trampas:
    def __init__(self):
        self.activas = []

#---------------------------CLASES DE PUNTAJES Y REGISTRO---------------------------

class Puntajes:
    def __init__(self):
        if not os.path.exists(RUTA_PUNTAJES):
            with open(RUTA_PUNTAJES, "w") as f:
                json.dump({"escapa": [], "cazador": []}, f)

    def agregar(self, nombre, puntaje, modo):
        pass 

    def top_5(self, modo):
        pass


class Registro:
    def validar(self, nombre):
        return len(nombre.strip()) > 0

#---------------------------INTERFAZ GRÁFICA---------------------------

class VentanaRegistro(tk.Toplevel):
    def __init__(self):
        super().__init__()
        self.title("Registro")

        tk.Label(self, text="Nombre del jugador:").pack()
        self.entry = tk.Entry(self)
        self.entry.pack()

class VentanaMenu(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Menú principal")

        tk.Button(self, text="Registrar jugador",
                  command=self.abrir_registro).pack()

    def abrir_registro(self):
        VentanaRegistro()

class VentanaJuego(tk.Toplevel):
    def __init__(self):
        super().__init__()
        self.title("Juego")

#---------------------------PROGRAMA PRINCIPAL---------------------------
if __name__ == "__main__":
    app = VentanaMenu()
    app.mainloop()
