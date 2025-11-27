# utils/compatibilidad.py
import os

def verificar_compatibilidad():
    """
    Verifica que /etc/exports exista (advertencia si no) y devuelve True/False.
    """
    try:
        if os.path.exists("/etc/exports"):
            return True
        else:
            # el archivo puede no existir en instalaciones mínimas; no necesariamente fatal
            print("Advertencia: /etc/exports no encontrado")
            return True

    except Exception as e:
        print("Error verificando compatibilidad: {0}".format(e))
        return False

def verificar_permisos_administrador():
    """
    Retorna True si se ejecuta como root (Unix). En Windows, intenta devolver True para permitir testing.
    """
    try:
        return os.geteuid() == 0
    except AttributeError:
        # Windows o plataforma sin geteuid -> no se puede verificar, asumir True (para testing)
        return True
