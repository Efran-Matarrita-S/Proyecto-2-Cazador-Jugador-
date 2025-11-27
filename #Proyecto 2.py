# Proyecto 2 - Escapa del laberinto
#Autores:
#Efran Matarrita Sanabria 2025112541
#Gabriel Zuñiga Duran 2025099243

#---------------------------IMPORTS---------------------------
import tkinter as tk
from tkinter import messagebox
import json
import os
import time
import random

#---------------------------VARIABLES GLOBALES---------------------------
RUTA_PUNTAJES = "datos/puntajes.json"
#nombre_jugador = None
#contador_trampa = 0

DIFICULTADES = {
    "facil": {
        "vel_enemigo": 400,
        "regen_energia": 300,
        "costo_correr": 10,
        "max_trampas": 4,
        "penalizacion": 50,
        "cantidad_enemigos": 1
    },
    "medio": {
        "vel_enemigo": 250,
        "regen_energia": 500,
        "costo_correr": 20,
        "max_trampas": 3,
        "penalizacion": 100,
        "cantidad_enemigos": 2
    },
    "dificil": {
        "vel_enemigo": 130,
        "regen_energia": 700,
        "costo_correr": 30,
        "max_trampas": 2,
        "penalizacion": 180,
        "cantidad_enemigos": 3
    }
}

#---------------------------FUNCIONES AUXILIARES---------------------------
def cargar_casilla(c): 
    if isinstance(c, Camino):
        return "c"            
    if isinstance(c, Muro):
        return "m"            
    if isinstance(c, Liana):
        return "l"            
    if isinstance(c, Tunel):
        return                
    return "t"                

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
    def __init__ (self):   # Probabilidad que tiene cada tipo de casilla
        self.prob_camino = 0.60
        self.prob_muro   = 0.20
        self.prob_liana  = 0.10
        self.prob_tunel  = 0.10

        # Coordenadas de la salida (se llenan al generar el mapa)
        self.salida_fila = None
        self.salida_col = None

    def generar(self):
        # Genera mapas hasta que encuentre uno con camino válido
        while True:
            matriz = self._generar_matriz_basica()

            # Forzamos inicio y cazador a ser camino
            matriz[0][0] = Camino()     # jugador
            matriz[9][9] = Camino()     # enemigo

            # Elegir salida en el borde (no (0,0) ni (9,9))
            sf, sc = self._elegir_salida_borde()
            matriz[sf][sc] = Camino()   # aseguramos que la salida sea transitable

            # Verificar si hay camino desde (0,0) hasta (sf, sc)
            if self._hay_camino(matriz, 0, 0, sf, sc):
                self.salida_fila = sf
                self.salida_col = sc
                return matriz
            # Si no hay camino, vuelve a generar otra matriz

    def _generar_matriz_basica(self):
        matriz = []
        casillas_dejar_libre = [(0,0),(0,1),(1,0),
                                (9,9),(9,8),(9,7),
                                (8,9),(8,8),(8,7)
            ]
        for f in range(10):
            fila = []
            for c in range(10):
                casilla_actual = (f,c)
                if casilla_actual not in casillas_dejar_libre:
                    fila.append(self.elegir_casilla())
                else:
                    fila.append(Camino())
            matriz.append(fila)
        return matriz

    def _elegir_salida_borde(self):
        posiciones = []
        n = 10

        # Borde superior e inferior
        for c in range(n):
            posiciones.append((0, c))
            posiciones.append((n - 1, c))

        # Borde izquierdo y derecho (sin repetir esquinas)
        for f in range(1, n - 1):
            posiciones.append((f, 0))
            posiciones.append((f, n - 1))

        # Excluir inicio (0,0) y posición del cazador (9,9)
        posiciones = [p for p in posiciones if p not in [(0, 0), (9, 9)]]

        return random.choice(posiciones)

    def _hay_camino(self, matriz, fi, ci, ff, cf):
        from collections import deque

        n = len(matriz)
        visitado = [[False] * n for _ in range(n)]
        q = deque()

        if not matriz[fi][ci].permite_jugador():
            return False

        q.append((fi, ci))
        visitado[fi][ci] = True

        while q:
            f, c = q.popleft()
            if f == ff and c == cf:
                return True

            for df, dc in [(1,0), (-1,0), (0,1), (0,-1)]:
                nf = f + df
                nc = c + dc

                if 0 <= nf < n and 0 <= nc < n and not visitado[nf][nc]:
                    if matriz[nf][nc].permite_jugador():
                        visitado[nf][nc] = True
                        q.append((nf, nc))

        return False

    def elegir_casilla(self):
        x = random.random()  # es un numero random entre 0 y 1

        if x < self.prob_camino:
            return Camino()
        elif x < self.prob_camino + self.prob_muro:
            return Muro()
        elif x < self.prob_camino + self.prob_muro + self.prob_liana:
            return Liana()
        else:
            return Tunel()
        
class Jugador:
    def __init__(self, fila, col,nombre,modo_de_juego):
        self.fila = fila
        self.col = col
        self.nombre = nombre
        self.modo_de_juego = modo_de_juego
        self.energia = 100

    def mover(self, df, dc):
        self.fila += df
        self.col += dc

    def correr(self):
        pass

    def gastar_energia(self, cantidad):
        if self.energia >= cantidad:
            self.energia -= cantidad
            return True
        return False


class Enemigo:
    def __init__(self, fila, col):
        self.fila = fila
        self.col = col
        self.estado = "activo"  # Puede tener 3 estados "activo", "muerto", "reapareciendo"
        self.tiempo_reaparicion = 0

    def mover(self, df, dc):
        self.fila += df
        self.col += dc



class Trampa:
    def __init__(self):
        self.activas = []

    def permite_jugador(self):
        return True

    def permite_enemigo(self):
        return True   
        


#---------------------------CLASES DE PUNTAJES Y REGISTRO---------------------------

class Puntajes:
    def __init__(self):
        if not os.path.exists(RUTA_PUNTAJES):
            os.makedirs("datos")
        if not os.path.exists(RUTA_PUNTAJES):
            with open(RUTA_PUNTAJES, "w") as f:
                json.dump({"escapa": [], "cazador": []}, f)

    def agregar(self, nombre, puntaje, modo):
        with open(RUTA_PUNTAJES, "r") as f:
            datos = json.load(f)
        
        datos[modo].append({"nombre": nombre, "puntaje": puntaje})
        
        # Ordenar de MENOR a mayor (menos tiempo = mejor)
        datos[modo].sort(key=lambda x: x["puntaje"])  #TODO: Revisar como sirve esto lo hizo Claude pero para implementarlo nosotros o dejarlo

        
        with open(RUTA_PUNTAJES, "w") as f:
            json.dump(datos, f, indent=4)

    def extraer_top_5(self, modo):
        with open(RUTA_PUNTAJES, "r") as f:
            datos = json.load(f)
        return datos[modo][:5]


class Registro:
    def validar_registrar(self, nombre, label_error):
        if len(nombre.strip()) > 0:
            label_error.config(text="")
            
            return True
        else:
            label_error.config(text="El nombre no puede estar vacío")
            return False   

#---------------------------INTERFAZ GRÁFICA---------------------------

class VentanaRegistro(tk.Toplevel):
    def __init__(self,parent):
        super().__init__(parent)
        self.title("Registro")
        self.geometry("200x200")
        self.nombre_jugador = None

        tk.Label(self, text="Nombre del jugador:").pack()
        self.entry = tk.Entry(self)
        self.entry.pack()

        tk.Button(self, text="Registrar", command=self.registrar).pack(pady=10)
        
        self.label_error = tk.Label(self, text="", fg="red")
        self.label_error.pack()

    def registrar(self):
        nombre = self.entry.get()
        registro = Registro()
        if registro.validar_registrar(nombre, self.label_error):
            self.nombre_jugador = nombre
            self.destroy()

class VentanaElegirTop(tk.Toplevel):
    def __init__(self,parent):
        super().__init__(parent)
        self.title("Top Globales")
        self.geometry("200x200")

        tk.Label(self, text="Elige el top que quieres abrir:").pack()

        tk.Button(self, text="Top de Escapadores", command=self.abrir_top_escapadores).pack(pady=10)

        tk.Button(self, text="Top de Cazadores", command=self.abrir_top_cazadores).pack(pady=10) #TODO: Validacion para no agregar el mismo username al top multiples veces (este esta opcional en realidad creo q se puede dejar como esta)

    def abrir_top_escapadores(self):
        puntajes = Puntajes()
        top_5 = puntajes.extraer_top_5("escapa")
        self.mostrar_top(top_5, "Escapadores")

    def abrir_top_cazadores(self):
        puntajes = Puntajes()
        top_5 = puntajes.extraer_top_5("cazador")
        self.mostrar_top(top_5, "Cazadores")

    def mostrar_top(self, datos, titulo):   
            # Crear nueva ventana para mostrar el top
            ventana_top = tk.Toplevel(self)
            ventana_top.title(f"Top 5 - {titulo}")
            ventana_top.geometry("500x400")

            tk.Label(ventana_top, text=f"Top 5 {titulo}", font=("Arial", 10, "bold")).pack(pady=10)

            frame_top = tk.Frame(ventana_top)
            frame_top.pack(pady=10, padx=10, fill="both", expand=True)

            tk.Label(frame_top, text="Posición", font=("Arial", 10, "bold"), width=12).pack(anchor="w")
            tk.Label(frame_top, text="Nombre", font=("Arial", 10, "bold"), width=20).pack(anchor="w")
            tk.Label(frame_top, text="Puntaje", font=("Arial", 10, "bold"), width=12).pack(anchor="w")     

            for i, jugador in enumerate(datos, 1):
                nombre = jugador["nombre"]
                puntaje = jugador["puntaje"]
                
                # Crear label con la información formateada
                label_fila = tk.Label(
                    frame_top,
                    text=f"{i}. {nombre:<20} {puntaje}",
                    font=("Arial", 10),
                )
                label_fila.pack(anchor="w", pady=5)

class VentanaMenu(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Menú principal")
        self.geometry("400x300")
        self.nombre_guardado = None

        tk.Button(self, text="Registrar jugador",
                  command=self.abrir_registro).pack(pady=10)
        
        tk.Button(self, text="Top Globales",
                  command=self.abrir_top).pack(pady=10)
        
        tk.Button(self, text="Iniciar juego",
                  command=self.abrir_juego).pack(pady=10)


    def abrir_registro(self):
        ventana_registro = VentanaRegistro(self)
        self.wait_window(ventana_registro)
        self.nombre_guardado = ventana_registro.nombre_jugador

    def abrir_top(self):
        ventana_top = VentanaElegirTop(self)
        self.wait_window(ventana_top)

    def abrir_juego(self):
        if self.nombre_guardado:
            # 1. Seleccionar dificultad
            ventana_diff = VentanaDificultad(self)
            self.wait_window(ventana_diff)

            if ventana_diff.dificultad is None:
                return  # usuario cerró la ventana

            dificultad_elegida = ventana_diff.dificultad

            # 2. Seleccionar modo
            ventana_modo = Ventana_modo_de_juego(self, self.nombre_guardado)
            self.wait_window(ventana_modo)

            if ventana_modo.modo_elegido:
                VentanaJuego(
                    self.nombre_guardado,
                    ventana_modo.modo_elegido,
                    dificultad_elegida   
                )
        else:
            messagebox.showwarning("Error:", "Debes registrar un nombre primero")


class VentanaJuego(tk.Toplevel):
    def __init__(self,nombre_jugador,modo_de_juego,dificultad):
        super().__init__()
        self.title("Juego")
        self.juego_terminado = False


        # Crear el jugador
        self.jugador = Jugador(0, 0, nombre_jugador, modo_de_juego)
        self.modo = modo_de_juego

        #Dificultad
        self.dificultad= dificultad

        params = DIFICULTADES[self.dificultad]

        self.vel_enemigo = params["vel_enemigo"]
        self.regen_rate = params["regen_energia"]
        self.costo_correr = params["costo_correr"]
        self.max_trampas = params["max_trampas"]
        self.penalizacion = params["penalizacion"]
        self.cantidad_enemigos = params["cantidad_enemigos"]

        # Generar el mapa antes de usar salida
        generador = GeneradorMapa()
        self.mapa = generador.generar()

        self.s_fila = generador.salida_fila
        self.s_col = generador.salida_col

        # Posiciones iniciales según modo
        if self.modo == "escapa":
            # Jugador abajo izquierda entonces escapar
            self.j_fila = 0
            self.j_col = 0

            # Enemigo arriba derecha entonces perseguir
            self.e_fila = 9
            self.e_col = 9

            # En este modo, el enemigo sigue al jugador
            self.objetivo_fila = self.j_fila
            self.objetivo_col = self.j_col

        else:  # modo cazador
            # Cazador empieza arriba derecha
            self.j_fila = 9
            self.j_col = 9

            # Escapador empieza abajo izquierda
            self.e_fila = 0
            self.e_col = 0

            # En este modo, el enemigo huye hacia la salida
            self.objetivo_fila = self.s_fila
            self.objetivo_col = self.s_col

        # Tamaño
        self.tam = 40

        # Timer del puntaje
        self.tiempo_inicio = time.time()

        # Canvas
        self.canvas = tk.Canvas(self, width=400, height=450)
        self.canvas.pack()

        # Barra de energía solo si eres escapador
        self.barra_energia = tk.Canvas(self, width=400, height=20, bg="white")
        if self.modo == "escapa":
            self.barra_energia.pack()

        self.actualizar_barra_energia()
        self.after(300, self.regenerar_energia)

        # Inicializar el contador de trampa
        self.contador_trampa = 0
        self.trampas_activas = []
        self.contador_activo = False

        # Dibujar el mapa
        self.dibujar_mapa()

        #Dibujar al jugador
        self.dibujar_jugador()

        #Teclas para moverse
        self.bind("<Up>", self.mover_arriba)  
        self.bind("<Down>", self.mover_abajo)
        self.bind("<Left>", self.mover_izquierda)
        self.bind("<Right>", self.mover_derecha)
        self.bind("<space>", self.poner_trampa)

        # Tecla para correr (Shift izquierdo)
        self.bind("<KeyPress-x>", self.correr)
        self.bind("<<KeyPress-x>>", self.soltar_correr)

        # Variable para saber si está corriendo
        self.corriendo = False

        #Ahora hacemos el enemigo
        # Lista de enemigos por si hay varios
        self.enemigos = []

        # Posiciones iniciales para spawn
        posiciones_spawn = [(9, 9), (9, 8), (8, 9)]

        for i in range(self.cantidad_enemigos):
            # Usar posiciones diferentes o la misma si no hay más
            spawn_f, spawn_c = posiciones_spawn[i] if i < len(posiciones_spawn) else (9, 9) #TODO:Revisar despues como sirve esto porque en realidad creo que no lo necesitamos
            
            enemigo = Enemigo(spawn_f, spawn_c)
            self.enemigos.append(enemigo)
            self.dibujar_enemigo(enemigo) 
        
        # Para que la ventana detecte teclas
        self.focus_set()

        #Movimiento por cada enemigo individual
        for enemigo in self.enemigos:
            self.mover_enemigo(enemigo)

    def eliminar_trampa(self,nf_eliminar,nc_eliminar):

        self.mapa[nf_eliminar][nc_eliminar] = Camino()

         # Buscar y eliminar la coordenada de la lista de trampas activas
        for i, (nf, nc) in enumerate(self.trampas_activas):
            if nf == nf_eliminar and nc == nc_eliminar:
                self.trampas_activas.pop(i)
                break  

        #Redibujamos camino
        x1 = nc_eliminar * 40  
        y1 = nf_eliminar * 40
        x2 = x1 + 40
        y2 = y1 + 40

        self.dibujar_camino(x1,y1,x2,y2)
        return

    def bajar_contador_trampa(self):
        if self.contador_trampa > 0:
            self.contador_trampa -= 1
            self.after(1000, self.bajar_contador_trampa)
        else:
            self.contador_activo = False  # Marcar que terminó el contador
        
        #Volvera a llamarse despues de 1 segundo
        

    def poner_trampa(self,event):

        if self.modo == "cazador":
            return
        nf = self.j_fila
        nc = self.j_col

        if not isinstance(self.mapa[nf][nc], Tunel) and self.contador_trampa == 0:
            self.mapa[nf][nc] = Trampa()
            self.contador_trampa = 5  # Cooldown de 5 segundos
            self.trampas_activas.append((nf,nc))

            
            
            if len(self.trampas_activas) > self.max_trampas:
                coordenadas_trampa_vieja = self.trampas_activas.pop(0)
                nf_eliminar = coordenadas_trampa_vieja[0]
                nc_eliminar = coordenadas_trampa_vieja[1]
                self.eliminar_trampa(nf_eliminar,nc_eliminar)
                #self.mapa[nf_eliminar][nc_eliminar] = Camino()

            # Dibujamos la trampa
            x1 = nc * 40  
            y1 = nf * 40
            x2 = x1 + 40
            y2 = y1 + 40    
            
            #self.canvas.create_rectangle(x1, y1, x2, y2, fill="lightgreen", outline="gray")

            self.dibujar_camino(x1,y1,x2,y2)

            
            #Maya diagonal derecha -> \
            self.canvas.create_line(x1+0, y1+30, x1+5, y1+40, fill="black")
            self.canvas.create_line(x1+0, y1+20, x1+10, y1+40, fill="black")
            self.canvas.create_line(x1+0, y1+10, x1+15, y1+40, fill="black")
            self.canvas.create_line(x1+0, y1+0, x1+20, y1+40, fill="black")

            self.canvas.create_line(x1+5, y1+0, x1+25, y1+40, fill="black")
            self.canvas.create_line(x1+10, y1+0, x1+30, y1+40, fill="black")
            self.canvas.create_line(x1+15, y1+0, x1+35, y1+40, fill="black")
            self.canvas.create_line(x1+20, y1+0, x1+40, y1+40, fill="black")
            self.canvas.create_line(x1+25, y1+0, x1+40, y1+30, fill="black")

            self.canvas.create_line(x1+30, y1+0, x1+40, y1+20, fill="black")
            self.canvas.create_line(x1+35, y1+0, x1+40, y1+10, fill="black")

            #Maya diagonal izquierda -> 
            self.canvas.create_line(x1+40, y1+30, x1+35, y1+40, fill="black")
            self.canvas.create_line(x1+40, y1+20, x1+30, y1+40, fill="black")
            self.canvas.create_line(x1+40, y1+10, x1+25, y1+40, fill="black")
            self.canvas.create_line(x1+40, y1+0, x1+20, y1+40, fill="black")

            self.canvas.create_line(x1+35, y1+0, x1+15, y1+40, fill="black")
            self.canvas.create_line(x1+30, y1+0, x1+10, y1+40, fill="black")
            self.canvas.create_line(x1+25, y1+0, x1+5, y1+40, fill="black")

            self.canvas.create_line(x1+20, y1+0, x1+0, y1+40, fill="black")
            self.canvas.create_line(x1+15, y1+0, x1+0, y1+30, fill="black")
            self.canvas.create_line(x1+10, y1+0, x1+0, y1+20, fill="black")
            self.canvas.create_line(x1+5, y1+0, x1+0, y1+10, fill="black")


            self.dibujar_jugador()

            if not self.contador_activo: 
                self.contador_activo = True
                self.bajar_contador_trampa()

    def cazador_palma(self, enemigo):

        #Cada elemento en el grafico lo eliminamos graficamente
        for elemento in enemigo.grafico:
            self.canvas.delete(elemento)
        
        # La lista con el grafico del enemigo es reiniciado
        enemigo.grafico = []

        enemigo.estado = "muerto"
        enemigo.tiempo_reaparicion = 10
        
        # Poner al enemigo fuera del mapa
        enemigo.fila = -1
        enemigo.col = -1

        # Contador de 10 segundos para reaparecer
        self.after(1000, lambda: self.contador_reaparicion(enemigo))
        #return
    
    def contador_reaparicion(self, enemigo):
        enemigo.tiempo_reaparicion -= 1

        #Si timer no terminado recursa, si si respaun
        if enemigo.tiempo_reaparicion > 0:
            self.after(1000, lambda: self.contador_reaparicion(enemigo))
        else:
            self.respawn_enemigo(enemigo)

    """def reaparece_enemigo(self, enemigo):
        enemigo.fila = 9
        enemigo.col = 9
        #enemigo.estado = "activo"
        self.respawn_enemigo(enemigo)"""       

    def respawn_enemigo(self,enemigo):
        # Opción 1: Siempre en la misma esquina
        enemigo.fila = 9
        enemigo.col = 9

        enemigo.estado = "activo"
        
        # Dibujar de nuevo
        self.dibujar_enemigo(enemigo) 
        self.mover_enemigo(enemigo)

    def dibujar_camino(self,x1,y1,x2,y2):
        self.canvas.create_rectangle(x1, y1, x2, y2, fill="lightgreen", outline="gray")

        self.canvas.create_line(x1+10, y1+33, x1+13, y1+30, fill="darkgreen")
        self.canvas.create_line(x1+10, y1+13, x1+13, y1+10, fill="darkgreen")

        self.canvas.create_line(x1+15, y1+20, x1+18, y1+17, fill="darkgreen")

        self.canvas.create_line(x1+25, y1+10, x1+28, y1+7, fill="darkgreen")
        self.canvas.create_line(x1+26, y1+28, x1+29, y1+25, fill="darkgreen")

        self.canvas.create_line(x1+33, y1+13, x1+36, y1+10, fill="darkgreen")
        self.canvas.create_line(x1+33, y1+33, x1+36, y1+30, fill="darkgreen")

    def dibujar_salida(self, x1, y1, x2, y2):
        # Dibujar base del piso (camino)
        self.dibujar_camino(x1, y1, x2, y2)

        # Dibujar marco de la puerta
        self.canvas.create_rectangle(
            x1 + 8, y1 + 6,
            x2 - 8, y2 - 4,
            fill="#8B4513", outline="black"
        )

        # Dividir como puerta doble
        self.canvas.create_line(
            (x1 + x2) // 2, y1 + 6,
            (x1 + x2) // 2, y2 - 4,
            fill="black"
        )

        # Manija
        self.canvas.create_oval(
            x2 - 14, (y1 + y2) // 2 - 2,
            x2 - 10, (y1 + y2) // 2 + 2,
            fill="gold", outline="black"
        )

    # Dibuja cada casilla para el mapa
    def dibujar_mapa(self):
        tam = 40  # tamaño de cada casilla (40x40 px)
        """casillas_dejar_libre = [(0,0),(0,1),(1,0),
                                (9,9),(9,8),(9,7),
                                (8,9),(8,8),(8,7)
            ]"""

        for f in range(10):
            for c in range(10):
                casilla_verificar = (f,c)
                #if casilla_verificar not in casillas_dejar_libre:
                casilla = cargar_casilla(self.mapa[f][c])                
                #else:
                    #casilla = "c" 
                    #c = Camino()      #not ((f == 9 and c == 9) or (f == 9 and c == 8) or (f == 8 and c == 9)) else c

                x1 = c * tam
                y1 = f * tam
                x2 = x1 + tam
                y2 = y1 + tam

                #--------------------------- CAMINO ---------------------------
                if casilla == "c":

                    # Si esta casilla es la salida entonces dibujar puerta
                    if f == self.s_fila and c == self.s_col:
                        self.dibujar_salida(x1, y1, x2, y2)
                    else:
                        self.dibujar_camino(x1, y1, x2, y2)

                #--------------------------- MURO ---------------------------
                elif casilla == "m":

                    # Fondo del muro
                    self.canvas.create_rectangle(
                        x1, y1, x2, y2,
                        fill="#45494B", outline="#45494B"
                    )

                    # Texturas izquierda
                    self.canvas.create_rectangle(x1+0,  y1+0,  x1+15, y1+13, fill="#282A2B", outline="")
                    self.canvas.create_rectangle(x1+0,  y1+15, x1+30, y1+28, fill="#282A2B", outline="")
                    self.canvas.create_rectangle(x1+0,  y1+30, x1+15, y1+40, fill="#282A2B", outline="")

                    # Texturas derecha
                    self.canvas.create_rectangle(x1+17, y1+0,  x1+40, y1+13, fill="#282A2B", outline="")
                    self.canvas.create_rectangle(x1+32, y1+15, x1+40, y1+28, fill="#282A2B", outline="")
                    self.canvas.create_rectangle(x1+17, y1+30, x1+40, y1+40, fill="#282A2B", outline="")

                #--------------------------- LIANA ---------------------------
                elif casilla == "l":

                    # Fondo
                    self.canvas.create_rectangle(x1, y1, x2, y2, fill="lightgreen", outline="gray")

                    # Lianas – parte alta (3)
                    self.canvas.create_rectangle(x1+9,  y1+0, x1+14, y1+15, fill="#1A5827", outline="#193F21")
                    self.canvas.create_rectangle(x1+19, y1+0, x1+24, y1+15, fill="#1A5827", outline="#193F21")
                    self.canvas.create_rectangle(x1+29, y1+0, x1+34, y1+15, fill="#1A5827", outline="#193F21")

                    # Lianas – parte alta (color claro)
                    self.canvas.create_rectangle(x1+10, y1+0, x1+13, y1+15, fill="#14C43A", outline="#14C43A")
                    self.canvas.create_rectangle(x1+20, y1+0, x1+23, y1+15, fill="#14C43A", outline="#14C43A")
                    self.canvas.create_rectangle(x1+30, y1+0, x1+33, y1+15, fill="#14C43A", outline="#14C43A")

                    # Lianas – parte media (oscuro)
                    self.canvas.create_rectangle(x1+11, y1+15, x1+16, y1+30, fill="#1A5827", outline="#193F21")
                    self.canvas.create_rectangle(x1+21, y1+15, x1+26, y1+30, fill="#1A5827", outline="#193F21")
                    self.canvas.create_rectangle(x1+31, y1+15, x1+36, y1+30, fill="#1A5827", outline="#193F21")

                    # Lianas – parte media (claro)
                    self.canvas.create_rectangle(x1+12, y1+15, x1+15, y1+30, fill="#14C43A", outline="#14C43A")
                    self.canvas.create_rectangle(x1+22, y1+15, x1+25, y1+30, fill="#14C43A", outline="#14C43A")
                    self.canvas.create_rectangle(x1+32, y1+15, x1+35, y1+30, fill="#14C43A", outline="#14C43A")

                    # Lianas – parte baja (oscuro)
                    self.canvas.create_rectangle(x1+9,  y1+30, x1+14, y1+37, fill="#1A5827", outline="#193F21")
                    self.canvas.create_rectangle(x1+19, y1+30, x1+24, y1+37, fill="#1A5827", outline="#193F21")
                    self.canvas.create_rectangle(x1+29, y1+30, x1+34, y1+37, fill="#1A5827", outline="#193F21")

                    # Lianas – parte baja (claro)
                    self.canvas.create_rectangle(x1+10, y1+30, x1+13, y1+37, fill="#14C43A", outline="#14C43A")
                    self.canvas.create_rectangle(x1+20, y1+30, x1+23, y1+37, fill="#14C43A", outline="#14C43A")
                    self.canvas.create_rectangle(x1+30, y1+30, x1+33, y1+37, fill="#14C43A", outline="#14C43A")

                #--------------------------- TÚNEL ---------------------------
                else:
                    # Fondo
                    self.canvas.create_rectangle(x1, y1, x2, y2, fill="#686262")

                    # Capas del túnel
                    self.canvas.create_rectangle(x1+10, y1+25, x1+30, y2, fill="#333030", outline="#333030")
                    self.canvas.create_rectangle(x1+15, y1+15, x1+25, y1+25, fill="#333030", outline="#333030")
                    self.canvas.create_rectangle(x1+19, y1+10, x1+21, y1+15, fill="#333030", outline="#333030")

    def jugador_es_cazador(self):
        return self.modo == "cazador"

    def enemigo_es_cazador(self):
        return self.modo == "escapa"
    
    def dibujar_jugador(self):

        #Base del jugador para ponerle cosas encima
        x_base = self.j_col * self.tam
        y_base = self.j_fila * self.tam

        # El jugador va a ser un cuadro rojo, igual por ahora :^ (Vamos a cambiar eso muejejeje)
        self.jugador_grafico = []

        #sombrero de aventurero
        sombrero_top = self.canvas.create_rectangle(

            x_base + 12, y_base + 2,    
            x_base + 28, y_base + 4,
            fill="saddlebrown", outline="black"
        )
        self.jugador_grafico.append(sombrero_top)

        # Sombrero - parte grande (ala)
        sombrero_bottom = self.canvas.create_rectangle(
            x_base + 8, y_base + 4,       # Justo debajo del pico
            x_base + 32, y_base + 8,
            fill="saddlebrown", outline="black"
        )
        self.jugador_grafico.append(sombrero_bottom)

        # Cuerpo
        cuerpo = self.canvas.create_rectangle(
            x_base + 10, y_base + 10,
            x_base + 30, y_base + 28,
            fill="tan", outline="black"
        )
        self.jugador_grafico.append(cuerpo)

        # Camisa: rojo si es cazador, verde si no
        color_camisa = "red" if self.jugador_es_cazador() else "green"
        camisa = self.canvas.create_rectangle(
            x_base + 10, y_base + 20,
            x_base + 30, y_base + 40,
            fill=color_camisa, outline="black"
        )
        self.jugador_grafico.append(camisa)

        # Si el jugador es cazador entonces dibujar arma
        if self.jugador_es_cazador():
            arma_top = self.canvas.create_rectangle(
                x_base + 5, y_base + 25,
                x_base + 20, y_base + 27,
                fill="black", outline="black"
            )
            self.jugador_grafico.append(arma_top)

            arma_bottom = self.canvas.create_rectangle(
                x_base + 17, y_base + 27,
                x_base + 23, y_base + 29,
                fill="black", outline="black"
            )
            self.jugador_grafico.append(arma_bottom)
  

    def dibujar_enemigo(self,enemigo):

        # borrar gráfico anterior si existe
        if hasattr(self, "enemigo_grafico"):
            for elem in enemigo.grafico:
                self.canvas.delete(elem)

        #Base del enemigo para ponerle cosas encima
        x_base = enemigo.col * self.tam
        y_base = enemigo.fila * self.tam

        enemigo.grafico = []

        #sombrero de aventurero (top)
        sombrero_top = self.canvas.create_rectangle(
        x_base + 12, y_base + 2,    
        x_base + 28, y_base + 4,
        fill="saddlebrown", outline="black"
        )
        enemigo.grafico.append(sombrero_top)

        # Sombrero - parte de abajo (bottom)
        sombrero_bottom = self.canvas.create_rectangle(
        x_base + 8, y_base + 4,       
        x_base + 32, y_base + 8,
        fill="saddlebrown", outline="black"
        )
        enemigo.grafico.append(sombrero_bottom)

        # Cuerpo
        cuerpo = self.canvas.create_rectangle(
        x_base + 10, y_base + 10,
        x_base + 30, y_base + 28,
        fill="tan", outline="black"
        )
        enemigo.grafico.append(cuerpo)

        # Camisa: rojo si él es cazador, verde si no
        color_camisa = "red" if self.enemigo_es_cazador() else "green"
        camisa = self.canvas.create_rectangle(
            x_base + 10, y_base + 20,
            x_base + 30, y_base + 40,
            fill=color_camisa, outline="black"
        )
        enemigo.grafico.append(camisa)

        # Si el enemigo es cazador entonces arma
        if self.enemigo_es_cazador():
            arma_top = self.canvas.create_rectangle(
                x_base + 5, y_base + 25,
                x_base + 20, y_base + 27,
                fill="black", outline="black"
            )
            enemigo.grafico.append(arma_top)

            arma_bottom = self.canvas.create_rectangle(
                x_base + 17, y_base + 27,
                x_base + 23, y_base + 29,
                fill="black", outline="black"
            )
            enemigo.grafico.append(arma_bottom)

    #Para verificar de que si se pueda mover a lo que quiere moverse
    def puede_moverse_a (self,nf,nc):
        # Está fuera del mapp
        if nf < 0 or nf >= 10 or nc < 0 or nc >= 10:
            return False

        casilla = self.mapa[nf][nc]
        # Muros nunca se pueden atravesar
        if isinstance(casilla, Muro):
            return False

        # Trampas siempre se pueden pisar
        if isinstance(casilla, Trampa):
            return True

        # ESCAPA entonces jugador es escapador: usa caminos + túneles
        if self.modo == "escapa":
            return isinstance(casilla, (Camino, Tunel))

        # CAZADOR entonces jugador es cazador: usa caminos + lianas
        else:
            return isinstance(casilla, (Camino, Liana))
    
    def enemigo_moverse_a (self,nf,nc):
        if nf < 0 or nf >= 10 or nc < 0 or nc >= 10:
            return False
        
        casilla= self.mapa[nf][nc]
        if isinstance(casilla, Muro):
            return False

        if isinstance(casilla, Trampa):
            return True

        # ESCAPA entonces enemigo es cazador: usa caminos + lianas
        if self.modo == "escapa":
            return isinstance(casilla, (Camino, Liana))

        # CAZADOR entonces enemigo es escapador: usa caminos + túneles
        else:
            return isinstance(casilla, (Camino, Tunel))
    
    def calcular_puntaje(self,tiempo):
        puntaje = 1000000
        if self.modo == "escapa":
            return puntaje - tiempo *1000
        else:
            return puntaje - tiempo * 800
    
    #--------------------------- ENERGÍA ---------------------------
    def actualizar_barra_energia(self):
        self.barra_energia.delete("all")

        energia = self.jugador.energia
        largo = int((energia / 100) * 380)

        # Fondo
        self.barra_energia.create_rectangle(10, 5, 390, 15, outline="black")

        # Energía actual
        color = "green" if energia > 50 else "orange" if energia > 20 else "red"
        self.barra_energia.create_rectangle(10, 5, 10 + largo, 15, fill=color)


    def regenerar_energia(self):
        if self.jugador.energia < 100:
            self.jugador.energia += 1
            self.actualizar_barra_energia()

        self.after(self.regen_rate, self.regenerar_energia)


    def correr(self, event):
        if self.modo == "escapa":
            self.corriendo = True

    def soltar_correr(self, event):
        self.corriendo = False
    #-------------- Moverse del jugador --------------
    def mover (self,df,dc):
        #El cazador no corre 
        if self.modo == "cazador":
            self.corriendo = False 

        pasos = 2 if self.corriendo and self.jugador.gastar_energia(self.costo_correr) else 1

        # Si la energía llegó a 0, dejar de correr
        if self.jugador.energia <= 0:
            self.corriendo = False

        # Actualizar barra siempre
        self.actualizar_barra_energia()

        for _ in range(pasos):
            nf = self.j_fila + df
            nc = self.j_col + dc

            if self.puede_moverse_a(nf, nc):
                self.j_fila = nf
                self.j_col = nc

                for elemento in self.jugador_grafico:
                    self.canvas.move(elemento, dc * self.tam, df * self.tam)

                # --- Condición de victoria normal ---
                if self.modo == "escapa":
                    if not self.juego_terminado and self.j_fila == self.s_fila and self.j_col == self.s_col:
                        self.juego_terminado = True
                        tiempo_transcurrido = int(time.time() - self.tiempo_inicio)
                        puntaje_ganado = self.calcular_puntaje(tiempo_transcurrido)
                        puntajes = Puntajes()
                        puntajes.agregar(self.jugador.nombre, puntaje_ganado, "escapa")
                        self.juego_terminado = True   # <<< Detiene IA inmediatamente
                        messagebox.showinfo("Victoria", "¡Has llegado a la salida!")
                        self.destroy()
                        return

                # --- Condición de victoria si SOY CAZADOR ---
                if self.modo == "cazador" and not self.juego_terminado:
                    # Solo si estoy exactamente en la misma casilla del escapador
                    for enemigo in self.enemigos:
                        if enemigo.estado == "activo" and self.j_fila == enemigo.fila and self.j_col == enemigo.col:
                            self.juego_terminado = True

                            tiempo_transcurrido = int(time.time() - self.tiempo_inicio)
                            puntaje_ganado = self.calcular_puntaje(tiempo_transcurrido)

                            puntajes = Puntajes()
                            puntajes.agregar(self.jugador.nombre, puntaje_ganado, "cazador")

                            messagebox.showinfo("Victoria", "¡Atrapaste al escapador!")
                            self.destroy()
                            return

            else:
                break  # Si no puede avanzar más, detener

        # Si el modo es escapador, el enemigo debe actualizar tu posición como objetivo
        if self.jugador.modo_de_juego == "escapa":
            self.objetivo_fila = self.j_fila
            self.objetivo_col = self.j_col

    #Movimientos del jugador
    def mover_arriba(self, event):
        self.mover(-1, 0)

    def mover_abajo(self, event):
        self.mover(1, 0)

    def mover_izquierda(self, event):
        self.mover(0, -1)

    def mover_derecha(self, event):
        self.mover(0, 1)

    def siguiente_paso_hacia(self, origen_f, origen_c, dest_f, dest_c):
        """Devuelve (nf, nc) = siguiente casilla para acercarse a (dest_f, dest_c)
        usando BFS. Si no hay camino, devuelve None.
        """
        from collections import deque

        n = 10
        visitado = [[False]*n for _ in range(n)]
        padre = [[None]*n for _ in range(n)]

        q = deque()
        q.append((origen_f, origen_c))
        visitado[origen_f][origen_c] = True

        while q:
            f, c = q.popleft()

            # Llegamos al destino
            if f == dest_f and c == dest_c:
                break

            for df, dc in [(1,0), (-1,0), (0,1), (0,-1)]:
                nf = f + df
                nc = c + dc

                if 0 <= nf < n and 0 <= nc < n and not visitado[nf][nc]:
                    if self.enemigo_moverse_a(nf, nc):
                        visitado[nf][nc] = True
                        padre[nf][nc] = (f, c)
                        q.append((nf, nc))

        # Si el destino no fue visitado, no hay camino
        if not (0 <= dest_f < n and 0 <= dest_c < n) or not visitado[dest_f][dest_c]:
            return None

        # Reconstruir el camino desde el destino hasta el origen
        cf, cc = dest_f, dest_c

        # Si ya estamos en el destino, no hay que moverse
        if (cf, cc) == (origen_f, origen_c):
            return None

        while padre[cf][cc] is not None and padre[cf][cc] != (origen_f, origen_c):
            cf, cc = padre[cf][cc]

        return cf, cc


    #-------------- Moverse del enemigo --------------
    def mover_enemigo(self,enemigo):
        if self.juego_terminado:
            return  #se deja de move cuando el jugador haya ganado o perdido

        # Si el enemigo está eliminado por trampa, no hacer nada
        if self.e_fila < 0:
            return

        # Elegir destino según modo
        if self.modo == "escapa":
            # En este modo, el enemigo es el cazador entonces persigue al jugador
            dest_f = self.j_fila
            dest_c = self.j_col
        else:
            # En modo cazador, el enemigo es el escapador entonces huye hacia la salida
            dest_f = self.s_fila
            dest_c = self.s_col

        # Calcular siguiente paso usando BFS
        siguiente = self.siguiente_paso_hacia(enemigo.fila, enemigo.col, dest_f, dest_c)

        if siguiente is not None:
            nf, nc = siguiente

            # Mover gráficamente
            df = nf - enemigo.fila  
            dc = nc - enemigo.col   

            enemigo.fila = nf
            enemigo.col = nc

            for elemento in enemigo.grafico:
                self.canvas.move(elemento, dc * self.tam, df * self.tam)

        # Verificar si atrapo al jugador 
        # Solo aplica cuando yo soy el escapador
        if self.modo == "escapa":
            if enemigo.fila == self.j_fila and enemigo.col == self.j_col:  
                self.juego_terminado = True
                messagebox.showerror("Derrota", "Te atraparon\nPerdiste.")
                self.destroy()
                return

        # === Si el enemigo es escapador y llega a la salida entonces jugador pierde ===
        if self.modo == "cazador":
            if enemigo.fila == self.s_fila and enemigo.col == self.s_col:
                messagebox.showerror("Derrota", "El escapador llegó a la salida.\n¡Perdiste!")
                self.destroy()
                return

        # === Si cae en trampa ===
        casilla_actual = self.mapa[enemigo.fila][enemigo.col] 

        if isinstance(casilla_actual, Trampa):
            self.eliminar_trampa(enemigo.fila, enemigo.col)
            self.cazador_palma(enemigo)
            return

        # Repetir en cierto tiempo (velocidad del enemigo)
        self.after(self.vel_enemigo, lambda: self.mover_enemigo(enemigo))

class Ventana_modo_de_juego(tk.Toplevel):
    def __init__(self, parent, nombre_jugador):
        super().__init__(parent)
        self.title("Seleccion de modo")
        self.geometry("400x300")
        self.nombre_jugador = nombre_jugador
        self.modo_elegido = None

        tk.Label(self, text="Elige modo de juego:", font=("Arial", 10)).pack(pady=20)

        tk.Button(self, text="Escapa", command=self.modo_escapa,
                  width=15, height=3).pack(pady=10)
        
        tk.Button(self, text="Cazador", command=self.modo_cazador,
                  width=15, height=3).pack(pady=10)

    def modo_escapa(self):
        self.modo_elegido = "escapa"
        self.destroy()

    def modo_cazador(self):
        self.modo_elegido = "cazador"
        self.destroy()

class VentanaDificultad(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.title("Seleccionar dificultad")
        self.geometry("400x250")
        self.dificultad = None

        tk.Label(self, text="Elige la dificultad:", font=("Arial", 12)).pack(pady=20)

        tk.Button(self, text="Fácil", width=15, height=2,
                  command=lambda: self.seleccionar("facil")).pack(pady=5)

        tk.Button(self, text="Medio", width=15, height=2,
                  command=lambda: self.seleccionar("medio")).pack(pady=5)

        tk.Button(self, text="Difícil", width=15, height=2,
                  command=lambda: self.seleccionar("dificil")).pack(pady=5)

    def seleccionar(self, diff):
        self.dificultad = diff
        self.destroy()



#---------------------------PROGRAMA PRINCIPAL---------------------------
if __name__ == "__main__":
    app = VentanaMenu()
    app.mainloop()