# gestor_nfs.py
# Compatible con Python 3.6.15 - Con fix de permisos

import os
import shutil
from datetime import datetime
import subprocess
import stat

class GestorNFS(object):
    """
    Clase para gestionar /etc/exports de forma simple y segura.
    Incluye gestión automática de permisos del sistema de archivos.
    """

    def __init__(self, ruta_exports="/etc/exports"):
        self.ruta_exports = ruta_exports
        self.ruta_respaldo = "{0}.respaldo".format(ruta_exports)
        
        # Opciones NFS con sus descripciones
        self.opciones_info = {
            'ro': 'Solo lectura - Los clientes pueden leer pero no modificar',
            'rw': 'Lectura/Escritura - Los clientes pueden leer y modificar archivos',
            'sync': 'Sincronización - Cambios se escriben inmediatamente al disco',
            'async': 'Asíncrono - Mejora rendimiento pero menos seguro',
            'no_root_squash': 'Root remoto tiene privilegios de root',
            'root_squash': 'Root remoto se mapea a usuario anónimo (más seguro)',
            'all_squash': 'Todos los usuarios remotos se mapean a anónimo',
            'no_subtree_check': 'Desactiva verificación de subdirectorios (más rápido)',
            'subtree_check': 'Verifica permisos en subdirectorios (más seguro)',
            'insecure': 'Permite conexiones desde puertos > 1024',
            'secure': 'Solo permite conexiones desde puertos < 1024',
            'anonuid': 'UID del usuario anónimo (ejemplo: anonuid=1000)',
            'anongid': 'GID del grupo anónimo (ejemplo: anongid=1000)'
        }
        
        self.opciones_validas = set(self.opciones_info.keys())

    def obtener_descripcion_opcion(self, opcion):
        """Retorna la descripción de una opción NFS"""
        return self.opciones_info.get(opcion, "Sin descripción disponible")

    def obtener_opciones_con_descripciones(self):
        """Retorna un diccionario con opciones y sus descripciones"""
        return self.opciones_info.copy()

    def validar_ruta(self, ruta):
        """
        Valida que la ruta existe y es accesible
        Retorna (es_valida, tipo, mensaje)
        tipo puede ser: 'directorio', 'archivo', 'no_existe', 'sin_permisos'
        """
        if not ruta:
            return (False, None, "La ruta está vacía")
        
        if not os.path.exists(ruta):
            return (False, 'no_existe', "La ruta no existe: {0}".format(ruta))
        
        if not os.access(ruta, os.R_OK):
            return (False, 'sin_permisos', "No hay permisos de lectura en: {0}".format(ruta))
        
        if os.path.isdir(ruta):
            return (True, 'directorio', "Directorio válido")
        elif os.path.isfile(ruta):
            return (True, 'archivo', "Archivo válido")
        else:
            return (False, 'desconocido', "Tipo de ruta no reconocido")

    def verificar_y_ajustar_permisos(self, ruta, opciones):
        """
        Verifica y ajusta los permisos del sistema de archivos según las opciones NFS
        Retorna (exito, mensaje)
        """
        try:
            # Verificar si la ruta existe
            if not os.path.exists(ruta):
                return (False, "La ruta no existe: {0}".format(ruta))
            
            # Obtener información actual
            stat_info = os.stat(ruta)
            permisos_actuales = stat.filemode(stat_info.st_mode)
            
            mensajes = []
            mensajes.append("Verificando permisos de: {0}".format(ruta))
            mensajes.append("Permisos actuales: {0}".format(permisos_actuales))
            
            # Determinar si necesita escritura
            necesita_escritura = 'rw' in opciones
            
            if os.path.isdir(ruta):
                # Para directorios con rw, necesitamos rwxr-xr-x (755) o mejor
                if necesita_escritura:
                    permisos_recomendados = stat.S_IRWXU | stat.S_IRGRP | stat.S_IXGRP | stat.S_IROTH | stat.S_IXOTH  # 755
                    modo_recomendado = "rwxr-xr-x (755)"
                else:
                    # Para solo lectura, r-xr-xr-x (555) es suficiente
                    permisos_recomendados = stat.S_IRUSR | stat.S_IXUSR | stat.S_IRGRP | stat.S_IXGRP | stat.S_IROTH | stat.S_IXOTH  # 555
                    modo_recomendado = "r-xr-xr-x (555)"
            else:
                # Para archivos con rw, necesitamos rw-r--r-- (644) o mejor
                if necesita_escritura:
                    permisos_recomendados = stat.S_IRUSR | stat.S_IWUSR | stat.S_IRGRP | stat.S_IROTH  # 644
                    modo_recomendado = "rw-r--r-- (644)"
                else:
                    # Para solo lectura, r--r--r-- (444)
                    permisos_recomendados = stat.S_IRUSR | stat.S_IRGRP | stat.S_IROTH  # 444
                    modo_recomendado = "r--r--r-- (444)"
            
            # Verificar si los permisos actuales son suficientes
            permisos_suficientes = (stat_info.st_mode & permisos_recomendados) == permisos_recomendados
            
            if not permisos_suficientes:
                mensajes.append("⚠️  ADVERTENCIA: Los permisos actuales pueden no ser suficientes")
                mensajes.append("    Permisos recomendados: {0}".format(modo_recomendado))
                mensajes.append("")
                mensajes.append("¿Desea ajustar los permisos automáticamente?")
                mensajes.append("(Esto cambiará los permisos del sistema de archivos)")
                
                return (False, "\n".join(mensajes))
            else:
                mensajes.append("✓ Los permisos son adecuados para la configuración NFS")
                return (True, "\n".join(mensajes))
                
        except Exception as e:
            return (False, "Error verificando permisos: {0}".format(str(e)))

    def aplicar_permisos_filesystem(self, ruta, opciones):
        """
        Aplica los permisos correctos al sistema de archivos según las opciones NFS
        Retorna (exito, mensaje)
        """
        try:
            if not os.path.exists(ruta):
                return (False, "La ruta no existe")
            
            necesita_escritura = 'rw' in opciones
            
            if os.path.isdir(ruta):
                if necesita_escritura:
                    # Directorio con escritura: 755 (rwxr-xr-x)
                    nuevo_modo = 0o755
                    os.chmod(ruta, nuevo_modo)
                    return (True, "Permisos ajustados a 755 (rwxr-xr-x) para lectura/escritura")
                else:
                    # Directorio solo lectura: 555 (r-xr-xr-x)
                    nuevo_modo = 0o555
                    os.chmod(ruta, nuevo_modo)
                    return (True, "Permisos ajustados a 555 (r-xr-xr-x) para solo lectura")
            else:
                if necesita_escritura:
                    # Archivo con escritura: 644 (rw-r--r--)
                    nuevo_modo = 0o644
                    os.chmod(ruta, nuevo_modo)
                    return (True, "Permisos ajustados a 644 (rw-r--r--) para lectura/escritura")
                else:
                    # Archivo solo lectura: 444 (r--r--r--)
                    nuevo_modo = 0o444
                    os.chmod(ruta, nuevo_modo)
                    return (True, "Permisos ajustados a 444 (r--r--r--) para solo lectura")
                    
        except PermissionError:
            return (False, "Error: Se requieren permisos de root para cambiar permisos")
        except Exception as e:
            return (False, "Error aplicando permisos: {0}".format(str(e)))

    def validar_red(self, hosts):
        """
        Valida que el formato de red/host sea correcto
        Acepta: IP, red CIDR, hostname, wildcard (*)
        """
        if not hosts or not hosts.strip():
            return (False, "El campo de hosts/red está vacío")
        
        hosts = hosts.strip()
        
        # Permitir wildcard
        if hosts == '*':
            return (True, "Permitir acceso desde cualquier host")
        
        # Validar formato CIDR (ej: 192.168.1.0/24)
        if '/' in hosts:
            partes = hosts.split('/')
            if len(partes) != 2:
                return (False, "Formato CIDR inválido. Use: 192.168.1.0/24")
            
            ip_parte = partes[0]
            try:
                mascara = int(partes[1])
                if mascara < 0 or mascara > 32:
                    return (False, "La máscara debe estar entre 0 y 32")
            except ValueError:
                return (False, "La máscara de red debe ser un número")
            
            # Validar la parte IP
            octetos = ip_parte.split('.')
            if len(octetos) != 4:
                return (False, "La dirección IP debe tener 4 octetos")
            
            for octeto in octetos:
                try:
                    num = int(octeto)
                    if num < 0 or num > 255:
                        return (False, "Cada octeto debe estar entre 0 y 255")
                except ValueError:
                    return (False, "Los octetos deben ser números")
            
            return (True, "Red CIDR válida")
        
        # Validar IP simple (ej: 192.168.1.100)
        octetos = hosts.split('.')
        if len(octetos) == 4:
            try:
                for octeto in octetos:
                    num = int(octeto)
                    if num < 0 or num > 255:
                        return (False, "Cada octeto debe estar entre 0 y 255")
                return (True, "Dirección IP válida")
            except ValueError:
                # Podría ser un hostname con puntos
                pass
        
        # Asumir que es un hostname
        if hosts.replace('-', '').replace('.', '').replace('_', '').isalnum():
            return (True, "Hostname válido")
        
        return (False, "Formato no reconocido. Use: IP, red/máscara o hostname")

    def leer_configuracion_actual(self):
        """
        Lee /etc/exports y devuelve lista de dicts:
        { 'carpeta':..., 'hosts':..., 'opciones': [...], 'linea_original':..., 'numero_linea': n }
        """
        configuraciones = []
        try:
            if not os.path.exists(self.ruta_exports):
                return configuraciones

            with open(self.ruta_exports, 'r') as f:
                for num, linea in enumerate(f, 1):
                    linea_raw = linea.rstrip("\n")
                    linea_strip = linea_raw.strip()
                    if not linea_strip or linea_strip.startswith('#'):
                        continue
                    
                    try:
                        idx_open = linea_raw.index('(')
                        idx_close = linea_raw.rindex(')')
                    except ValueError:
                        continue

                    antes = linea_raw[:idx_open].strip()
                    texto_opciones = linea_raw[idx_open+1:idx_close].strip()
                    partes_antes = antes.split()
                    if not partes_antes:
                        continue
                    
                    carpeta = partes_antes[0]
                    hosts = " ".join(partes_antes[1:]) if len(partes_antes) > 1 else "*"
                    opciones = [o.strip() for o in texto_opciones.split(',') if o.strip()]
                    
                    configuraciones.append({
                        'carpeta': carpeta,
                        'hosts': hosts,
                        'opciones': opciones,
                        'linea_original': linea_raw,
                        'numero_linea': num
                    })
            return configuraciones
        except Exception as e:
            print("Error leyendo configuración: {0}".format(e))
            return []

    def _validar_parametros(self, carpeta, hosts, opciones):
        if not carpeta or not hosts:
            print("Carpeta y hosts son requeridos")
            return False
        
        if not isinstance(opciones, list):
            print("Opciones deben ser lista")
            return False
        
        # Validar ruta
        valida, tipo, mensaje = self.validar_ruta(carpeta)
        if not valida:
            print("Ruta inválida: {0}".format(mensaje))
            return False
        
        # Validar red/hosts
        valida_red, mensaje_red = self.validar_red(hosts)
        if not valida_red:
            print("Hosts/Red inválida: {0}".format(mensaje_red))
            return False
        
        # Validar opciones
        for opt in opciones:
            if '=' in opt:
                clave = opt.split('=', 1)[0]
            else:
                clave = opt
            if clave not in self.opciones_validas:
                print("Opción inválida: {0}".format(opt))
                return False
        
        return True

    def _formatear_linea_exports(self, carpeta, hosts, opciones):
        texto_opciones = ",".join(opciones)
        return "{0} {1}({2})".format(carpeta, hosts, texto_opciones)

    def _crear_respaldo(self):
        try:
            if os.path.exists(self.ruta_exports):
                marca_tiempo = datetime.now().strftime("%Y%m%d_%H%M%S")
                ruta_respaldo_timestamp = "{0}.{1}".format(self.ruta_respaldo, marca_tiempo)
                shutil.copy2(self.ruta_exports, ruta_respaldo_timestamp)
                print("Respaldo creado: {0}".format(ruta_respaldo_timestamp))
        except Exception as e:
            print("Error creando respaldo: {0}".format(e))

    def agregar_configuracion(self, carpeta, hosts, opciones, ajustar_permisos=False):
        """
        Agrega una nueva línea a /etc/exports. Devuelve True/False.
        Si ajustar_permisos=True, modifica los permisos del filesystem.
        """
        try:
            if not self._validar_parametros(carpeta, hosts, opciones):
                return False
            
            # Si se solicita, ajustar permisos del filesystem
            if ajustar_permisos:
                exito, mensaje = self.aplicar_permisos_filesystem(carpeta, opciones)
                print(mensaje)
                if not exito:
                    print("Advertencia: No se pudieron ajustar los permisos del filesystem")
            
            self._crear_respaldo()
            linea = self._formatear_linea_exports(carpeta, hosts, opciones)
            
            with open(self.ruta_exports, 'a') as f:
                f.write("\n" + linea + "\n")
            
            print("Configuración agregada: {0}".format(linea))
            return True
        except Exception as e:
            print("Error agregando configuración: {0}".format(e))
            return False

    def eliminar_configuracion(self, indice):
        """
        Elimina la configuración por índice en la lista devuelta por leer_configuracion_actual.
        """
        try:
            configs = self.leer_configuracion_actual()
            if indice < 0 or indice >= len(configs):
                return False
            
            self._crear_respaldo()
            
            with open(self.ruta_exports, 'w') as f:
                for i, c in enumerate(configs):
                    if i == indice:
                        continue
                    f.write(c['linea_original'].rstrip("\n") + "\n")
            
            print("Configuración {0} eliminada".format(indice))
            return True
        except Exception as e:
            print("Error eliminando configuración: {0}".format(e))
            return False

    def obtener_opciones_validas(self):
        return sorted(list(self.opciones_validas))

    def aplicar_cambios_nfs(self):
        """
        Ejecuta 'exportfs -ra' para aplicar cambios. Retorna True si succeed.
        """
        try:
            resultado = subprocess.run(
                ["exportfs", "-ra"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                universal_newlines=True
            )
            if resultado.returncode == 0:
                print("exportfs -ra: OK")
                return True
            else:
                print("exportfs -ra error: {0}".format(resultado.stderr))
                return False
        except Exception as e:
            print("Error aplicando cambios NFS: {0}".format(e))
            return False

    def verificar_servicio_nfs(self):
        """
        Verifica el estado del servicio NFS
        Retorna (activo, mensaje)
        """
        try:
            # Verificar si el servicio está activo
            resultado = subprocess.run(
                ["systemctl", "is-active", "nfs-server"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                universal_newlines=True
            )
            
            if resultado.returncode == 0:
                return (True, "Servicio NFS activo y funcionando")
            else:
                return (False, "Servicio NFS no está activo. Ejecute: sudo systemctl start nfs-server")
                
        except Exception as e:
            return (False, "No se pudo verificar el servicio NFS: {0}".format(str(e)))