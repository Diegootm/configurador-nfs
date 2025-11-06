import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext

class VentanaPrincipal:
    # este va ha ser la interfaz grafica

    def __init__(self, raiz, gestor_nfs):
        self.raiz = raiz
        self.gestor_nfs = gestor_nfs
        self.configuraciones = []
        self.variables_opciones = {}
        
        self._inicicializar_interfaz()
        self._cargar_configuraciones()

    def _inicicializar_interfaz(self):
        #va a iniciar los componentes de la interfaz

        self.cuaderno = ttk.Notebook(self.raiz)
        self.cuaderno.pack(fill='both', expan=True, padx=10, pady=10)

        #pestanias
        self._crear_pestana_ver_configuraciones()
        self._crear_pestana_agregar_configuracion()
        self._crear_pestana_gestion_configuraciones()

        # barra de estado

        self.barra_estado = ttk.Label(self.raiz, text="Listo", relief=tk.SUNKEN, anchor=tk.W)
        self.barra_estado.pack(side=tk.BOTTOM, fill=tk.X)
    
    def _crear_pestana_ver_configuraciones(self):
        """Crea la pestaña para ver configuraciones actuales"""
        marco_ver = ttk.Frame(self.cuaderno)
        self.cuaderno.add(marco_ver, text="Ver Configuraciones")
        
        # Título
        etiqueta_titulo = ttk.Label(marco_ver, text="Configuraciones NFS Actuales:", 
                                   font=('Arial', 12, 'bold'))
        etiqueta_titulo.pack(pady=5)
        
        # Área de texto para mostrar configuraciones
        self.texto_configuraciones = scrolledtext.ScrolledText(
            marco_ver, 
            width=80, 
            height=20,
            wrap=tk.WORD
        )
        self.texto_configuraciones.pack(fill='both', expand=True, padx=10, pady=5)
        
        # Botones
        marco_botones = ttk.Frame(marco_ver)
        marco_botones.pack(pady=10)
        
        boton_actualizar = ttk.Button(
            marco_botones, 
            text="Actualizar Vista", 
            command=self._cargar_configuraciones
        )
        boton_actualizar.pack(side=tk.LEFT, padx=5)
        
        boton_aplicar_cambios = ttk.Button(
            marco_botones,
            text="Aplicar Cambios NFS",
            command=self._aplicar_cambios_nfs
        )
        boton_aplicar_cambios.pack(side=tk.LEFT, padx=5)
    
    def _crear_pestana_agregar_configuracion(self):
        """Crea la pestaña para agregar nuevas configuraciones"""
        marco_agregar = ttk.Frame(self.cuaderno)
        self.cuaderno.add(marco_agregar, text="Agregar Configuración")
        
        # Campos de entrada
        self._crear_campos_entrada(marco_agregar)
        
        # Opciones NFS
        self._crear_opciones_nfs(marco_agregar)
        
        # Botones
        marco_botones = ttk.Frame(marco_agregar)
        marco_botones.pack(pady=20)
        
        boton_agregar = ttk.Button(
            marco_botones,
            text="Agregar Configuración",
            command=self._agregar_configuracion
        )
        boton_agregar.pack(side=tk.LEFT, padx=5)
        
        boton_limpiar = ttk.Button(
            marco_botones,
            text="Limpiar Campos",
            command=self._limpiar_campos
        )
        boton_limpiar.pack(side=tk.LEFT, padx=5)
    
    def _crear_pestana_gestion_configuraciones(self):
        """Crea la pestaña para modificar/eliminar configuraciones"""
        marco_gestion = ttk.Frame(self.cuaderno)
        self.cuaderno.add(marco_gestion, text="Gestionar Configuraciones")
        
        # Título
        etiqueta_titulo = ttk.Label(marco_gestion, text="Configuraciones Existentes:", 
                                   font=('Arial', 12, 'bold'))
        etiqueta_titulo.pack(pady=5)
        
        # Lista de configuraciones
        marco_lista = ttk.Frame(marco_gestion)
        marco_lista.pack(fill='both', expand=True, padx=10, pady=5)
        
        self.lista_configuraciones = tk.Listbox(marco_lista, height=15)
        barra_desplazamiento = ttk.Scrollbar(marco_lista, orient="vertical", 
                                           command=self.lista_configuraciones.yview)
        self.lista_configuraciones.configure(yscrollcommand=barra_desplazamiento.set)
        
        self.lista_configuraciones.pack(side=tk.LEFT, fill='both', expand=True)
        barra_desplazamiento.pack(side=tk.RIGHT, fill='y')
        
        # Botones de gestión
        marco_botones_gestion = ttk.Frame(marco_gestion)
        marco_botones_gestion.pack(pady=10)
        
        boton_eliminar = ttk.Button(
            marco_botones_gestion,
            text="Eliminar Seleccionada",
            command=self._eliminar_configuracion
        )
        boton_eliminar.pack(side=tk.LEFT, padx=5)
        
        boton_actualizar_lista = ttk.Button(
            marco_botones_gestion,
            text="Actualizar Lista",
            command=self._actualizar_lista_configuraciones
        )
        boton_actualizar_lista.pack(side=tk.LEFT, padx=5)
    
    def _crear_campos_entrada(self, padre):
        """Crea los campos de entrada para carpeta y host"""
        marco_campos = ttk.Frame(padre)
        marco_campos.pack(fill='x', padx=10, pady=10)
        
        # Campo Carpeta
        etiqueta_carpeta = ttk.Label(marco_campos, text="Carpeta a exportar:")
        etiqueta_carpeta.grid(row=0, column=0, sticky='w', pady=5)
        
        self.entrada_carpeta = ttk.Entry(marco_campos, width=50)
        self.entrada_carpeta.grid(row=0, column=1, padx=5, pady=5, sticky='ew')
        
        # Campo Host
        etiqueta_host = ttk.Label(marco_campos, text="Host o Red:")
        etiqueta_host.grid(row=1, column=0, sticky='w', pady=5)
        
        self.entrada_host = ttk.Entry(marco_campos, width=50)
        self.entrada_host.grid(row=1, column=1, padx=5, pady=5, sticky='ew')
        
        # Ejemplos
        etiqueta_ejemplos = ttk.Label(marco_campos, 
                                     text="Ejemplos: /home/miusuario 192.168.1.0/24", 
                                     font=('Arial', 9))
        etiqueta_ejemplos.grid(row=2, column=0, columnspan=2, sticky='w', pady=5)
        
        marco_campos.columnconfigure(1, weight=1)
    
    def _crear_opciones_nfs(self, padre):
        """Crea los checkboxes para las opciones NFS"""
        marco_opciones = ttk.LabelFrame(padre, text="Opciones NFS")
        marco_opciones.pack(fill='x', padx=10, pady=10)
        
        opciones_validas = self.gestor_nfs.obtener_opciones_validas()
        opciones_ordenadas = sorted(opciones_validas)
        
        # Crear checkboxes en 3 columnas
        self.variables_opciones = {}
        fila, columna = 0, 0
        max_columnas = 3
        
        for opcion in opciones_ordenadas:
            variable = tk.BooleanVar()
            self.variables_opciones[opcion] = variable
            
            casilla_verificacion = ttk.Checkbutton(
                marco_opciones,
                text=opcion,
                variable=variable
            )
            casilla_verificacion.grid(row=fila, column=columna, sticky='w', padx=5, pady=2)
            
            columna += 1
            if columna >= max_columnas:
                columna = 0
                fila += 1
        
        # Ajustar columnas
        for i in range(max_columnas):
            marco_opciones.columnconfigure(i, weight=1)
    
    def _cargar_configuraciones(self):
        """Carga y muestra las configuraciones actuales"""
        self.configuraciones = self.gestor_nfs.leer_configuracion_actual()
        
        # Actualizar área de texto
        self.texto_configuraciones.delete(1.0, tk.END)
        
        if not self.configuraciones:
            self.texto_configuraciones.insert(tk.END, "No hay configuraciones NFS definidas.")
        else:
            for i, configuracion in enumerate(self.configuraciones):
                self.texto_configuraciones.insert(tk.END, f"{i+1}. {configuracion['linea_original']}\n")
        
        # Actualizar lista en pestaña de gestión
        self._actualizar_lista_configuraciones()
        
        self._actualizar_barra_estado(f"Configuraciones cargadas: {len(self.configuraciones)}")
    
    def _actualizar_lista_configuraciones(self):
        """Actualiza la lista de configuraciones en la pestaña de gestión"""
        self.lista_configuraciones.delete(0, tk.END)
        
        for i, configuracion in enumerate(self.configuraciones):
            texto_item = f"{i+1}. {configuracion['carpeta']} -> {configuracion['host']}"
            self.lista_configuraciones.insert(tk.END, texto_item)
    
    def _agregar_configuracion(self):
        """Maneja el evento de agregar nueva configuración"""
        carpeta = self.entrada_carpeta.get().strip()
        host = self.entrada_host.get().strip()
        
        if not carpeta or not host:
            messagebox.showerror("Error", "Debe especificar carpeta y host")
            return
        
        # Obtener opciones seleccionadas
        opciones = [opcion for opcion, variable in self.variables_opciones.items() if variable.get()]
        
        if not opciones:
            messagebox.showwarning("Advertencia", "No se seleccionaron opciones. Se usarán opciones por defecto.")
            opciones = ['ro', 'sync']  # Opciones por defecto
        
        # Agregar configuración
        if self.gestor_nfs.agregar_configuracion(carpeta, host, opciones):
            messagebox.showinfo("Éxito", "Configuración agregada correctamente")
            self._limpiar_campos()
            self._cargar_configuraciones()
        else:
            messagebox.showerror("Error", "No se pudo agregar la configuración")
    
    def _eliminar_configuracion(self):
        """Maneja el evento de eliminar configuración"""
        seleccion = self.lista_configuraciones.curselection()
        
        if not seleccion:
            messagebox.showwarning("Advertencia", "Seleccione una configuración para eliminar")
            return
        
        indice = seleccion[0]
        
        confirmacion = messagebox.askyesno(
            "Confirmar Eliminación",
            f"¿Está seguro de eliminar la configuración seleccionada?\n\n{self.configuraciones[indice]['linea_original']}"
        )
        
        if confirmacion:
            if self.gestor_nfs.eliminar_configuracion(indice):
                messagebox.showinfo("Éxito", "Configuración eliminada correctamente")
                self._cargar_configuraciones()
            else:
                messagebox.showerror("Error", "No se pudo eliminar la configuración")
    
    def _aplicar_cambios_nfs(self):
        """Aplica los cambios reiniciando el servicio NFS"""
        confirmacion = messagebox.askyesno(
            "Aplicar Cambios",
            "¿Está seguro de aplicar los cambios al servicio NFS?\nEsto reiniciará el servicio."
        )
        
        if confirmacion:
            if self.gestor_nfs.aplicar_cambios_nfs():
                messagebox.showinfo("Éxito", "Cambios aplicados correctamente al servicio NFS")
            else:
                messagebox.showerror("Error", "No se pudieron aplicar los cambios al servicio NFS")
    
    def _limpiar_campos(self):
        """Limpia todos los campos de entrada"""
        self.entrada_carpeta.delete(0, tk.END)
        self.entrada_host.delete(0, tk.END)
        
        for variable in self.variables_opciones.values():
            variable.set(False)
    
    def _actualizar_barra_estado(self, mensaje):
        """Actualiza el texto de la barra de estado"""
        self.barra_estado.config(text=mensaje)
