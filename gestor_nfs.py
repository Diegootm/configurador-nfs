import os
import re 
import shutil
from datetime import datetime
import subprocess


class GestorNfs():


    def __init__(self, ruta_exports="/etc/exports"):
        self.ruta_exports = ruta_exports
        self.ruta_respaldo = f"{ruta_exports}.respaldo"
        self.opciones_validas = {
            'rw', 'ro', 'sync', 'async', 'no_root_squash', 
            'root_squash', 'all_squash', 'no_subtree_check', 
            'subtree_check', 'insecure', 'secure', 'anonuid', 'anongid'
        }
    
    def leer_configuracion_actual(self):
        # para ver las configuracion del archivo 

        configuraciones = []

        try: 
            if not os.path.exists(self.ruta_exports):
                return configuraciones
            
            with open(self.ruta_exports, 'r') as archivo:
                 for numero_linea, linea in enumerate(archivo, 1):
                    linea = linea.strip()

                    if not linea or linea.strartswith('#')
                    continue

                    configuracion = self._analizar_linea_exports(linea, numero_linea)

                    if configuracion: 
                        configuraciones.apped(configuracion)
                return configuraciones
        
        except Exception as error:
            print(f"error al leer la configuracion {errro}")
            return []

    def _analizar_linea_exports(self, linea, numero_linea):
        # esto para analizar una linea de archivo de exports y extrae la informacion

        try:
            patron = r'^(\S+)\s+(\S+)\(([^)]+)\)$'
            coincidencia = re.match(patron, linea)
            
            if not coincidencia:
                return None
            
            carpeta, host, texto_opciones = coincidencia.groups()
            opciones = [opcion.strip() for opcion in texto_opciones.split(',')]
            
            return {
                'carpeta': carpeta,
                'host': host,
                'opciones': opciones,
                'linea_original': linea,
                'numero_linea': numero_linea
            }
            
        except Exception as error:
            print(f"Error analizando línea {numero_linea}: {error}")
            return None
    
    def agregar_configuracion(self, carpeta, host, opciones):
        """
        Agrega una nueva configuración al archivo exports
        """
        try:
            if not self._validar_parametros(carpeta, host, opciones):
                return False
            
            self._crear_respaldo()
            
            linea_nueva = self._formatear_linea_exports(carpeta, host, opciones)
            
            with open(self.ruta_exports, 'a') as archivo:
                archivo.write(f"\n{linea_nueva}")
            
            print(f"Configuración agregada: {linea_nueva}")
            return True
            
        except Exception as error:
            print(f"Error agregando configuración: {error}")
            return False
    
    def eliminar_configuracion(self, indice):
        """
        Elimina una configuración del archivo exports
        """
        try:
            configuraciones = self.leer_configuracion_actual()
            
            if indice < 0 or indice >= len(configuraciones):
                return False
            
            self._crear_respaldo()
            
            with open(self.ruta_exports, 'w') as archivo:
                for i, configuracion in enumerate(configuraciones):
                    if i != indice:
                        archivo.write(f"{configuracion['linea_original']}\n")
            
            print(f"Configuración {indice} eliminada exitosamente")
            return True
            
        except Exception as error:
            print(f"Error eliminando configuración: {error}")
            return False
    
    def _validar_parametros(self, carpeta, host, opciones):
        """
        Valida los parámetros de configuración
        """
        if not carpeta or not host:
            print("Error: Carpeta y host son requeridos")
            return False
        
        if not isinstance(opciones, list):
            print("Error: Las opciones deben ser una lista")
            return False
        
        for opcion in opciones:
            if opcion not in self.opciones_validas:
                print(f"Error: Opción inválida: {opcion}")
                return False
        
        return True
    
    def _formatear_linea_exports(self, carpeta, host, opciones):
        """
        Formatea una línea para el archivo exports
        """
        texto_opciones = ','.join(opciones)
        return f"{carpeta} {host}({texto_opciones})"
    
    def _crear_respaldo(self):
        """
        Crea un respaldo del archivo exports actual
        """
        try:
            if os.path.exists(self.ruta_exports):
                marca_tiempo = datetime.now().strftime("%Y%m%d_%H%M%S")
                ruta_respaldo_timestamp = f"{self.ruta_respaldo}.{marca_tiempo}"
                shutil.copy2(self.ruta_exports, ruta_respaldo_timestamp)
                print(f"Respaldo creado: {ruta_respaldo_timestamp}")
        except Exception as error:
            print(f"Error creando respaldo: {error}")
    
    def obtener_opciones_validas(self):
        """
        Retorna la lista de opciones válidas para NFS
        """
        return self.opciones_validas.copy()
    
    def aplicar_cambios_nfs(self):
        """
        Aplica los cambios reiniciando el servicio NFS
        """
        try:
            resultado = subprocess.run(["exportfs", "-ra"], 
                                     capture_output=True, text=True)
            
            if resultado.returncode == 0:
                print("Configuraciones NFS aplicadas exitosamente")
                return True
            else:
                print(f"Error aplicando configuraciones NFS: {resultado.stderr}")
                return False
                
        except Exception as error:
            print(f"Error aplicando cambios NFS: {error}")
            return False