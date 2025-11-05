#!/usr/bin/env python3
"""
Aplicación principal para gestión de configuración NFS
"""

import sys
import os

# Añadir el directorio actual al path para imports
#sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from gestor_nfs import GestorNFS
from ui.ventana_principal import VentanaPrincipal
from utils.compatibilidad import verificar_compatibilidad
import tkinter as tk


def principal():
    """
    Función principal que inicia la aplicación
    """
    print("Iniciando aplicación de configuración NFS...")
    
    # Verificar compatibilidad del sistema
    if not verificar_compatibilidad():
        print("Advertencia: El sistema puede no ser completamente compatible")
    
    # Crear instancia del gestor NFS
    gestor_nfs = GestorNFS()
    
    # Crear y mostrar la interfaz gráfica
    raiz = tk.Tk()
    aplicacion = VentanaPrincipal(raiz, gestor_nfs)
    
    # Configurar la ventana principal
    raiz.title("Configurador NFS - OpenSUSE 15.6")
    raiz.geometry("900x700")
    
    # Centrar la ventana en la pantalla
    raiz.eval('tk::PlaceWindow . center')
    
    # Iniciar el loop principal de la aplicación
    print("Aplicación iniciada correctamente")
    raiz.mainloop()


if __name__ == "__main__":
    principal()