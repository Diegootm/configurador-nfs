# ui/ventana_principal.py
# Interfaz gráfica compatible con Python 3.6

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
from tkinter import simpledialog

class VentanaPrincipal(object):
    def __init__(self, raiz, gestor_nfs):
        self.raiz = raiz
        self.gestor_nfs = gestor_nfs
        self.configuraciones = []
        # opciones simples (checkbox booleans)
        self.variables_opciones = {}
        # valores para opciones con argumento (anonuid, anongid)
        self.valores_opciones = {}

        self._inicializar_interfaz()
        self._cargar_configuraciones()

    def _inicializar_interfaz(self):
        self.raiz.title("Configurador NFS (compatible Python 3.6)")
        self.cuaderno = ttk.Notebook(self.raiz)
        self.cuaderno.pack(fill='both', expand=True, padx=10, pady=10)

        self._crear_pestana_ver_configuraciones()
        self._crear_pestana_agregar_configuracion()
        self._crear_pestana_gestion_configuraciones()

        self.barra_estado = ttk.Label(self.raiz, text="Listo", relief=tk.SUNKEN, anchor=tk.W)
        self.barra_estado.pack(side=tk.BOTTOM, fill=tk.X)

    def _crear_pestana_ver_configuraciones(self):
        marco = ttk.Frame(self.cuaderno)
        self.cuaderno.add(marco, text="Ver Configuraciones")

        etiqueta = ttk.Label(marco, text="Configuraciones NFS actuales:", font=("Arial", 12, "bold"))
        etiqueta.pack(pady=5)

        self.texto_configuraciones = scrolledtext.ScrolledText(marco, width=80, height=20, wrap=tk.WORD)
        self.texto_configuraciones.pack(fill='both', expand=True, padx=10, pady=5)

        marco_bot = ttk.Frame(marco)
        marco_bot.pack(pady=10)
        btn_actualizar = ttk.Button(marco_bot, text="Actualizar Vista", command=self._cargar_configuraciones)
        btn_actualizar.pack(side=tk.LEFT, padx=5)
        btn_aplicar = ttk.Button(marco_bot, text="Aplicar Cambios NFS", command=self._aplicar_cambios_nfs)
        btn_aplicar.pack(side=tk.LEFT, padx=5)

    def _crear_pestana_agregar_configuracion(self):
        marco = ttk.Frame(self.cuaderno)
        self.cuaderno.add(marco, text="Agregar Configuración")

        # campos carpeta y hosts
        marco_campos = ttk.Frame(marco)
        marco_campos.pack(fill='x', padx=10, pady=10)
        ttk.Label(marco_campos, text="Carpeta a exportar:").grid(row=0, column=0, sticky='w')
        self.entrada_carpeta = ttk.Entry(marco_campos, width=60)
        self.entrada_carpeta.grid(row=0, column=1, sticky='ew', padx=5, pady=2)
        ttk.Label(marco_campos, text="Hosts o red (ej: 192.168.1.0/24 o 10.0.0.0/24):").grid(row=1, column=0, sticky='w')
        self.entrada_hosts = ttk.Entry(marco_campos, width=60)
        self.entrada_hosts.grid(row=1, column=1, sticky='ew', padx=5, pady=2)
        marco_campos.columnconfigure(1, weight=1)

        ttk.Label(marco_campos, text="Ejemplo: /home/miusuario 192.168.1.0/24").grid(row=2, column=0, columnspan=2, sticky='w', pady=5)

        # opciones NFS
        marco_opts = ttk.LabelFrame(marco, text="Opciones NFS")
        marco_opts.pack(fill='x', padx=10, pady=10)

        opciones = self.gestor_nfs.obtener_opciones_validas()
        # ordenamos, y tratar anonuid/anongid aparte para pedir valor
        opciones = sorted(opciones)

        fila = 0
        col = 0
        max_cols = 3

        for opt in opciones:
            if opt in ('anonuid', 'anongid'):
                # checkbutton + entry para valor
                var = tk.BooleanVar()
                self.variables_opciones[opt] = var
                chk = ttk.Checkbutton(marco_opts, text=opt, variable=var, command=lambda o=opt: self._toggle_valor(o))
                chk.grid(row=fila, column=col, sticky='w', padx=5, pady=2)
                # entry (disabled por defecto)
                entrada = ttk.Entry(marco_opts, width=8)
                entrada.grid(row=fila, column=col+1, sticky='w', padx=2)
                entrada.configure(state='disabled')
                self.valores_opciones[opt] = entrada

                col += 2
            else:
                var = tk.BooleanVar()
                self.variables_opciones[opt] = var
                chk = ttk.Checkbutton(marco_opts, text=opt, variable=var)
                chk.grid(row=fila, column=col, sticky='w', padx=5, pady=2)
                col += 1

            if col >= max_cols:
                fila += 1
                col = 0

        # botones
        marco_bot = ttk.Frame(marco)
        marco_bot.pack(pady=10)
        btn_agregar = ttk.Button(marco_bot, text="Agregar Configuración", command=self._agregar_configuracion)
        btn_agregar.pack(side=tk.LEFT, padx=5)
        btn_limpiar = ttk.Button(marco_bot, text="Limpiar Campos", command=self._limpiar_campos)
        btn_limpiar.pack(side=tk.LEFT, padx=5)

    def _toggle_valor(self, opcion):
        """
        Habilita o deshabilita el entry asociado a anonuid/anongid
        """
        entry = self.valores_opciones.get(opcion)
        var = self.variables_opciones.get(opcion)
        if entry is None or var is None:
            return
        if var.get():
            entry.configure(state='normal')
        else:
            entry.delete(0, tk.END)
            entry.configure(state='disabled')

    def _crear_pestana_gestion_configuraciones(self):
        marco = ttk.Frame(self.cuaderno)
        self.cuaderno.add(marco, text="Gestionar Configuraciones")

        ttk.Label(marco, text="Configuraciones existentes:", font=("Arial", 12, "bold")).pack(pady=5)
        marco_lista = ttk.Frame(marco)
        marco_lista.pack(fill='both', expand=True, padx=10, pady=5)
        self.lista_configuraciones = tk.Listbox(marco_lista, height=15)
        barra = ttk.Scrollbar(marco_lista, orient='vertical', command=self.lista_configuraciones.yview)
        self.lista_configuraciones.configure(yscrollcommand=barra.set)
        self.lista_configuraciones.pack(side=tk.LEFT, fill='both', expand=True)
        barra.pack(side=tk.RIGHT, fill='y')

        marco_bot = ttk.Frame(marco)
        marco_bot.pack(pady=10)
        ttk.Button(marco_bot, text="Eliminar Seleccionada", command=self._eliminar_configuracion).pack(side=tk.LEFT, padx=5)
        ttk.Button(marco_bot, text="Actualizar Lista", command=self._actualizar_lista_configuraciones).pack(side=tk.LEFT, padx=5)

    def _cargar_configuraciones(self):
        self.configuraciones = self.gestor_nfs.leer_configuracion_actual()
        self.texto_configuraciones.delete(1.0, tk.END)
        if not self.configuraciones:
            self.texto_configuraciones.insert(tk.END, "No hay configuraciones NFS definidas.\n")
        else:
            for i, c in enumerate(self.configuraciones):
                linea = "{0}. {1}".format(i+1, c['linea_original'])
                self.texto_configuraciones.insert(tk.END, linea + "\n")
        self._actualizar_lista_configuraciones()
        self._actualizar_barra_estado("Configuraciones cargadas: {0}".format(len(self.configuraciones)))

    def _actualizar_lista_configuraciones(self):
        self.lista_configuraciones.delete(0, tk.END)
        for i, c in enumerate(self.configuraciones):
            texto = "{0}. {1} -> {2}".format(i+1, c['carpeta'], c['hosts'])
            self.lista_configuraciones.insert(tk.END, texto)

    def _agregar_configuracion(self):
        carpeta = self.entrada_carpeta.get().strip()
        hosts = self.entrada_hosts.get().strip()
        if not carpeta or not hosts:
            messagebox.showerror("Error", "Debe indicar carpeta y hosts/red")
            return

        opciones = []
        for opt, var in self.variables_opciones.items():
            if isinstance(var, tk.BooleanVar) and var.get():
                # si es anonuid/anongid, buscar valor en entry
                if opt in self.valores_opciones:
                    entry = self.valores_opciones[opt]
                    valor = entry.get().strip()
                    if not valor:
                        # pedir valor con dialog
                        valor = simpledialog.askstring("Valor requerido", "Escriba valor para {0}:".format(opt))
                    if valor:
                        opciones.append("{0}={1}".format(opt, valor))
                    else:
                        messagebox.showerror("Error", "La opción {0} requiere un valor numérico".format(opt))
                        return
                else:
                    opciones.append(opt)

        if not opciones:
            # aplicar por defecto
            opciones = ['rw', 'sync']

        ok = self.gestor_nfs.agregar_configuracion(carpeta, hosts, opciones)
        if ok:
            messagebox.showinfo("Éxito", "Configuración agregada")
            self._limpiar_campos()
            self._cargar_configuraciones()
        else:
            messagebox.showerror("Error", "No se pudo agregar la configuración (ver consola)")

    def _eliminar_configuracion(self):
        sel = self.lista_configuraciones.curselection()
        if not sel:
            messagebox.showwarning("Advertencia", "Seleccione una configuración")
            return
        idx = sel[0]
        linea = self.configuraciones[idx]['linea_original']
        confirma = messagebox.askyesno("Confirmar", "Eliminar esta configuración?\n\n{0}".format(linea))
        if not confirma:
            return
        ok = self.gestor_nfs.eliminar_configuracion(idx)
        if ok:
            messagebox.showinfo("Éxito", "Configuración eliminada")
            self._cargar_configuraciones()
        else:
            messagebox.showerror("Error", "No se pudo eliminar (ver consola)")

    def _aplicar_cambios_nfs(self):
        confirma = messagebox.askyesno("Aplicar cambios", "Esto ejecutará 'exportfs -ra'. Continuar?")
        if not confirma:
            return
        ok = self.gestor_nfs.aplicar_cambios_nfs()
        if ok:
            messagebox.showinfo("Éxito", "Cambios aplicados correctamente")
        else:
            messagebox.showerror("Error", "No se pudieron aplicar los cambios (ver consola)")

    def _limpiar_campos(self):
        self.entrada_carpeta.delete(0, tk.END)
        self.entrada_hosts.delete(0, tk.END)
        for var in self.variables_opciones.values():
            var.set(False)
        for entry in self.valores_opciones.values():
            entry.delete(0, tk.END)
            entry.configure(state='disabled')

    def _actualizar_barra_estado(self, texto):
        self.barra_estado.config(text=texto)
