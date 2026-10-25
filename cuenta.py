from kivy.app import App
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.label import Label
from kivy.graphics import Color, Ellipse, Line
from math import sin, cos, radians

try:
    from plyer import gps
except ImportError:
    gps = None

class AutoSpeedometerLayout(FloatLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        self.current_speed = 0.0
        self.max_speed = 100.0  # Velocidad máxima del dial en km/h

        # Etiqueta digital inferior para lectura exacta de velocidad
        self.digital_label = Label(
            text="0 km/h",
            font_size=28,
            bold=True,
            color=(0.9, 0.9, 0.9, 1),
            pos_hint={'center_x': 0.5, 'center_y': 0.32}
        )
        self.add_widget(self.digital_label)

        # Lienzo gráfico para el dial analógico y la aguja
        with self.canvas.before:
            # Fondo oscuro del tacómetro
            Color(0.08, 0.09, 0.12, 1)
            self.bg_dial = Ellipse(size=(300, 300), pos=(0, 0))
            
            # Anillo exterior cian brillante
            Color(0, 0.7, 0.9, 1)
            self.outer_ring = Line(circle=(0, 0, 150), width=4)
            
            # Línea de la aguja analógica (roja estilo competición)
            Color(1, 0.2, 0.2, 1)
            self.needle = Line(points=[0, 0, 0, 0], width=3)
            
            # Eje central de la aguja
            Color(0.2, 0.2, 0.25, 1)
            self.center_cap = Ellipse(size=(20, 20), pos=(0, 0))

        # Marca central solicitada
        self.brand_label = Label(
            text="SCOOTER PRO",
            font_size=18,
            bold=True,
            color=(0.5, 0.6, 0.7, 1),
            pos_hint={'center_x': 0.5, 'center_y': 0.58}
        )
        self.add_widget(self.brand_label)

        self.bind(size=self.update_graphics, pos=self.update_graphics)

        # Iniciar el GPS de forma automática al arrancar la app
        if gps:
            try:
                gps.configure(on_location=self.on_location, on_status=self.on_status)
                # minTime=400 para alta fluidez, minDistance=0 para capturar cada variación
                gps.start(minTime=400, minDistance=0)
            except NotImplementedError:
                self.digital_label.text = "GPS no compatible"
            except Exception as e:
                self.digital_label.text = f"Error GPS"

    def update_graphics(self, *args):
        size = min(self.width, self.height) * 0.65
        cx = self.center_x
        cy = self.center_y + 20
        
        self.bg_dial.pos = (cx - size / 2, cy - size / 2)
        self.bg_dial.size = (size, size)
        
        self.outer_ring.circle = (cx, cy, size / 2)
        self.center_cap.pos = (cx - 10, cy - 10)
        self.center_cap.size = (20, 20)
        
        self.update_needle()

    def update_needle(self):
        size = min(self.width, self.height) * 0.65
        radius = (size / 2) - 25
        cx = self.center_x
        cy = self.center_y + 20

        # Mapeo de velocidad a ángulos (de 225° a -45° -> 270 grados de recorrido)
        speed_clamped = min(max(self.current_speed, 0), self.max_speed)
        fraction = speed_clamped / self.max_speed
        angle_deg = 225 - (fraction * 270)
        angle_rad = radians(angle_deg)

        nx = cx + radius * cos(angle_rad)
        ny = cy + radius * sin(angle_rad)

        self.needle.points = [cx, cy, nx, ny]

    def on_location(self, **kwargs):
        speed_ms = kwargs.get('speed', 0.0)
        if speed_ms is not None:
            speed_kmh = speed_ms * 3.6
            self.current_speed = max(0.0, speed_kmh)
            self.digital_label.text = f"{int(round(self.current_speed))} km/h"
            self.update_needle()

    def on_status(self, *args, **kwargs):
        pass

class AutoSpeedometerApp(App):
    def build(self):
        return AutoSpeedometerLayout()

if __name__ == '__main__':
    AutoSpeedometerApp().run()