#!/bin/bash
# install_deps.sh - Instalador Seguro de Dependências para o ND Hub PyScripts

echo -e "\e[1;36m=============================================\e[0m"
echo -e "\e[1;36m       Instalador: Convertores ND Hub        \e[0m"
echo -e "\e[1;36m=============================================\e[0m"

echo ""
echo -e "\e[1;34m[1/2] Checando pacotes de sistema (Ubuntu)... \e[0m"
echo -e "\e[2mIsso pode requerer senha de super usuário (Polkit).\e[0m"
pkexec env DISPLAY=$DISPLAY XAUTHORITY=$XAUTHORITY apt-get update
pkexec env DISPLAY=$DISPLAY XAUTHORITY=$XAUTHORITY apt-get install -y ffmpeg imagemagick libreoffice-core

echo ""
echo -e "\e[1;34m[2/2] Injetando libs no Virtual Env isolado... \e[0m"
VENV_ACTIVATE="/home/neto/gns/tools/.venv/bin/activate"

if [ -f "$VENV_ACTIVATE" ]; then
    source "$VENV_ACTIVATE"
    # Atualiza pip
    pip install --upgrade pip
    # Instala dependências de conversão e sqlite/pandas
    pip install pillow pandas reportlab pypdf pyyaml openpyxl python-docx
    echo -e "\e[1;32mBibliotecas python injetadas com sucesso.\e[0m"
else
    echo -e "\e[1;31mErro Crítico: VirtualEnv não encontrado em /home/neto/gns/tools/.venv\e[0m"
    echo -e "\e[1;31mCrie antes executando: python3 -m venv /home/neto/gns/tools/.venv\e[0m"
    exit 1
fi

echo ""
echo -e "\e[1;32m=============================================\e[0m"
echo -e "\e[1;32m TUDO PRONTO! O Conversor funcionará 100%    \e[0m"
echo -e "\e[1;32m=============================================\e[0m"
