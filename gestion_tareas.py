import heapq
import json
from datetime import datetime


class GestorTareas:
    def __init__(self, archivo="tareas.json"):
        self.tareas = []  # Cola de prioridad (heap)
        self.tareas_completadas = set()
        self.archivo = archivo
        self.cargar_datos()

    def agregar_tarea(self, nombre, prioridad, fecha_vencimiento, dependencias=None):
        """Agregar una nueva tarea."""
        if not isinstance(prioridad, int) or prioridad < 0:
            raise ValueError("La prioridad debe ser un número entero no negativo.")
        if dependencias is None:
            dependencias = []

        try:
            fecha_vencimiento = datetime.strptime(fecha_vencimiento, "%Y-%m-%d")
        except ValueError:
            raise ValueError("La fecha de vencimiento debe tener el formato AAAA-MM-DD.")

        tarea = {
            "nombre": nombre,
            "prioridad": prioridad,
            "fecha_vencimiento": fecha_vencimiento.strftime("%Y-%m-%d"),
            "dependencias": dependencias,
        }

        heapq.heappush(self.tareas, (-prioridad, fecha_vencimiento, tarea))
        self.guardar_datos()

    def listar_tareas(self, ordenar_por="prioridad"):
        """Listar todas las tareas pendientes."""
        tareas_pendientes = [
            tarea for _, _, tarea in self.tareas if tarea["nombre"] not in self.tareas_completadas
        ]

        if ordenar_por == "fecha":
            return sorted(
                tareas_pendientes, key=lambda t: datetime.strptime(t["fecha_vencimiento"], "%Y-%m-%d")
            )
        elif ordenar_por == "prioridad":
            return sorted(tareas_pendientes, key=lambda t: t["prioridad"], reverse=True)
        else:
            raise ValueError("El criterio de ordenación debe ser 'prioridad' o 'fecha'.")

    def completar_tarea(self, nombre):
        """Marcar una tarea como completada."""
        if nombre in self.tareas_completadas:
            print(f"La tarea '{nombre}' ya está completada.")
        else:
            self.tareas_completadas.add(nombre)
            self.guardar_datos()

    def obtener_siguiente_tarea(self):
        """Obtener la tarea con mayor prioridad."""
        while self.tareas:
            _, _, tarea = self.tareas[0]
            if tarea["nombre"] not in self.tareas_completadas:
                return tarea
            heapq.heappop(self.tareas)  # Eliminar la tarea completada del heap
        return None  # No hay tareas disponibles

    def es_ejecutable(self, nombre):
        """Verificar si una tarea es ejecutable (todas sus dependencias están completadas)."""
        for _, _, tarea in self.tareas:
            if tarea["nombre"] == nombre:
                for dependencia in tarea["dependencias"]:
                    if dependencia not in self.tareas_completadas:
                        return False  # Alguna dependencia no está completada
                return True  # Todas las dependencias están completadas
        return False  # La tarea no existe

    def guardar_datos(self):
        """Guardar las tareas en un archivo JSON."""
        datos = {
            "tareas": [
                {
                    "prioridad": -p,
                    "fecha_vencimiento": t["fecha_vencimiento"],
                    "nombre": t["nombre"],
                    "dependencias": t["dependencias"],
                }
                for p, _, t in self.tareas
            ],
            "completadas": list(self.tareas_completadas),
        }

        with open(self.archivo, "w") as archivo:
            json.dump(datos, archivo, indent=4)

    def cargar_datos(self):
        """Cargar las tareas desde un archivo JSON."""
        try:
            with open(self.archivo, "r") as archivo:
                datos = json.load(archivo)
                self.tareas = [
                    (-t["prioridad"], datetime.strptime(t["fecha_vencimiento"], "%Y-%m-%d"), t)
                    for t in datos.get("tareas", [])
                ]
                self.tareas_completadas = set(datos.get("completadas", []))
        except FileNotFoundError:
            self.tareas = []
            self.tareas_completadas = set()


def menu():
    gestor = GestorTareas()
    
    while True:
        print("\nMenú de Gestión de Tareas:")
        print("1) Añadir nueva tarea")
        print("2) Mostrar tareas pendientes (ordenadas por prioridad o fecha de vencimiento)")
        print("3) Marcar tareas como completadas y eliminarlas")
        print("4) Obtener la siguiente tarea de mayor prioridad")
        print("5) Verificar si una tarea es ejecutable")
        print("6) Salir")
        
        opcion = input("Selecciona una opción: ")
        
        if opcion == "1":
            nombre = input("Nombre de la tarea: ")
            try:
                prioridad = int(input("Prioridad de la tarea (número entero, mayor es más importante): "))
            except ValueError:
                print("La prioridad debe ser un número entero.")
                continue
            dependencias = input("Dependencias (separadas por comas, deja vacío si no hay): ").split(",")
            dependencias = [d.strip() for d in dependencias if d.strip()]
            fecha_vencimiento = input("Fecha de vencimiento (formato AAAA-MM-DD): ")
            try:
                gestor.agregar_tarea(nombre, prioridad, fecha_vencimiento, dependencias)
                print(f"Tarea '{nombre}' añadida con éxito.")
            except ValueError as e:
                print(e)
        
        elif opcion == "2":
            criterio = input("Ordenar tareas por (prioridad/fecha): ").strip().lower()
            if criterio not in ["prioridad", "fecha"]:
                print("Criterio inválido. Usa 'prioridad' o 'fecha'.")
                continue
            tareas = gestor.listar_tareas(ordenar_por=criterio)
            if tareas:
                print(f"Tareas pendientes ordenadas por {criterio}:")
                for tarea in tareas:
                    print(f"- {tarea['nombre']} (Prioridad: {tarea['prioridad']}, Fecha de vencimiento: {tarea['fecha_vencimiento']}, Dependencias: {', '.join(tarea['dependencias'])})")
            else:
                print("No hay tareas pendientes.")
        
        elif opcion == "3":
            nombre = input("Nombre de la tarea a completar: ")
            gestor.completar_tarea(nombre)
            print(f"Tarea '{nombre}' marcada como completada.")
        
        elif opcion == "4":
            tarea = gestor.obtener_siguiente_tarea()
            if tarea:
                print(f"Siguiente tarea: {tarea['nombre']} (Prioridad: {tarea['prioridad']}, Fecha de vencimiento: {tarea['fecha_vencimiento']}, Dependencias: {', '.join(tarea['dependencias'])})")
            else:
                print("No hay tareas disponibles.")
        
        elif opcion == "5":
            nombre = input("Nombre de la tarea para verificar: ")
            if gestor.es_ejecutable(nombre):
                print(f"La tarea '{nombre}' es ejecutable.")
            else:
                print(f"La tarea '{nombre}' no es ejecutable porque tiene dependencias sin completar.")
        
        elif opcion == "6":
            print("Saliendo del gestor de tareas. ¡Hasta luego!")
            break
        
        else:
            print("Opción no válida. Inténtalo de nuevo.")


# Ejecutar el menú
menu()
