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

        #Posicion inicial del jugador
        self.j_fila= 0
        self.j_col= 0

        self.tam= 40

        # Posición inicial del enemigo
        self.e_fila = 9
        self.e_col = 9

        # Dibujar el mapa
        self.dibujar_mapa()

        #Dibujar al jugador
        self.dibujar_jugador()

        # Dibujar enemigo
        self.dibujar_enemigo()

        #Teclas para moverse
        self.bind("<Up>", self.mover_arriba)
        self.bind("<Down>", self.mover_abajo)
        self.bind("<Left>", self.mover_izquierda)
        self.bind("<Right>", self.mover_derecha)
        # Para que la ventana detecte teclas
        self.focus_set()
        self.mover_enemigo()
    
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

    def dibujar_jugador(self):
        x1 = self.j_col * self.tam
        y1 = self.j_fila * self.tam
        x2 = x1 + self.tam
        y2 = y1 + self.tam

        # El jugador va a ser un cuadro rojo, igual por ahora :^
        self.jugador_grafico = self.canvas.create_rectangle(
            x1, y1, x2, y2, fill="red"
        )

    def dibujar_enemigo(self):
        x1 = self.e_col * self.tam
        y1 = self.e_fila * self.tam
        x2 = x1 + self.tam
        y2 = y1 + self.tam

        self.enemigo_grafico = self.canvas.create_rectangle(
            x1, y1, x2, y2, fill="purple"
        )

    #Para verificar de que si se pueda mover a lo que quiere moverse
    def puede_moverse_a (self,nf,nc):
        # Está fuera del mapp
        if nf < 0 or nf >= 10 or nc < 0 or nc >= 10:
            return False

        casilla = self.mapa[nf][nc]
        return casilla.permite_jugador()
    
    def enemigo_moverse_a (self,nf,nc):
        if nf < 0 or nf >= 10 or nc < 0 or nc >= 10:
            return False
        
        casilla= self.mapa[nf][nc]
        return casilla.permite_enemigo()
    

    #-------------- Moverse del jugador --------------
    def mover (self,df,dc):
        nf = self.j_fila + df
        nc = self.j_col + dc

        if self.puede_moverse_a(nf, nc):
            self.j_fila = nf
            self.j_col = nc
            self.canvas.move(self.jugador_grafico, dc * self.tam, df * self.tam)

    #Movimientos del jugador
    def mover_arriba(self, event):
        self.mover(-1, 0)

    def mover_abajo(self, event):
        self.mover(1, 0)

    def mover_izquierda(self, event):
        self.mover(0, -1)

    def mover_derecha(self, event):
        self.mover(0, 1)

    #-------------- Moverse del enemigo --------------
    def mover_enemigo(self):
        df = 0
        dc = 0

        # Movimiento vertical hacia el jugador
        if self.e_fila < self.j_fila:
            df = 1
        elif self.e_fila > self.j_fila:
            df = -1

        # Movimiento horizontal hacia el jugador
        if self.e_col < self.j_col:
            dc = 1
        elif self.e_col > self.j_col:
            dc = -1

        # Intentar movimiento vertical primero
        if df != 0 and self.enemigo_moverse_a(self.e_fila + df, self.e_col):
            self.e_fila += df
            self.canvas.move(self.enemigo_grafico, 0, df * self.tam)

        # Si no pudo, intentar horizontal
        elif dc != 0 and self.enemigo_moverse_a(self.e_fila, self.e_col + dc):
            self.e_col += dc
            self.canvas.move(self.enemigo_grafico, dc * self.tam, 0)

        # Para saber si me atrapo (por ahora :p)
        if self.e_fila == self.j_fila and self.e_col == self.j_col:
            print("¡Te atraparon!")
            return

        #Aqui se cambia la velocidad a la que se mueve el enemigo
        self.after(400, self.mover_enemigo)

#---------------------------PROGRAMA PRINCIPAL---------------------------
if __name__ == "__main__":
    app = VentanaMenu()
    app.mainloop()
