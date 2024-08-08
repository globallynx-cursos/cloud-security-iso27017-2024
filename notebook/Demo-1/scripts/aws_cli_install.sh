#!/bin/bash

# Actualizar paquetes
sudo apt update

# Instalar dependencias
sudo apt install curl unzip -y

# Cambiar al directorio temporal
cd /tmp

# Descargar AWS CLI
curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"

# Descomprimir el archivo
unzip awscliv2.zip

# Instalar AWS CLI
sudo ./aws/install

# Verificar la instalación
aws --version

# Limpiar archivos temporales
rm -rf awscliv2.zip aws
