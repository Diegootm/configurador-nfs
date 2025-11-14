
# Configurador NFS para OpenSUSE 15.6

Esta es una aplicacion de formato grafico que permite gestionarl las configuraciones del servidor NFS.

## Características

- Ver configuraciones actuales de NFS
- Agregar nuevas configuraciones
- Eliminar configuraciones existentes
- Aplicar cambios al servicio NFS
- Interfaz en español

## Requisitos del Sistema

### Version de software necesario
- Opensuse 15.6 (el mas recomendado) o superiores
- Python 3.6 o superior
- Tkinter (viene incluido con Python)
- Sistema Linux con NFS

## Entorno de desarrollo
### Instalacion del entorno de desarrollo:

```bash
# 1. Instalar Python y Tkinter
sudo zypper install -y python3 python3-tk

# 2. Instalar editor de código (opcional)
sudo zypper install -y vscode    # Visual Studio Code
# O
sudo zypper install -y geany     # Geany (más liviano)

# 3. Clonar el repositorio
git clone https://github.com/TU_USUARIO/configurador-nfs.git
cd configurador-nfs
```


## Guía de Instalación - Configurador NFS

### Instalación Automática:

```bash
# Descargar el proyecto
git clone https://github.com/Diegootm/configurador-nfs.git
cd configurador-nfs
# Ejecutar script de instalación
chmod +x install.sh
sed -i 's/\r$//' install.sh
sudo ./install.sh
# Ejecutar configurador-nfs
configurador-nfs
```
Finalmente va a estar listo para el uso en tu equipo!
