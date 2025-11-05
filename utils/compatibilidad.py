# esto espara verificar la compatibilidad del SO

import os 

def verificar_compatilibidad():

    try: 
        if os.path.exists ("etc/exports"):
            print("archivo /etc/exports encotrado")
            return True
        else:
            print("el archivo no fue encotrado")
            return True
    
    except Exception as error:
        print(f"error verificado compatibilidad: {error}")
        return True

def verificar_permisos_administrador():
    # esto es para verificar si tenemos permisos de administrador

    try:
        return os.geteuid() == 0
    except AttributeError:

        return True

        