#!/usr/bin/env python3

import argparse
import subprocess
import os
import sys

def usage():
    print("Usage: script.py [-f <fichier_entree>] [-o <fichier_sortie>]")
    print("Options:")
    print("  -f, --file <fichier>    Spécifie le fichier contenant la liste des cibles à tester")
    print("  -o, --output <fichier>  Spécifie le fichier de sortie pour le résultat au format Markdown (optionnel)")
    print("  -o1, --outputcypher <fichier>  Spécifie le fichier de sortie pour les cypher pour le résultat au format Markdown (optionnel)")
    print("  -h, --help              Affiche ce message d'aide")
    sys.exit(1)

parser = argparse.ArgumentParser(add_help=False)
parser.add_argument('-f', '--file', dest='inputfile', required=True)
parser.add_argument('-o', '--output', dest='outputfile')
parser.add_argument('-o1', '--outputcypher', dest='outputfile1')
parser.add_argument('-h', '--help', action='store_true')
args, unknown = parser.parse_known_args()

if args.help:
    usage()

inputfile = args.inputfile
outputfile = args.outputfile
outputfile1 = args.outputfile1

if not os.path.isfile(inputfile):
    print(f"Le fichier {inputfile} n'existe pas.")
    sys.exit(1)

testssl_path = "/opt/tools/testssl.sh/testssl.sh"
if not os.path.isfile(testssl_path):
    print("Erreur : testssl.sh non trouvé dans /opt/tools/testssl.sh/")
    sys.exit(1)

def write_output(text, file_path=None):
    if file_path:
        with open(file_path, 'a') as f:
            f.write(text + '\n')
    print(text)

if outputfile:
    sortie_dir = os.path.dirname(outputfile)
    if sortie_dir and not os.path.exists(sortie_dir):
        os.makedirs(sortie_dir, exist_ok=True)
    open(outputfile, 'w').close()

if outputfile1:
    sortie_dir = os.path.dirname(outputfile1)
    if sortie_dir and not os.path.exists(sortie_dir):
        os.makedirs(sortie_dir, exist_ok=True)
    open(outputfile1, 'w').close()

header1 = "| Machine | Port | SSLv2 | SSLv3 | TLS 1.0 | TLS 1.1 | TLS 1.2 | TLS 1.3 |"
header2 = "| ------ | --- | :-: | :-: | :-: | :-: | :-: | :-: |"
write_output(header1, outputfile)
write_output(header2, outputfile)

with open(inputfile, 'r') as fin:
    for line in fin:
        line = line.strip()
        if not line:
            continue
        result = subprocess.getoutput(f'{testssl_path} -p --color 0 "{line}" 2>&1')
        machine = line
        port = line.split(':')[-1] if ':' in line else "443"
        sslv2 = "❌" if "SSLv2" in result and "not offered" in result else "✅"
        sslv3 = "❌" if "SSLv3" in result and "not offered" in result else "✅"
        tls1 = "❌" if "TLS 1.0" in result and "not offered" in result else "✅"
        tls11 = "❌" if "TLS 1.1" in result and "not offered" in result else "✅"
        tls12 = "❌" if "TLS 1.2" in result and "not offered" in result else "✅"
        tls13 = "❌" if "TLS 1.3" in result and "not offered" in result else "✅"
        ligne = f"| {machine} | {port} | {sslv2} | {sslv3} | {tls1} | {tls11} | {tls12} | {tls13} |"
        write_output(ligne, outputfile)

header3 = "| Machine        | Port  |      LUCKY13      |      SWEET32      |     POODLE     | BEAST |"
header4 = "|:---------:|:---:|:-----:|:-----:|:-----:|:-----:|"
write_output(header3, outputfile1)
write_output(header4, outputfile1)

with open(inputfile, 'r') as fin:
    for line in fin:
        line = line.strip()
        if not line:
            continue
        result = subprocess.getoutput(f'{testssl_path} -L -A -O -W --color 0 "{line}" 2>&1')
        machine = line
        port = line.split(':')[-1] if ':' in line else "443"
        LUCKY13 = "✅" if "LUCKY13" in result and "not vulnerable" in result else "❌"
        SWEET32 = "✅" if "SWEET32" in result and "not vulnerable" in result else "❌"
        POODLE  = "✅" if "POODLE"  in result and "not vulnerable" in result else "❌"
        BEAST   = "✅" if "BEAST"   in result and "not vulnerable" in result else "❌"
        ligne2 = f"| {machine} | {port} | {LUCKY13} | {SWEET32} | {POODLE} | {BEAST} |"
        write_output(ligne2, outputfile1)

if outputfile:
    print(f"Le résultat a été écrit dans {outputfile}")

if outputfile1:
    print(f"Le résultat cypher a été écrit dans {outputfile1}")


for f in os.listdir('.'):
    if f.startswith('core'):
        try:
            os.remove(f)
        except OSError:
            pass
