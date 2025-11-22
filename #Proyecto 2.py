# Proyecto 2 - Escapa del laberinto
#Autores:
#Efran Matarrita Sanabria 2025112541
#Gabriel Zuñiga Duran 2025099243

#---------------------------IMPORTS---------------------------
import tkinter as tk
import json
import os
import random

#---------------------------VARIABLES GLOBALES---------------------------
RUTA_PUNTAJES = "datos/puntajes.json"

#---------------------------FUNCIONES AUXILIARES---------------------------
def color_casilla(c):  #Son colores x mientras tanto, ya despues le buscamos algo nice :)
    if isinstance(c, Camino):
        return "#bfbfbf"   # gris
    if isinstance(c, Muro):
        return "#000000"   # negro
    if isinstance(c, Liana):
        return "#2ecc71"   # verde
    if isinstance(c, Tunel):
        return "#3498db"   # azul
    return "#ffffff"       # blanco por defeto

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
    def __init__ (self):   #Porbabilidad que tiene cada tipo de casilla
        self.prob_camino= 0.50
        self.prob_muro= 0.20
        self.prob_liana= 0.20
        self.prob_tunel= 0.10

    def generar(self):
        # Crear una matriz 10x10 con casillas aleatorias
        # ====== NO VALIDA QUE ESTE LA SALIDA SI O SI======
        matriz = []

        for f in range(10):
            fila = []
            for c in range(10):
                fila.append(self.elegir_casilla())
            matriz.append(fila)

        return matriz
    
    def elegir_casilla(self):
        x= random.random()  #es un numero random entre 0 y 1

        if x < self.prob_camino:
            return Camino()
        elif x < self.prob_camino + self.prob_muro:
            return Muro()
        elif x < self.prob_camino + self.prob_muro + self.prob_liana:
            return Liana()
        else:
            return Tunel()
        
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
        self.geometry("300x200")

        tk.Button(self, text="Registrar jugador",
                  command=self.abrir_registro).pack(pady=10)
        
        tk.Button(self, text="Iniciar juego",
                  command=self.abrir_juego).pack(pady=10)

    def abrir_registro(self):
        VentanaRegistro()

    def abrir_juego(self):
        VentanaJuego()

class VentanaJuego(tk.Toplevel):
    def __init__(self):
        super().__init__()
        self.title("Juego")

         # Crear canvas donde se dibuja el mapa
        self.canvas = tk.Canvas(self, width=400, height=400)
        self.canvas.pack()

        # Generar el mapa real
        generador = GeneradorMapa()
        self.mapa = generador.generar()

        # Dibujar el mapa
        self.dibujar_mapa()
    
    # Dibuja cada casilla para el mapa
    def dibujar_mapa(self):
        tam = 40  # tamaño de cada casilla (40x40 px)

        for f in range(10):
            for c in range(10):
                casilla = self.mapa[f][c]
                color = color_casilla(casilla)

                x1 = c * tam
                y1 = f * tam
                x2 = x1 + tam
                y2 = y1 + tam

                self.canvas.create_rectangle(x1, y1, x2, y2, fill=color, outline="gray")

#---------------------------PROGRAMA PRINCIPAL---------------------------
if __name__ == "__main__":
    app = VentanaMenu()
    app.mainloop()
