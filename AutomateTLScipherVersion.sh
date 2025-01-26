#!/bin/bash

# Ce script utilise testssl.sh situé dans /opt/tools/testssl.sh/testssl.sh

usage() {
    echo "Usage: $0 [-f <fichier_entree>] [-o <fichier_sortie>]"
    echo "Options:"
    echo "  -f, --file <fichier>    Spécifie le fichier contenant la liste des cibles à tester"
    echo "  -o, --output <fichier>  Spécifie le fichier de sortie pour le résultat au format Markdown (optionnel)"
    echo "  -h, --help              Affiche ce message d'aide"
    exit 1
}

inputfile=""
outputfile=""

while [[ $# -gt 0 ]]; do
    case $1 in
        -f|--file)
            inputfile="$2"
            shift 2
            ;;
        -o|--output)
            outputfile="$2"
            shift 2
            ;;
        -h|--help)
            usage
            ;;
        *)
            echo "Option non reconnue : $1"
            usage
            ;;
    esac
done

if [ -z "$inputfile" ]; then
    echo "Erreur : Vous devez spécifier un fichier d'entrée avec l'option -f ou --file"
    usage
fi

if [ ! -f "$inputfile" ]; then
    echo "Le fichier $inputfile n'existe pas."
    exit 1
fi

if [ ! -f "/opt/tools/testssl.sh/testssl.sh" ]; then
    echo "Erreur : testssl.sh non trouvé dans /opt/tools/testssl.sh/"
    exit 1
fi

output() {
    if [ -n "$outputfile" ]; then
        echo "$1" >> "$outputfile"
    fi
    echo "$1"
}

if [ -n "$outputfile" ]; then
    sortie_dir=$(dirname "$outputfile")
    if [ ! -d "$sortie_dir" ]; then
        mkdir -p "$sortie_dir"
        if [ $? -ne 0 ]; then
            echo "Erreur : Impossible de créer le répertoire $sortie_dir"
            exit 1
        fi
    fi
    > "$outputfile"
fi

output "| Machine | Port | SSLv2 | SSLv3 | TLS 1.0 | TLS 1.1 |"
output "| --- | --- | :-: | :-: | :-: | :-: |"

while IFS= read -r ligne
do
    resultat=$(/opt/tools/testssl.sh/testssl.sh --color 0 "$ligne" 2>&1 | tee /dev/tty)
    
    machine="$ligne"
    port=$(echo "$ligne" | grep -oP ':\K\d+$' || echo "443")
    
    sslv2=$(echo "$resultat" | grep -q "SSLv2.*not offered" && echo "❌" || echo "✅")
    sslv3=$(echo "$resultat" | grep -q "SSLv3.*not offered" && echo "❌" || echo "✅")
    tls1=$(echo "$resultat" | grep -q "TLS 1.0.*not offered" && echo "❌" || echo "✅")
    tls11=$(echo "$resultat" | grep -q "TLS 1.1.*not offered" && echo "❌" || echo "✅")

    output "| $machine | $port | $sslv2 | $sslv3 | $tls1 | $tls11 |"
    
done < "$inputfile"

if [ -n "$outputfile" ]; then
    echo "Le résultat a été écrit dans $outputfile"
fi

rm core*