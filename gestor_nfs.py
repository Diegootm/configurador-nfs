# gestor_nfs.py
# Compatible con Python 3.6.15

import os
import shutil
from datetime import datetime
import subprocess
import stat

class GestorNFS(object):
    """
    Clase para gestionar /etc/exports de forma simple y segura.
    """

    def __init__(self, ruta_exports="/etc/exports"):
        self.ruta_exports = ruta_exports
        self.ruta_respaldo = "{0}.respaldo".format(ruta_exports)
        # opciones válidas (las que aceptan valor se deben pasar como 'clave=valor')
        self.opciones_validas = {
            'rw', 'ro', 'sync', 'async', 'no_root_squash',
            'root_squash', 'all_squash', 'no_subtree_check',
            'subtree_check', 'insecure', 'secure', 'anonuid',
            'anongid'
        }

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
                    # Buscar paréntesis que contienen opciones
                    try:
                        idx_open = linea_raw.index('(')
                        idx_close = linea_raw.rindex(')')
                    except ValueError:
                        # línea no en formato esperado, omitir
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
        # validar opciones
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

    def agregar_configuracion(self, carpeta, hosts, opciones):
        """
        Agrega una nueva línea a /etc/exports. Devuelve True/False.
        """
        try:
            if not self._validar_parametros(carpeta, hosts, opciones):
                return False
            self._crear_respaldo()
            linea = self._formatear_linea_exports(carpeta, hosts, opciones)
            # Asegurarse de terminar con newline
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
# Fin de gestor_nfs.py
