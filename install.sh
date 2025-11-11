#!/bin/bash
# Script de instalación para Configurador NFS

echo "=== Instalando Configurador NFS ==="

# Verificar que estamos en OpenSUSE
if [ ! -f /etc/os-release ] || ! grep -q "openSUSE" /etc/os-release; then
    echo "⚠️  Advertencia: Este script está diseñado para OpenSUSE"
fi

# Verificar Python
if ! command -v python3 &> /dev/null; then
    echo " Error: Python3 no está instalado"
    echo " Instalando Python3..."
    sudo zypper install -y python3
fi

# Verificar Tkinter
if ! python3 -c "import tkinter" 2>/dev/null; then
    echo " Instalando Tkinter..."
    sudo zypper install -y python3-tk
fi

# Crear directorio de instalación
echo "Creando directorio de instalación..."
sudo mkdir -p /opt/configurador-nfs

# Copiar archivos de la aplicación
echo "Copiando archivos de la aplicación..."
sudo cp -r *.py ui utils /opt/configurador-nfs/

# Crear script ejecutable
echo " Creando script ejecutable..."
sudo tee /usr/local/bin/configurador-nfs > /dev/null << 'EOF'
#!/bin/bash
cd /opt/configurador-nfs
python3 main.py "$@"
EOF

sudo chmod +x /usr/local/bin/configurador-nfs

# Crear entrada en el menú de aplicaciones
echo " Creando entrada en el menú..."
sudo tee /usr/share/applications/configurador-nfs.desktop > /dev/null << 'EOF'
[Desktop Entry]
Version=1.0
Type=Application
Name=Configurador NFS
Comment=Configurador gráfico para servidor NFS en OpenSUSE
Exec=configurador-nfs
Icon=network-server
Terminal=false
Categories=System;Settings;
Keywords=nfs;server;network;configurador;opensuse;
EOF

echo ""
echo " ¡Instalación completada!"
echo ""
echo " Ahora puedes usar el Configurador NFS de las siguientes formas:"
echo "   1. Ejecutar en terminal: configurador-nfs"
echo "   2. Buscar en el menú: 'Configurador NFS'"
echo "   3. Icono en System → Configurador NFS"
echo ""
echo "📝 Nota: Para modificar /etc/exports, ejecuta como root:"
echo "   sudo configurador-nfs"
