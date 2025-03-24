# -------------------------------------------------------------
# Fichier : Serial-Argos-Test-All-AT.py
# Auteur  : Paul Miailhe
# Date    : 21/03/2025
# Objet   : Script de test d'interface série avec le module Argos-SMD ARRIBADA
 
# Copyright (c) 2025 CNES - Centre National d'Études Spatiales 
# -------------------------------------------------------------

"""
Liste complète des commandes AT pour le module SMD Argos (avec tailles approximatives) :

- AT+PING=?                                    : Ping du module SMD                                 (~10 octets)
- AT+FW=?                                      : Lecture de la version firmware                     (~8 octets)
- AT+ADDR=?                                    : Lecture de l'adresse (MAC)                         (~10 octets)
- AT+ADDR=xxxx                                 : Écriture de l'adresse (MAC)                        (~14 octets)
- AT+SECKEY=?                                  : Lecture de la clé secrète                          (~12 octets)
- AT+SECKEY=xxxx                               : Écriture de la clé secrète                         (~38 octets)
- AT+SN=?                                      : Lecture du numéro de série                         (~8 octets)
- AT+ID=?                                      : Lecture de l'identifiant SMD                       (~8 octets)
- AT+ID=xxxx                                   : Écriture de l'identifiant                          (~14 octets)
- AT+TCXO_WU=?                                 : Lecture du temps de warm-up du TCXO                (~14 octets)
- AT+TCXO_WU=xxxx                              : Écriture du temps de warm-up du TCXO               (~20 octets)
- AT+RCONF=?                                   : Lecture de la configuration radio                  (~12 octets)
- AT+SAVE_RCONF=                               : Sauvegarde de la configuration radio               (~16 octets)
- AT+TX=...                                    : Envoi d'un message uplink                          (~58 octets)
- AT+CW=...                                    : Envoi d’un signal en mode onde continue (CW)       (~30 octets)
- AT+LPM=?                                     : Lecture du mode basse consommation                 (~10 octets)
- AT+LPM=...                                   : Écriture du mode basse consommation                (~12 octets)
- AT+VERSION=?                                 : Lecture de la version AT                           (~14 octets)
- AT+UDATE=?                                   : Lecture de la date UTC                             (~12 octets)
- AT+KMAC=0                                    : Réinitialisation de profil KMAC                    (~10 octets)
- AT+KMAC=1                                    : Activation de profil KMAC                          (~10 octets)
- AT+RCONF=44cd3a299068292a74d2126f3402610d    : Configuration radio : LDA2                         (~44 octets)
- AT+RCONF=bd176535b394a665bd86f354c5f424fb    : Configuration radio : LDA2L                        (~44 octets)
- AT+RCONF=efd2412f8570581457f2d982e76d44d7    : Configuration radio : VLDA4                        (~44 octets)
- AT+RCONF=41bc11b8980df01ba8b4b8f41099620b    : Configuration radio : LDK                          (~44 octets)
"""

import serial
import time
from datetime import datetime

# Configuration du port série
SERIAL_PORT = 'COM6'       # À adapter à votre système
BAUD_RATE = 9600
TIMEOUT = 2   

# Liste des codes d’erreur +ERROR=XX retournés par le module SMD
ERROR_CODES = {
    0:  "Aucune erreur (OK)",
    1:  "Commande AT inconnue",
    2:  "Format de paramètre invalide",
    3:  "Paramètres manquants",
    4:  "Trop de paramètres",
    5:  "Valeur incompatible",
    6:  "Commande AT non reconnue",
    7:  "ID invalide",
    8:  "ID inconnu",
    20: "Longueur des données utilisateur invalide",
    21: "File d'attente de données pleine",
    22: "File d'attente de données vide",
    30: "Timeout de réception RX",
    40: "Erreur transceiver (par ex : message non émis)",
    41: "Erreur d’auto-réglage du transceiver",
    42: "Erreur PLL transceiver",
    43: "Timeout oscillateur transceiver",
    44: "Reset transceiver",
    60: "Fréquence de TX/Modulation non valide dans la config",
}

# Liste des commandes AT à tester
COMMANDES_AT = [
    "AT+KMAC=0",
    "AT+KMAC=1",
    "AT+PING=?",
    "AT+FW=?",
    "AT+ADDR=?",
    "AT+SECKEY=?",
    "AT+SN=?",
    "AT+ID=?",
    "AT+TCXO_WU=?",
    "AT+RCONF=?",
    "AT+SAVE_RCONF=",
    "AT+TX=000000000000000000000000000000000000000000000000",
    "AT+CW=1,401000000,20",
    "AT+LPM=?",
    "AT+VERSION=?",
    "AT+UDATE=?",
    # Configurations spécifiques
    "AT+RCONF=44cd3a299068292a74d2126f3402610d",  # LDA2
    "AT+RCONF=bd176535b394a665bd86f354c5f424fb",  # LDA2L
    "AT+RCONF=efd2412f8570581457f2d982e76d44d7",  # VLDA4
    "AT+RCONF=41bc11b8980df01ba8b4b8f41099620b",  # LDK
]

def envoyer_commande(ser, commande):
    print(f"\n> Envoi : {commande}")
    ser.write((commande + "\r\n").encode())
    
    response = b""
    start_time = time.time()
    while True:
        chunk = ser.read(1)
        if not chunk or time.time() - start_time > TIMEOUT:
            break
        response += chunk
    print("< Réponse :", response.decode(errors='replace').strip())

def log_to_file(content):
    with open("argos_log_test_command.txt", "a", encoding="utf-8") as f:
        f.write(content + "\n")

def interpret_error(response: str):
    if "+ERROR=" in response:
        try:
            code = int(response.split("+ERROR=")[1].split()[0])
            meaning = ERROR_CODES.get(code, "Code d'erreur inconnu")
            print(f"Erreur détectée : +ERROR={code} → {meaning}")
            log_to_file(f"[ERROR {code}] {meaning}")
        except Exception:
            print("Format d'erreur non reconnu.")
            log_to_file("[ERROR] Format non reconnu")

def timestamp():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def send_command(ser, command):
    now = timestamp()
    print(f"\n{now} > Envoi : {command}")
    log_to_file(f"[{now}] > {command}")
    ser.write(command.encode() + b'\r\n')
    response = b""
    while True:
        chunk = ser.read(1)
        if not chunk:
            break
        response += chunk
    decoded = response.decode(errors='replace').strip()
    print(f"< Réponse : {decoded}")
    log_to_file(f"[{now}] < {decoded}")
    interpret_error(decoded)
    return decoded

def main():
    print("Test des commandes AT - Initialisation du port série...")
    try:
        with serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=TIMEOUT) as ser:
            time.sleep(2)  # Petite pause après ouverture du port
            for cmd in COMMANDES_AT:
                send_command(ser, cmd)
                time.sleep(0.5)  # Pause entre les commandes
    except serial.SerialException as e:
        print(f"Erreur de communication série : {e}")
    print("\nTest terminé.")

if __name__ == "__main__":
    main()
