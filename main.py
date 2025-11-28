# main.py
# Compatible con Python 3.6.15
# Punto de entrada principal del Configurador NFS

import tkinter as tk
from tkinter import messagebox
import sys
import os
import subprocess

from gestor_nfs import GestorNFS
from ui.ventana_principal import VentanaPrincipal
from utils.compatibilidad import verificar_compatibilidad, verificar_permisos_administrador

def mostrar_advertencia_permisos():
    """Muestra una advertencia si no se ejecuta como root"""
    root = tk.Tk()
    root.withdraw()  # Ocultar ventana principal temporalmente
    
    respuesta = messagebox.askquestion(
        "⚠️ Advertencia de Permisos",
        "No se está ejecutando como root (superusuario).\n\n"
        "Algunas operaciones FALLARÁN:\n"
        "• Modificar /etc/exports\n"
        "• Ajustar permisos del sistema de archivos\n"
        "• Aplicar cambios con exportfs\n\n"
        "Para usar todas las funciones, ejecute:\n"
        "sudo configurador-nfs\n\n"
        "¿Desea continuar de todos modos?\n"
        "(Solo podrá ver configuraciones existentes)",
        icon='warning'
    )
    
    root.destroy()
    
    return respuesta == 'yes'

def verificar_nfs_instalado():
    """Verifica si NFS está instalado en el sistema"""
    try:
        # Verificar si exportfs existe
        resultado = subprocess.run(
            ["which", "exportfs"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            universal_newlines=True
        )
        
        if resultado.returncode != 0:
            root = tk.Tk()
            root.withdraw()
            
            messagebox.showerror(
                "❌ NFS No Instalado",
                "El servidor NFS no está instalado en el sistema.\n\n"
                "Para instalar NFS en OpenSUSE 15.6, ejecute:\n\n"
                "sudo zypper install nfs-kernel-server\n"
                "sudo systemctl enable nfs-server\n"
                "sudo systemctl start nfs-server\n\n"
                "El programa se cerrará."
            )
            
            root.destroy()
            return False
        
        return True
        
    except Exception as e:
        print("Error verificando NFS: {0}".format(e))
        return True  # Continuar de todos modos

def principal():
    """Función principal del programa"""
    print("=" * 60)
    print("Configurador NFS para OpenSUSE 15.6")
    print("Compatible con Python 3.6.15")
    print("=" * 60)
    print("")
    
    # Verificar compatibilidad del sistema
    if not verificar_compatibilidad():
        print("⚠️  ADVERTENCIA: Sistema no compatible o /etc/exports ausente")
        print("   El programa puede no funcionar correctamente")
        print("")
    
    # Verificar si NFS está instalado
    if not verificar_nfs_instalado():
        sys.exit(1)
    
    # Verificar permisos de administrador
    es_root = verificar_permisos_administrador()
    
    if not es_root:
        print("⚠️  ADVERTENCIA: No se ejecuta como root")
        print("   Para funcionalidad completa, ejecute: sudo configurador-nfs")
        print("")
        
        # Mostrar diálogo de advertencia
        if not mostrar_advertencia_permisos():
            print("Operación cancelada por el usuario.")
            sys.exit(0)
    else:
        print("✓ Ejecutando como root - Funcionalidad completa disponible")
        print("")
    
    # Crear instancia del gestor NFS
    try:
        gestor = GestorNFS()
        print("✓ Gestor NFS inicializado correctamente")
    except Exception as e:
        print("❌ Error inicializando gestor NFS: {0}".format(e))
        sys.exit(1)
    
    # Crear ventana principal
    try:
        raiz = tk.Tk()
        
        # Configurar geometría y posición
        raiz.geometry("950x750")
        
        # Centrar ventana en la pantalla
        try:
            raiz.eval('tk::PlaceWindow . center')
        except Exception:
            # Método alternativo para centrar
            raiz.update_idletasks()
            ancho = raiz.winfo_width()
            alto = raiz.winfo_height()
            x = (raiz.winfo_screenwidth() // 2) - (ancho // 2)
            y = (raiz.winfo_screenheight() // 2) - (alto // 2)
            raiz.geometry('{0}x{1}+{2}+{3}'.format(ancho, alto, x, y))
        
        # Crear interfaz
        app = VentanaPrincipal(raiz, gestor)
        
        print("✓ Interfaz gráfica cargada")
        print("")
        print("=" * 60)
        print("Aplicación iniciada correctamente")
        print("=" * 60)
        print("")
        
        # Iniciar loop de eventos
        raiz.mainloop()
        
    except Exception as e:
        print("❌ Error creando interfaz gráfica: {0}".format(e))
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    try:
        principal()
    except KeyboardInterrupt:
        print("\n\nPrograma interrumpido por el usuario")
        sys.exit(0)
    except Exception as e:
        print("\n❌ Error fatal: {0}".format(e))
        import traceback
        traceback.print_exc()
        sys.exit(1)
