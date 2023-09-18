import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
import mysql.connector
from mysql.connector import Error
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
import datetime

# Conectar a la base de datos MySQL
try:
    conexion = mysql.connector.connect(
        host="localhost",
        user="root",
        password="",
        database="tareas_app"
    )
except Error as e:
    messagebox.showerror("Error de conexión", f"No se pudo conectar a la base de datos: {e}")
    exit()

# Función para agregar una tarea a la base de datos
def agregar_tarea():
    titulo = entry_titulo.get()
    descripcion = entry_descripcion.get("1.0", tk.END)
    fecha_limite = entry_fecha_limite.get()
    fecha_asignacion = entry_fecha_asignacion.get()
    persona_asignada = entry_persona_asignada.get()
    persona_asignadora = entry_persona_asignadora.get()
    nivel_prioridad = combo_prioridad.get()

    if not titulo or not fecha_limite:
        messagebox.showerror("Campos requeridos", "Título y Fecha Límite son campos requeridos.")
        return

    cursor = conexion.cursor()
    insert_query = "INSERT INTO tareas (titulo, descripcion, fecha_limite, fecha_asignacion, persona_asignada, persona_asignadora, nivel_prioridad, completado) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"
    try:
        cursor.execute(insert_query, (titulo, descripcion, fecha_limite, fecha_asignacion, persona_asignada, persona_asignadora, nivel_prioridad, False))
        conexion.commit()
        messagebox.showinfo("Éxito", "Tarea agregada correctamente.")
    except Error as e:
        messagebox.showerror("Error al agregar tarea", f"No se pudo agregar la tarea: {e}")
    finally:
        cursor.close()

    entry_titulo.delete(0, tk.END)
    entry_descripcion.delete("1.0", tk.END)
    entry_fecha_limite.delete(0, tk.END)
    entry_fecha_asignacion.delete(0, tk.END)
    entry_persona_asignada.delete(0, tk.END)
    entry_persona_asignadora.delete(0, tk.END)
    combo_prioridad.set("")  # Restablecer la selección del nivel de prioridad

# Función para mostrar tareas en la lista
def mostrar_tareas():
    tree.delete(*tree.get_children())
    cursor = conexion.cursor()
    cursor.execute("SELECT * FROM tareas")
    tareas = cursor.fetchall()
    for tarea in tareas:
        completado = "Sí" if tarea[7] else "No"  # Ajusta el índice para la columna 'completado'
        tree.insert("", "end", values=(tarea[0], tarea[1], tarea[2], tarea[3], tarea[4], tarea[5], tarea[6], completado))
    cursor.close()

# Función para marcar una tarea como completada
def marcar_completado():
    seleccion = tree.selection()
    if not seleccion:
        messagebox.showwarning("Advertencia", "Selecciona una tarea primero.")
    else:
        tarea_id = int(seleccion[0][1:])  # Elimina el prefijo 'I' y convierte a entero
        cursor = conexion.cursor()
        try:
            cursor.execute("UPDATE tareas SET completado = 1 WHERE id = %s", (tarea_id,))
            conexion.commit()
            mostrar_tareas()  # Actualiza la lista de tareas después de marcar una como completada
            generar_grafico()  # Actualiza el gráfico después de marcar una como completada
        except Error as e:
            messagebox.showerror("Error al marcar tarea", f"No se pudo marcar la tarea como completada: {e}")
        finally:
            cursor.close()

# Función para generar un gráfico de tareas completadas
def generar_grafico():
    cursor = conexion.cursor()
    cursor.execute("SELECT COUNT(*) FROM tareas WHERE completado = 1")
    completadas = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM tareas WHERE completado = 0")
    no_completadas = cursor.fetchone()[0]
    cursor.close()

    labels = ['Completadas', 'No Completadas']
    sizes = [completadas, no_completadas]
    colors = ['green', 'red']
    plt.pie(sizes, labels=labels, colors=colors, autopct='%1.1f%%', startangle=140)
    plt.axis('equal')
    plt.title('Tareas Completadas vs. No Completadas')

    fig = plt.gcf()
    fig.set_size_inches(6, 6)  # Ajusta el tamaño del gráfico
    canvas = FigureCanvasTkAgg(fig, master=frame_grafico)
    canvas.get_tk_widget().pack()
    canvas.draw()

# Configurar la ventana principal
ventana = tk.Tk()
ventana.title("Sistema de Tareas")

# Crear y configurar los widgets de la interfaz
frame_agregar = ttk.LabelFrame(ventana, text="Agregar Tarea")
frame_agregar.pack(padx=10, pady=10, fill="both")

frame_listado = ttk.LabelFrame(ventana, text="Listado de Tareas")
frame_listado.pack(padx=10, pady=10, fill="both")

frame_grafico = ttk.LabelFrame(ventana, text="Gráfico de Tareas")
frame_grafico.pack(padx=10, pady=10, fill="both")

label_titulo = ttk.Label(frame_agregar, text="Título:")
label_titulo.grid(row=0, column=0, padx=5, pady=5, sticky="w")

entry_titulo = ttk.Entry(frame_agregar)
entry_titulo.grid(row=0, column=1, padx=5, pady=5, sticky="w")

label_descripcion = ttk.Label(frame_agregar, text="Descripción:")
label_descripcion.grid(row=1, column=0, padx=5, pady=5, sticky="w")

entry_descripcion = tk.Text(frame_agregar, height=5, width=30)
entry_descripcion.grid(row=1, column=1, padx=5, pady=5, sticky="w")

label_fecha_limite = ttk.Label(frame_agregar, text="Fecha Límite:")
label_fecha_limite.grid(row=2, column=0, padx=5, pady=5, sticky="w")

entry_fecha_limite = ttk.Entry(frame_agregar)
entry_fecha_limite.grid(row=2, column=1, padx=5, pady=5, sticky="w")

label_fecha_asignacion = ttk.Label(frame_agregar, text="Fecha de Asignación:")
label_fecha_asignacion.grid(row=3, column=0, padx=5, pady=5, sticky="w")

entry_fecha_asignacion = ttk.Entry(frame_agregar)
entry_fecha_asignacion.grid(row=3, column=1, padx=5, pady=5, sticky="w")

label_persona_asignada = ttk.Label(frame_agregar, text="Persona a la que se le asignó:")
label_persona_asignada.grid(row=4, column=0, padx=5, pady=5, sticky="w")

entry_persona_asignada = ttk.Entry(frame_agregar)
entry_persona_asignada.grid(row=4, column=1, padx=5, pady=5, sticky="w")

label_persona_asignadora = ttk.Label(frame_agregar, text="Persona que asignó la tarea:")
label_persona_asignadora.grid(row=5, column=0, padx=5, pady=5, sticky="w")

entry_persona_asignadora = ttk.Entry(frame_agregar)
entry_persona_asignadora.grid(row=5, column=1, padx=5, pady=5, sticky="w")

label_prioridad = ttk.Label(frame_agregar, text="Nivel de Prioridad:")
label_prioridad.grid(row=6, column=0, padx=5, pady=5, sticky="w")

prioridades = ["ALTA", "MEDIA", "BAJA"]
combo_prioridad = ttk.Combobox(frame_agregar, values=prioridades)
combo_prioridad.grid(row=6, column=1, padx=5, pady=5, sticky="w")

boton_agregar = ttk.Button(frame_agregar, text="Agregar Tarea", command=agregar_tarea)
boton_agregar.grid(row=7, columnspan=2, padx=5, pady=5)

tree = ttk.Treeview(frame_listado, columns=("ID", "Título", "Descripción", "Fecha Límite", "Fecha Asignación", "Persona Asignada", "Persona Asignadora", "Nivel Prioridad", "Completada"), show="headings")
tree.heading("ID", text="ID")
tree.heading("Título", text="Título")
tree.heading("Descripción", text="Descripción")
tree.heading("Fecha Límite", text="Fecha Límite")
tree.heading("Fecha Asignación", text="Fecha Asignación")
tree.heading("Persona Asignada", text="Persona Asignada")
tree.heading("Persona Asignadora", text="Persona Asignadora")
tree.heading("Nivel Prioridad", text="Nivel Prioridad")
tree.heading("Completada", text="Completada")
tree.pack()

boton_mostrar_tareas = ttk.Button(frame_listado, text="Mostrar Tareas", command=mostrar_tareas)
boton_mostrar_tareas.pack()

boton_marcar_completado = ttk.Button(frame_listado, text="Marcar Completado", command=marcar_completado)
boton_marcar_completado.pack()

boton_generar_grafico = ttk.Button(frame_grafico, text="Generar Gráfico", command=generar_grafico)
boton_generar_grafico.pack()

# Función para cerrar la aplicación
def cerrar_aplicacion():
    if messagebox.askokcancel("Salir", "¿Deseas salir de la aplicación?"):
        ventana.destroy()

ventana.protocol("WM_DELETE_WINDOW", cerrar_aplicacion)

# Ejecutar la aplicación
ventana.mainloop()

# Cerrar la conexión a la base de datos al salir de la aplicación
if conexion.is_connected():
    conexion.close()
