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
#contador_trampa = 0

#---------------------------FUNCIONES AUXILIARES---------------------------
def cargar_casilla(c): 
    if isinstance(c, Camino):
        return "c"            #"#bfbfbf"   # gris
    if isinstance(c, Muro):
        return "m"            #"#000000"   # negro
    if isinstance(c, Liana):
        return "l"            #"#2ecc71"   # verde
    if isinstance(c, Tunel):
        return                #"#3498db"   # azul
    return "t"                #"#ffffff"       # blanco por defeto

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
        self.prob_camino= 0.60
        self.prob_muro= 0.20
        self.prob_liana= 0.10
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
        self.geometry("500x500")

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

        # Inicializar el contador de trampa como atributo
        self.contador_trampa = 0

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
        self.bind("<space>", self.poner_trampa) #TODO: Poner algun tipo de validacion (aca o en otro lado) que verifique que no somos cazador
        # Para que la ventana detecte teclas
        self.focus_set()
        self.mover_enemigo()

    def bajar_contador_trampa(self):
        if self.contador_trampa > 0:
            self.contador_trampa -= 1
        print(self.contador_trampa)
        #else:
            #return
        
        #Volvera a llamarse despues de 1 segundo
        self.after(1000, self.bajar_contador_trampa)

    def poner_trampa(self,event):
        nf = self.j_fila
        nc = self.j_col

        if not isinstance(self.mapa[nf][nc], Tunel) and self.contador_trampa == 0:
            self.mapa[nf][nc] = Trampa()
            self.contador_trampa = 5  # Cooldown de 5 segundos
            #print(self.contador_trampa)

            # Dibujamos la trampa
            x1 = nc * 40  # Aquí estaba invertido
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

            #print("Poner trampa")

            self.bajar_contador_trampa()

    def cazador_palma(self):

        #Cada elemento en el grafico lo eliminamos graficamente
        for elemento in self.enemigo_grafico:
            self.canvas.delete(elemento)
        
        # La lista con el grafico del enemigo es reiniciado
        self.enemigo_grafico = []
        
        # Poner al enemigo fuera del mapa
        self.e_fila = -1
        self.e_col = -1

        print("Cazadol GGs")

    def dibujar_camino(self,x1,y1,x2,y2):
        self.canvas.create_rectangle(x1, y1, x2, y2, fill="lightgreen", outline="gray")

        self.canvas.create_line(x1+10, y1+33, x1+13, y1+30, fill="darkgreen")
        self.canvas.create_line(x1+10, y1+13, x1+13, y1+10, fill="darkgreen")

        self.canvas.create_line(x1+15, y1+20, x1+18, y1+17, fill="darkgreen")

        self.canvas.create_line(x1+25, y1+10, x1+28, y1+7, fill="darkgreen")
        self.canvas.create_line(x1+26, y1+28, x1+29, y1+25, fill="darkgreen")

        self.canvas.create_line(x1+33, y1+13, x1+36, y1+10, fill="darkgreen")
        self.canvas.create_line(x1+33, y1+33, x1+36, y1+30, fill="darkgreen")

    # Dibuja cada casilla para el mapa
    def dibujar_mapa(self):
        tam = 40  # tamaño de cada casilla (40x40 px)
        #self.muros

        for f in range(10):
            for c in range(10):
                casilla = self.mapa[f][c]
                casilla = cargar_casilla(casilla) #TODO: CAMBIAR NOMBRE DE ESTA FUNCION O ELIMINARLA POR COMPLETO IDK , CAMBIAR NOMBRE A elegir_casilla POR EJEMPLO
          
                x1 = c * tam
                y1 = f * tam
                x2 = x1 + tam
                y2 = y1 + tam

                if casilla == "c":
                    self.dibujar_camino(x1,y1,x2,y2)


                elif casilla == "m":

                    #Creamos el muro

                    self.canvas.create_rectangle(x1, y1, x2, y2, 
                                                         fill="#45494B", outline="#45494B"
                                                         )

                    #Texturas izquierdas
                    self.canvas.create_rectangle(x1+0, y1+0, x1+15, y1+13, 
                                                         fill="#282A2B", outline=""
                                                         )
                    
                    self.canvas.create_rectangle(x1+0, y1+15, x1+30, y1+28, 
                                                         fill="#282A2B", outline=""
                                                         )
                    
                    self.canvas.create_rectangle(x1+0, y1+30, x1+15, y1+40, 
                                                         fill="#282A2B", outline=""
                                                         )
                    
                    #Texturas derechas
                    self.canvas.create_rectangle(x1+17, y1+0, x1+40, y1+13, 
                                                         fill="#282A2B", outline=""
                                                         )
                    
                    self.canvas.create_rectangle(x1+32, y1+15, x1+40, y1+28, 
                                                         fill="#282A2B", outline=""
                                                         )
                    
                    self.canvas.create_rectangle(x1+17, y1+30, x1+40, y1+40, 
                                                         fill="#282A2B", outline=""
                                                         )


                elif casilla == "l":

                    self.canvas.create_rectangle(x1, y1, x2, y2, fill="lightgreen", outline="gray")

                    #Primera parte de las 3 lianas - outlines oscuros primero
                    self.canvas.create_rectangle(x1+9, y1+0, x1+14, y1+15, 
                                                         fill="#1A5827", outline="#193F21"
                                                         )
                    
                    self.canvas.create_rectangle(x1+19, y1+0, x1+24, y1+15, 
                                                         fill="#1A5827", outline="#193F21"
                                                         )
                    
                    self.canvas.create_rectangle(x1+29, y1+0, x1+34, y1+15, 
                                                         fill="#1A5827", outline="#193F21"
                                                         )
                    
                    #Primera parte de las 3 lianas - colores claros encima
                    self.canvas.create_rectangle(x1+10, y1+0, x1+13, y1+15, 
                                                         fill="#14C43A", outline="#14C43A"
                                                         )
                    
                    self.canvas.create_rectangle(x1+20, y1+0, x1+23, y1+15, 
                                                         fill="#14C43A", outline="#14C43A"
                                                         )
                    
                    self.canvas.create_rectangle(x1+30, y1+0, x1+33, y1+15, 
                                                         fill="#14C43A", outline="#14C43A"
                                                         )
                    
                    #Parte media de las 3 lianas - outlines oscuros primero
                    self.canvas.create_rectangle(x1+11, y1+15, x1+16, y1+30, 
                                                         fill="#1A5827", outline="#193F21"
                                                         )
                    
                    self.canvas.create_rectangle(x1+21, y1+15, x1+26, y1+30, 
                                                         fill="#1A5827", outline="#193F21"
                                                         )
                    
                    self.canvas.create_rectangle(x1+31, y1+15, x1+36, y1+30, 
                                                         fill="#1A5827", outline="#193F21"
                                                         )
                    
                    #Parte media de las 3 lianas - colores claros encima
                    self.canvas.create_rectangle(x1+12, y1+15, x1+15, y1+30, 
                                                         fill="#14C43A", outline="#14C43A"
                                                         )
                    
                    self.canvas.create_rectangle(x1+22, y1+15, x1+25, y1+30, 
                                                         fill="#14C43A", outline="#14C43A"
                                                         )
                    
                    self.canvas.create_rectangle(x1+32, y1+15, x1+35, y1+30, 
                                                         fill="#14C43A", outline="#14C43A"
                                                         )
                    
                    #Parte baja de las 3 lianas - outlines oscuros primero
                    self.canvas.create_rectangle(x1+9, y1+30, x1+14, y1+37, 
                                                         fill="#1A5827", outline="#193F21"
                                                         )
                    
                    self.canvas.create_rectangle(x1+19, y1+30, x1+24, y1+37, 
                                                         fill="#1A5827", outline="#193F21"
                                                         )
                    
                    self.canvas.create_rectangle(x1+29, y1+30, x1+34, y1+37, 
                                                         fill="#1A5827", outline="#193F21"
                                                         )
                    
                    #Parte baja de las 3 lianas - colores claros encima
                    self.canvas.create_rectangle(x1+10, y1+30, x1+13, y1+37, 
                                                         fill="#14C43A", outline="#14C43A"
                                                         )
                    
                    self.canvas.create_rectangle(x1+20, y1+30, x1+23, y1+37, 
                                                         fill="#14C43A", outline="#14C43A"
                                                         )
                    
                    self.canvas.create_rectangle(x1+30, y1+30, x1+33, y1+37, 
                                                         fill="#14C43A", outline="#14C43A"
                                                         )


                else:
                    self.canvas.create_rectangle(x1, y1, x2, y2, fill="#686262")

                    #Crearemos la parte de adentro de el tunel (Rectangulos stacked up cada vez mas pequeños)
                    self.canvas.create_rectangle(x1+10, y1+25, x1+30, y1+40, 
                                                         fill="#333030", outline="#333030"
                                                         )
                    
                    self.canvas.create_rectangle(x1+15, y1+15, x1+25, y1+25, 
                                                         fill="#333030", outline="#333030"
                                                         )
                    
                    self.canvas.create_rectangle(x1+19, y1+10, x1+21, y1+15, 
                                                         fill="#333030", outline="#333030"
                                                         )



                #self.canvas.create_rectangle(x1, y1, x2, y2, fill="color_de_casilla", outline="gray")

    def dibujar_jugador(self):

        #Base del jugador para ponerle cosas encima
        x_base = self.j_col * self.tam
        y_base = self.j_fila * self.tam

        """
        x1 = self.j_col * self.tam
        y1 = self.j_fila * self.tam
        x2 = x1 + self.tam
        y2 = y1 + self.tam
        """

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

        camisa = self.canvas.create_rectangle(
            x_base + 10, y_base + 20,
            x_base + 30, y_base + 40,
            fill="green", outline="black"
        )
        self.jugador_grafico.append(camisa)
  

    def dibujar_enemigo(self):

        """
        x1 = self.e_col * self.tam
        y1 = self.e_fila * self.tam
        x2 = x1 + self.tam
        y2 = y1 + self.tam
        """

        #Base del enemigo para ponerle cosas encima
        x_base = self.e_col * self.tam
        y_base = self.e_fila * self.tam

        self.enemigo_grafico = []

        #sombrero de aventurero
        sombrero_top = self.canvas.create_rectangle(

            x_base + 12, y_base + 2,    
            x_base + 28, y_base + 4,
            fill="saddlebrown", outline="black"
        )
        self.enemigo_grafico.append(sombrero_top)

        # Sombrero - parte grande (ala)
        sombrero_bottom = self.canvas.create_rectangle(
            x_base + 8, y_base + 4,       
            x_base + 32, y_base + 8,
            fill="saddlebrown", outline="black"
        )
        self.enemigo_grafico.append(sombrero_bottom)

        # Cuerpo
        cuerpo = self.canvas.create_rectangle(
            x_base + 10, y_base + 10,
            x_base + 30, y_base + 28,
            fill="tan", outline="black"
        )
        self.enemigo_grafico.append(cuerpo)

        camisa = self.canvas.create_rectangle(
            x_base + 10, y_base + 20,
            x_base + 30, y_base + 40,
            fill="red", outline="black"
        )
        self.enemigo_grafico.append(camisa)

        arma_top = self.canvas.create_rectangle(
            x_base + 5, y_base + 25,
            x_base + 20, y_base + 27,
            fill="black", outline="black"
        )
        self.enemigo_grafico.append(arma_top)

        arma_bottom = self.canvas.create_rectangle(
            x_base + 17, y_base + 27,
            x_base + 23, y_base + 29,
            fill="black", outline="black"
        )
        self.enemigo_grafico.append(arma_bottom)

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
            for elemento in self.jugador_grafico:
                self.canvas.move(elemento, dc * self.tam, df * self.tam)

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
            for elemento in self.enemigo_grafico:
                self.canvas.move(elemento, 0, df * self.tam)

        # Si no pudo, intentar horizontal
        elif dc != 0 and self.enemigo_moverse_a(self.e_fila, self.e_col + dc):
            self.e_col += dc
            for elemento in self.enemigo_grafico:
                self.canvas.move(elemento, dc * self.tam, 0)

        # Para saber si me atrapo (por ahora :p)
        if self.e_fila == self.j_fila and self.e_col == self.j_col:
            print("¡Te atraparon!")
            return

        #Aqui se cambia la velocidad a la que se mueve el enemigo
        self.after(100, self.mover_enemigo)

        casilla_actual = self.mapa[self.e_fila][self.e_col]

        if isinstance(casilla_actual, Trampa): #TODO: AGREGAR VERIFICACION DE SI EL ENEMIGO ES CAZADOR O CASADO (pun intended)
            self.cazador_palma()

#---------------------------PROGRAMA PRINCIPAL---------------------------
if __name__ == "__main__":
    app = VentanaMenu()
    app.mainloop()
