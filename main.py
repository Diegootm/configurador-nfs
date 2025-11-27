# main.py
import tkinter as tk
import sys

from gestor_nfs import GestorNFS
from ui.ventana_principal import VentanaPrincipal
from utils.compatibilidad import verificar_compatibilidad, verificar_permisos_administrador

def principal():
    print("Iniciando Configurador NFS...")
    if not verificar_compatibilidad():
        print("Advertencia: sistema no 100% compatible o /etc/exports ausente")
    if not verificar_permisos_administrador():
        print("Advertencia: parece que no se ejecuta como root. Algunas operaciones fallarán.")
    gestor = GestorNFS()
    raiz = tk.Tk()
    app = VentanaPrincipal(raiz, gestor)
    raiz.geometry("900x700")
    try:
        raiz.eval('tk::PlaceWindow . center')
    except Exception:
        pass
    raiz.mainloop()

if __name__ == "__main__":
    principal()
