import os

def verificar_compatibilidad():
    """
    Verifica si el sistema es compatible
    """
    try:
        if os.path.exists("/etc/exports"):
            print("Archivo /etc/exports encontrado")
            return True
        else:
            print("Advertencia: Archivo /etc/exports no encontrado")
            return True 
            
    except Exception as error:
        print(f"Error verificando compatibilidad: {error}")
        return True  


def verificar_permisos_administrador():
    """
    Verifica si la aplicación tiene permisos de administrador
    """
    try:
        return os.geteuid() == 0
    except AttributeError:
        return True

        
