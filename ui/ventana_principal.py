# ui/ventana_principal.py
# Interfaz gráfica mejorada compatible con Python 3.6

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext, filedialog
import os
import subprocess

class VentanaPrincipal(object):
    def __init__(self, raiz, gestor_nfs):
        self.raiz = raiz
        self.gestor_nfs = gestor_nfs
        self.configuraciones = []
        self.variables_opciones = {}
        self.valores_opciones = {}
        
        # Colores del tema
        self.COLOR_PRIMARIO = "#2c5282"  # Azul oscuro
        self.COLOR_SECUNDARIO = "#4299e1"  # Azul claro
        self.COLOR_EXITO = "#48bb78"  # Verde
        self.COLOR_ADVERTENCIA = "#ed8936"  # Naranja
        self.COLOR_FONDO = "#f7fafc"  # Gris muy claro
        self.COLOR_FONDO_OSCURO = "#edf2f7"  # Gris claro
        
        self._configurar_estilos()
        self._inicializar_interfaz()
        self._cargar_configuraciones()

    def _configurar_estilos(self):
        """Configura los estilos personalizados de ttk"""
        style = ttk.Style()
        
        # Estilo para el Notebook (pestañas)
        style.configure("TNotebook", background=self.COLOR_FONDO)
        style.configure("TNotebook.Tab", padding=[20, 10], font=("Arial", 10, "bold"))
        
        # Estilo para frames
        style.configure("TFrame", background=self.COLOR_FONDO)
        style.configure("Card.TFrame", background="white", relief="solid", borderwidth=1)
        
        # Estilo para labels
        style.configure("TLabel", background=self.COLOR_FONDO, font=("Arial", 10))
        style.configure("Title.TLabel", font=("Arial", 14, "bold"), foreground=self.COLOR_PRIMARIO)
        style.configure("Subtitle.TLabel", font=("Arial", 11, "bold"), foreground=self.COLOR_SECUNDARIO)
        
        # Estilo para botones
        style.configure("Primary.TButton", font=("Arial", 10, "bold"))
        style.configure("Success.TButton", font=("Arial", 10, "bold"))
        style.configure("Warning.TButton", font=("Arial", 10, "bold"))

    def _inicializar_interfaz(self):
        self.raiz.title("Configurador NFS - OpenSUSE 15.6")
        self.raiz.configure(bg=self.COLOR_FONDO)
        
        # Frame principal con padding
        frame_principal = ttk.Frame(self.raiz, style="TFrame")
        frame_principal.pack(fill='both', expand=True, padx=15, pady=15)
        
        # Título principal
        titulo = ttk.Label(
            frame_principal, 
            text="🖥️ Configurador de Servidor NFS",
            style="Title.TLabel"
        )
        titulo.pack(pady=(0, 10))
        
        # Notebook (pestañas)
        self.cuaderno = ttk.Notebook(frame_principal)
        self.cuaderno.pack(fill='both', expand=True)

        self._crear_pestana_ver_configuraciones()
        self._crear_pestana_agregar_configuracion()
        self._crear_pestana_gestion_configuraciones()

        # Barra de estado mejorada
        self.barra_estado = tk.Label(
            self.raiz,
            text="✓ Listo",
            relief=tk.SUNKEN,
            anchor=tk.W,
            bg=self.COLOR_EXITO,
            fg="white",
            font=("Arial", 9),
            padx=10,
            pady=5
        )
        self.barra_estado.pack(side=tk.BOTTOM, fill=tk.X)

    def _crear_pestana_ver_configuraciones(self):
        marco = ttk.Frame(self.cuaderno, style="TFrame")
        self.cuaderno.add(marco, text="📋 Ver Configuraciones")

        # Card container
        card = ttk.Frame(marco, style="Card.TFrame")
        card.pack(fill='both', expand=True, padx=10, pady=10)

        etiqueta = ttk.Label(
            card,
            text="Configuraciones NFS Actuales",
            style="Subtitle.TLabel"
        )
        etiqueta.pack(pady=10)

        # Área de texto con colores personalizados
        self.texto_configuraciones = scrolledtext.ScrolledText(
            card,
            width=80,
            height=18,
            wrap=tk.WORD,
            font=("Courier New", 10),
            bg="white",
            fg="#2d3748",
            relief="solid",
            borderwidth=1
        )
        self.texto_configuraciones.pack(fill='both', expand=True, padx=15, pady=(0, 15))

        # Frame de botones
        marco_bot = ttk.Frame(card, style="TFrame")
        marco_bot.pack(pady=10)
        
        btn_actualizar = ttk.Button(
            marco_bot,
            text="🔄 Actualizar Vista",
            command=self._cargar_configuraciones,
            style="Primary.TButton"
        )
        btn_actualizar.pack(side=tk.LEFT, padx=5)
        
        btn_aplicar = ttk.Button(
            marco_bot,
            text="✓ Aplicar Cambios NFS",
            command=self._aplicar_cambios_nfs,
            style="Success.TButton"
        )
        btn_aplicar.pack(side=tk.LEFT, padx=5)

    def _crear_pestana_agregar_configuracion(self):
        marco = ttk.Frame(self.cuaderno, style="TFrame")
        self.cuaderno.add(marco, text="➕ Agregar Configuración")

        # Card principal
        card = ttk.Frame(marco, style="Card.TFrame")
        card.pack(fill='both', expand=True, padx=10, pady=10)

        # Título
        titulo = ttk.Label(card, text="Nueva Configuración NFS", style="Subtitle.TLabel")
        titulo.pack(pady=10)

        # Frame para campos de entrada
        marco_campos = ttk.Frame(card, style="TFrame")
        marco_campos.pack(fill='x', padx=20, pady=10)

        # Campo carpeta con explorador
        ttk.Label(
            marco_campos,
            text="📁 Carpeta o archivo a exportar:",
            font=("Arial", 10, "bold")
        ).grid(row=0, column=0, sticky='w', pady=5)
        
        frame_carpeta = ttk.Frame(marco_campos)
        frame_carpeta.grid(row=1, column=0, sticky='ew', pady=(0, 10))
        
        self.entrada_carpeta = ttk.Entry(frame_carpeta, width=50, font=("Arial", 10))
        self.entrada_carpeta.pack(side=tk.LEFT, fill='x', expand=True, padx=(0, 5))
        
        btn_explorar = ttk.Button(
            frame_carpeta,
            text="📂 Explorar",
            command=self._explorar_carpeta,
            width=12
        )
        btn_explorar.pack(side=tk.LEFT)
        
        # Label de validación de ruta
        self.label_validacion_ruta = ttk.Label(
            marco_campos,
            text="",
            foreground=self.COLOR_ADVERTENCIA
        )
        self.label_validacion_ruta.grid(row=2, column=0, sticky='w')
        
        # Vincular validación al cambio de texto
        self.entrada_carpeta.bind('<KeyRelease>', self._validar_ruta_tiempo_real)

        # Campo hosts/red con validación
        ttk.Label(
            marco_campos,
            text="🌐 Hosts o red (IP/CIDR):",
            font=("Arial", 10, "bold")
        ).grid(row=3, column=0, sticky='w', pady=(15, 5))
        
        self.entrada_hosts = ttk.Entry(marco_campos, width=50, font=("Arial", 10))
        self.entrada_hosts.grid(row=4, column=0, sticky='ew', pady=(0, 5))
        
        # Label de validación de red
        self.label_validacion_red = ttk.Label(
            marco_campos,
            text="",
            foreground=self.COLOR_ADVERTENCIA
        )
        self.label_validacion_red.grid(row=5, column=0, sticky='w')
        
        # Vincular validación
        self.entrada_hosts.bind('<KeyRelease>', self._validar_red_tiempo_real)
        
        # Ejemplos
        ttk.Label(
            marco_campos,
            text="💡 Ejemplos: 192.168.1.100 | 192.168.1.0/24 | 10.0.0.0/8 | *",
            font=("Arial", 9, "italic"),
            foreground="#718096"
        ).grid(row=6, column=0, sticky='w', pady=(0, 10))

        marco_campos.columnconfigure(0, weight=1)

        # Opciones NFS con tooltips
        self._crear_seccion_opciones(card)

        # Botones de acción
        marco_bot = ttk.Frame(card, style="TFrame")
        marco_bot.pack(pady=15)
        
        btn_agregar = ttk.Button(
            marco_bot,
            text="✓ Agregar Configuración",
            command=self._agregar_configuracion,
            style="Success.TButton"
        )
        btn_agregar.pack(side=tk.LEFT, padx=5)
        
        btn_limpiar = ttk.Button(
            marco_bot,
            text="🗑️ Limpiar Campos",
            command=self._limpiar_campos,
            style="Warning.TButton"
        )
        btn_limpiar.pack(side=tk.LEFT, padx=5)

    def _crear_seccion_opciones(self, parent):
        """Crea la sección de opciones NFS con descripciones"""
        marco_opts = ttk.LabelFrame(
            parent,
            text="⚙️ Opciones NFS",
            padding=15
        )
        marco_opts.pack(fill='both', expand=True, padx=20, pady=10)

        # Obtener opciones con descripciones
        opciones_info = self.gestor_nfs.obtener_opciones_con_descripciones()
        opciones = sorted(opciones_info.keys())

        # Configuración recomendada
        recomendacion = ttk.Label(
            marco_opts,
            text="💡 Configuración recomendada: rw, sync, no_subtree_check",
            font=("Arial", 9, "italic"),
            foreground=self.COLOR_SECUNDARIO
        )
        recomendacion.grid(row=0, column=0, columnspan=4, sticky='w', pady=(0, 10))

        fila = 1
        col = 0
        max_cols = 2

        for opt in opciones:
            descripcion = opciones_info[opt]
            
            if opt in ('anonuid', 'anongid'):
                # Checkbox + Entry para opciones con valor
                var = tk.BooleanVar()
                self.variables_opciones[opt] = var
                
                frame_opt = ttk.Frame(marco_opts)
                frame_opt.grid(row=fila, column=col, sticky='ew', padx=5, pady=3, columnspan=2)
                
                chk = ttk.Checkbutton(
                    frame_opt,
                    text=opt,
                    variable=var,
                    command=lambda o=opt: self._toggle_valor(o)
                )
                chk.pack(side=tk.LEFT)
                
                entrada = ttk.Entry(frame_opt, width=10)
                entrada.pack(side=tk.LEFT, padx=5)
                entrada.configure(state='disabled')
                self.valores_opciones[opt] = entrada
                
                # Tooltip
                self._crear_tooltip(frame_opt, descripcion)
                
                fila += 1
                col = 0
            else:
                # Checkbox simple
                var = tk.BooleanVar()
                self.variables_opciones[opt] = var
                
                frame_opt = ttk.Frame(marco_opts)
                frame_opt.grid(row=fila, column=col, sticky='w', padx=5, pady=3)
                
                chk = ttk.Checkbutton(frame_opt, text=opt, variable=var)
                chk.pack(side=tk.LEFT)
                
                # Tooltip
                self._crear_tooltip(frame_opt, descripcion)
                
                col += 1
                if col >= max_cols:
                    fila += 1
                    col = 0

    def _crear_tooltip(self, widget, texto):
        """Crea un tooltip simple para el widget"""
        def mostrar_tooltip(event):
            x, y, _, _ = widget.bbox("insert")
            x += widget.winfo_rootx() + 25
            y += widget.winfo_rooty() + 25
            
            self.tooltip_window = tk.Toplevel(widget)
            self.tooltip_window.wm_overrideredirect(True)
            self.tooltip_window.wm_geometry("+{0}+{1}".format(x, y))
            
            label = tk.Label(
                self.tooltip_window,
                text=texto,
                background="#2d3748",
                foreground="white",
                relief="solid",
                borderwidth=1,
                font=("Arial", 9),
                padx=10,
                pady=5,
                wraplength=300
            )
            label.pack()
        
        def ocultar_tooltip(event):
            if hasattr(self, 'tooltip_window'):
                self.tooltip_window.destroy()
        
        widget.bind('<Enter>', mostrar_tooltip)
        widget.bind('<Leave>', ocultar_tooltip)

    def _explorar_carpeta(self):
        """Abre el explorador de archivos para seleccionar carpeta o archivo"""
        # Primero preguntar si es carpeta o archivo
        tipo = messagebox.askquestion(
            "Seleccionar tipo",
            "¿Desea exportar una CARPETA?\n\n(Seleccione 'No' para exportar un archivo individual)",
            icon='question'
        )
        
        if tipo == 'yes':
            # Seleccionar carpeta
            ruta = filedialog.askdirectory(
                title="Seleccione la carpeta a exportar",
                initialdir="/home"
            )
        else:
            # Seleccionar archivo
            ruta = filedialog.askopenfilename(
                title="Seleccione el archivo a exportar",
                initialdir="/home"
            )
        
        if ruta:
            self.entrada_carpeta.delete(0, tk.END)
            self.entrada_carpeta.insert(0, ruta)
            self._validar_ruta_tiempo_real()

    def _validar_ruta_tiempo_real(self, event=None):
        """Valida la ruta en tiempo real mientras el usuario escribe"""
        ruta = self.entrada_carpeta.get().strip()
        
        if not ruta:
            self.label_validacion_ruta.config(text="", foreground=self.COLOR_ADVERTENCIA)
            return
        
        es_valida, tipo, mensaje = self.gestor_nfs.validar_ruta(ruta)
        
        if es_valida:
            if tipo == 'directorio':
                self.label_validacion_ruta.config(
                    text="✓ Directorio válido y accesible",
                    foreground=self.COLOR_EXITO
                )
            elif tipo == 'archivo':
                self.label_validacion_ruta.config(
                    text="✓ Archivo válido y accesible",
                    foreground=self.COLOR_EXITO
                )
        else:
            self.label_validacion_ruta.config(
                text="✗ {0}".format(mensaje),
                foreground=self.COLOR_ADVERTENCIA
            )

    def _validar_red_tiempo_real(self, event=None):
        """Valida la red/hosts en tiempo real"""
        hosts = self.entrada_hosts.get().strip()
        
        if not hosts:
            self.label_validacion_red.config(text="", foreground=self.COLOR_ADVERTENCIA)
            return
        
        es_valida, mensaje = self.gestor_nfs.validar_red(hosts)
        
        if es_valida:
            self.label_validacion_red.config(
                text="✓ {0}".format(mensaje),
                foreground=self.COLOR_EXITO
            )
        else:
            self.label_validacion_red.config(
                text="✗ {0}".format(mensaje),
                foreground=self.COLOR_ADVERTENCIA
            )

    def _toggle_valor(self, opcion):
        """Habilita/deshabilita el entry para anonuid/anongid"""
        entry = self.valores_opciones.get(opcion)
        var = self.variables_opciones.get(opcion)
        
        if entry is None or var is None:
            return
        
        if var.get():
            entry.configure(state='normal')
            entry.focus()
        else:
            entry.delete(0, tk.END)
            entry.configure(state='disabled')

    def _crear_pestana_gestion_configuraciones(self):
        marco = ttk.Frame(self.cuaderno, style="TFrame")
        self.cuaderno.add(marco, text="🗂️ Gestionar Configuraciones")

        # Card
        card = ttk.Frame(marco, style="Card.TFrame")
        card.pack(fill='both', expand=True, padx=10, pady=10)

        titulo = ttk.Label(
            card,
            text="Configuraciones Existentes",
            style="Subtitle.TLabel"
        )
        titulo.pack(pady=10)

        # Frame lista
        marco_lista = ttk.Frame(card, style="TFrame")
        marco_lista.pack(fill='both', expand=True, padx=15, pady=5)
        
        self.lista_configuraciones = tk.Listbox(
            marco_lista,
            height=15,
            font=("Courier New", 10),
            bg="white",
            fg="#2d3748",
            selectbackground=self.COLOR_SECUNDARIO,
            selectforeground="white",
            relief="solid",
            borderwidth=1
        )
        
        barra = ttk.Scrollbar(marco_lista, orient='vertical', command=self.lista_configuraciones.yview)
        self.lista_configuraciones.configure(yscrollcommand=barra.set)
        self.lista_configuraciones.pack(side=tk.LEFT, fill='both', expand=True)
        barra.pack(side=tk.RIGHT, fill='y')

        # Botones
        marco_bot = ttk.Frame(card, style="TFrame")
        marco_bot.pack(pady=15)
        
        ttk.Button(
            marco_bot,
            text="🗑️ Eliminar Seleccionada",
            command=self._eliminar_configuracion,
            style="Warning.TButton"
        ).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(
            marco_bot,
            text="🔄 Actualizar Lista",
            command=self._actualizar_lista_configuraciones,
            style="Primary.TButton"
        ).pack(side=tk.LEFT, padx=5)

    def _cargar_configuraciones(self):
        self.configuraciones = self.gestor_nfs.leer_configuracion_actual()
        self.texto_configuraciones.delete(1.0, tk.END)
        
        if not self.configuraciones:
            self.texto_configuraciones.insert(
                tk.END,
                "ℹ️ No hay configuraciones NFS definidas.\n\n"
                "Para agregar una nueva configuración, use la pestaña 'Agregar Configuración'."
            )
            self.texto_configuraciones.tag_add("info", "1.0", "3.0")
            self.texto_configuraciones.tag_config("info", foreground=self.COLOR_SECUNDARIO)
        else:
            for i, c in enumerate(self.configuraciones):
                linea = "{0}. {1}\n".format(i+1, c['linea_original'])
                self.texto_configuraciones.insert(tk.END, linea)
        
        self._actualizar_lista_configuraciones()
        self._actualizar_barra_estado(
            "✓ Configuraciones cargadas: {0}".format(len(self.configuraciones)),
            tipo="exito"
        )

    def _actualizar_lista_configuraciones(self):
        self.lista_configuraciones.delete(0, tk.END)
        for i, c in enumerate(self.configuraciones):
            texto = "{0}. {1} → {2} ({3})".format(
                i+1, c['carpeta'], c['hosts'], ', '.join(c['opciones'])
            )
            self.lista_configuraciones.insert(tk.END, texto)

    def _agregar_configuracion(self):
        carpeta = self.entrada_carpeta.get().strip()
        hosts = self.entrada_hosts.get().strip()
        
        # Validar ruta
        if not carpeta:
            messagebox.showerror("Error", "Debe seleccionar una carpeta o archivo")
            return
        
        es_valida, tipo, mensaje = self.gestor_nfs.validar_ruta(carpeta)
        if not es_valida:
            messagebox.showerror("Error de Ruta", mensaje)
            return
        
        # Validar hosts
        if not hosts:
            messagebox.showerror("Error", "Debe especificar hosts o red")
            return
        
        es_valida_red, mensaje_red = self.gestor_nfs.validar_red(hosts)
        if not es_valida_red:
            messagebox.showerror("Error de Red/Hosts", mensaje_red)
            return

        # Recopilar opciones seleccionadas
        opciones = []
        for opt, var in self.variables_opciones.items():
            if isinstance(var, tk.BooleanVar) and var.get():
                if opt in self.valores_opciones:
                    entry = self.valores_opciones[opt]
                    valor = entry.get().strip()
                    
                    if not valor:
                        messagebox.showerror(
                            "Error",
                            "La opción {0} requiere un valor numérico".format(opt)
                        )
                        return
                    
                    # Validar que sea numérico
                    try:
                        int(valor)
                        opciones.append("{0}={1}".format(opt, valor))
                    except ValueError:
                        messagebox.showerror(
                            "Error",
                            "El valor de {0} debe ser numérico".format(opt)
                        )
                        return
                else:
                    opciones.append(opt)

        # Si no se seleccionaron opciones, usar valores por defecto seguros
        if not opciones:
            respuesta = messagebox.askyesno(
                "Opciones por defecto",
                "No seleccionó ninguna opción.\n\n"
                "¿Desea usar la configuración recomendada?\n"
                "(rw, sync, no_subtree_check)"
            )
            if respuesta:
                opciones = ['rw', 'sync', 'no_subtree_check']
            else:
                return

        # NUEVO: Verificar permisos del sistema de archivos
        permisos_ok, mensaje_permisos = self.gestor_nfs.verificar_y_ajustar_permisos(carpeta, opciones)
        
        ajustar_permisos = False
        if not permisos_ok:
            # Preguntar al usuario si desea ajustar permisos
            respuesta = messagebox.askyesnocancel(
                "⚠️ Verificación de Permisos",
                mensaje_permisos + "\n\n" +
                "Seleccione:\n" +
                "• SÍ: Ajustar permisos automáticamente (recomendado)\n" +
                "• NO: Continuar sin ajustar (puede causar 'Permission Denied')\n" +
                "• CANCELAR: Abortar operación"
            )
            
            if respuesta is None:  # Cancelar
                return
            elif respuesta:  # Sí
                ajustar_permisos = True
            # Si respuesta es False (No), continuamos sin ajustar

        # Agregar configuración
        ok = self.gestor_nfs.agregar_configuracion(carpeta, hosts, opciones, ajustar_permisos)
        
        if ok:
            msg_exito = "✓ Configuración agregada correctamente\n\n"
            if ajustar_permisos:
                msg_exito += "✓ Permisos del sistema de archivos ajustados\n\n"
            msg_exito += "⚠️ IMPORTANTE: Debe aplicar los cambios en la pestaña 'Ver Configuraciones'"
            
            messagebox.showinfo("Éxito", msg_exito)
            self._limpiar_campos()
            self._cargar_configuraciones()
        else:
            messagebox.showerror(
                "Error",
                "No se pudo agregar la configuración.\n"
                "Verifique los permisos y los logs del sistema."
            )

    def _eliminar_configuracion(self):
        sel = self.lista_configuraciones.curselection()
        if not sel:
            messagebox.showwarning("Advertencia", "Seleccione una configuración de la lista")
            return
        
        idx = sel[0]
        linea = self.configuraciones[idx]['linea_original']
        
        confirma = messagebox.askyesno(
            "Confirmar eliminación",
            "¿Está seguro de eliminar esta configuración?\n\n{0}".format(linea)
        )
        
        if not confirma:
            return
        
        ok = self.gestor_nfs.eliminar_configuracion(idx)
        
        if ok:
            messagebox.showinfo("Éxito", "✓ Configuración eliminada correctamente")
            self._cargar_configuraciones()
        else:
            messagebox.showerror("Error", "No se pudo eliminar la configuración")

    def _aplicar_cambios_nfs(self):
        # Primero verificar el estado del servicio NFS
        servicio_activo, mensaje_servicio = self.gestor_nfs.verificar_servicio_nfs()
        
        if not servicio_activo:
            respuesta = messagebox.askyesno(
                "⚠️ Servicio NFS Inactivo",
                mensaje_servicio + "\n\n" +
                "¿Desea intentar iniciar el servicio automáticamente?\n\n" +
                "(Requiere permisos de root)"
            )
            
            if respuesta:
                try:
                    subprocess.run(
                        ["systemctl", "start", "nfs-server"],
                        check=True,
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE
                    )
                    messagebox.showinfo(
                        "Éxito",
                        "✓ Servicio NFS iniciado correctamente"
                    )
                except Exception as e:
                    messagebox.showerror(
                        "Error",
                        "No se pudo iniciar el servicio NFS.\n" +
                        "Ejecute manualmente: sudo systemctl start nfs-server"
                    )
                    return
            else:
                return
        
        confirma = messagebox.askyesno(
            "Aplicar cambios",
            "Esto ejecutará 'exportfs -ra' para aplicar los cambios.\n\n"
            "¿Desea continuar?"
        )
        
        if not confirma:
            return
        
        ok = self.gestor_nfs.aplicar_cambios_nfs()
        
        if ok:
            messagebox.showinfo(
                "Éxito",
                "✓ Cambios aplicados correctamente\n\n" +
                "El servidor NFS ha sido actualizado.\n" +
                "Los clientes pueden ahora acceder a los recursos compartidos."
            )
            self._actualizar_barra_estado("✓ Cambios NFS aplicados correctamente", tipo="exito")
        else:
            messagebox.showerror(
                "Error",
                "No se pudieron aplicar los cambios.\n\n" +
                "Posibles causas:\n" +
                "• No tiene permisos de root\n" +
                "• El servicio NFS no está instalado\n" +
                "• Hay errores de sintaxis en /etc/exports\n\n" +
                "Ejecute: sudo exportfs -ra"
            )
            self._actualizar_barra_estado("✗ Error al aplicar cambios NFS", tipo="error")

    def _limpiar_campos(self):
        self.entrada_carpeta.delete(0, tk.END)
        self.entrada_hosts.delete(0, tk.END)
        self.label_validacion_ruta.config(text="")
        self.label_validacion_red.config(text="")
        
        for var in self.variables_opciones.values():
            var.set(False)
        
        for entry in self.valores_opciones.values():
            entry.delete(0, tk.END)
            entry.configure(state='disabled')

    def _actualizar_barra_estado(self, texto, tipo="info"):
        """Actualiza la barra de estado con colores según el tipo"""
        colores = {
            "exito": self.COLOR_EXITO,
            "advertencia": self.COLOR_ADVERTENCIA,
            "error": "#e53e3e",
            "info": self.COLOR_SECUNDARIO
        }
        
        self.barra_estado.config(
            text=texto,
            bg=colores.get(tipo, self.COLOR_SECUNDARIO)
        )