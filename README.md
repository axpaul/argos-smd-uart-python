# Python Demonstrator – Arribada Argos SMD Module

## Overview

This project provides a Python-based script to test, configure, and communicate with the **Argos SMD module** developed by **Arribada Initiative**.  
The module is mounted on an **Arribada Wing board**, and connected to a computer via a **USB–UART FTDI adapter (3.3V TTL logic level)**.

The script acts as a lightweight command-line interface to:
- Send AT commands
- Configure radio modes (e.g. LDA2)
- Send Argos uplink messages
- Interpret module responses and errors
- Log communication activity

---

## Hardware Setup

### Arribada Wing ↔ FTDI USB-TTL Connection

![FTDI Wiring](Capture%20d’écran%202025-03-24%20165737.png)

| Arribada Wing Pin | FTDI Cable Wire           | Description                      |
|-------------------|---------------------------|----------------------------------|
| `3V3`             | VCC (red)                 | Power supply (3.3V)              |
| `TX`              | RX (yellow)               | UART transmission (Wing → PC)    |
| `RX`              | TX (orange)               | UART reception (PC → Wing)       |
| `GND`             | GND (black)               | Ground / common reference        |

> **Important:** The module operates at 3.3V logic only. Do not use 5V-level UART signals.

---

## Script Features (`Serial-Argos-Demo.py`)

- Automatic UART initialization
- Radio configuration (e.g. LDA2 mode)
- Periodic Argos uplink transmission (every 3 seconds)
- Response decoding with timestamp
- AT error code interpretation
- Interactive mode on keyboard interrupt
- Logging to `argos_log.txt`

---

## Supported AT Commands

| AT Command                     | Description                                             | Typical Size |
|--------------------------------|---------------------------------------------------------|--------------|
| `AT+PING=?`                   | Ping the module                                         | ~10 bytes    |
| `AT+FW=?`                     | Read firmware version                                   | ~8 bytes     |
| `AT+ADDR=?`                  | Read MAC address                                        | ~10 bytes    |
| `AT+ADDR=xxxx`                | Set MAC address                                         | ~14 bytes    |
| `AT+SECKEY=?`                 | Read device secret key                                  | ~12 bytes    |
| `AT+SECKEY=xxxxxxxx...`       | Write secret key (32 hex bytes)                         | ~38 bytes    |
| `AT+SN=?`                     | Read serial number                                      | ~8 bytes     |
| `AT+ID=?`                     | Read module ID                                          | ~8 bytes     |
| `AT+ID=xxxx`                  | Set module ID                                           | ~14 bytes    |
| `AT+TCXO_WU=?`                | Read TCXO warmup time                                   | ~14 bytes    |
| `AT+TCXO_WU=xxxx`             | Set TCXO warmup time                                    | ~20 bytes    |
| `AT+RCONF=?`                  | Read current radio configuration                        | ~12 bytes    |
| `AT+RCONF=...`                | Set radio configuration                                 | ~44 bytes    |
| `AT+SAVE_RCONF=`             | Save radio configuration                                | ~16 bytes    |
| `AT+TX=...`                   | Send Argos uplink message (48 hex chars = 24 bytes)     | ~58 bytes    |
| `AT+CW=Mode,Freq,Power`       | Transmit continuous wave signal                         | ~30 bytes    |
| `AT+LPM=?`                    | Read low-power mode                                     | ~10 bytes    |
| `AT+LPM=x`                    | Set low-power mode                                      | ~12 bytes    |
| `AT+VERSION=?`                | Read AT version                                         | ~14 bytes    |
| `AT+UDATE=?`                  | Read UTC date                                           | ~12 bytes    |
| `AT+KMAC=0`                   | Reset KMAC profile                                      | ~10 bytes    |
| `AT+KMAC=1`                   | Apply KMAC profile                                      | ~10 bytes    |

---

## Error Codes `+ERROR=XX`

| Code | Description                                              |
|------|----------------------------------------------------------|
| 0    | No error (OK)                                            |
| 1    | Unknown AT command                                       |
| 2    | Invalid parameter format                                 |
| 3    | Missing parameters                                       |
| 4    | Too many parameters                                      |
| 5    | Incompatible value                                       |
| 6    | AT command not recognized                                |
| 7    | Invalid ID                                               |
| 8    | Unknown ID                                               |
| 20   | Invalid user data length                                 |
| 21   | Data queue full                                          |
| 22   | Data queue empty                                         |
| 30   | RX timeout                                               |
| 40   | Transceiver error (e.g., message not transmitted)        |
| 41   | Transceiver auto-ranging error                           |
| 42   | Transceiver PLL error                                    |
| 43   | Transceiver XTAL timeout                                 |
| 44   | Transceiver reset                                        |
| 60   | Invalid TX frequency/modulation combination              |

---

## Configuration Profiles & Payloads

The Argos SMD module supports multiple radio configurations, depending on the selected profile (LDA2, LDA2L, VLDA4, LDK).  
Each mode expects a specific uplink message format and length (payload).

### Supported Radio Configurations (`AT+RCONF=...`)

| Mode   | AT Command                                                           | Description                            |
|--------|----------------------------------------------------------------------|----------------------------------------|
| LDA2   | `AT+RCONF=44cd3a299068292a74d2126f3402610d`                         | Standard LDA2 profile (27 dBm)         |
| LDA2L  | `AT+RCONF=bd176535b394a665bd86f354c5f424fb`                         | LDA2 Low-power variant (27 dBm)        |
| VLDA4  | `AT+RCONF=efd2412f8570581457f2d982e76d44d7`                         | Very Low Data Rate (VLDA4, 22 dBm)     |
| LDK    | `AT+RCONF=41bc11b8980df01ba8b4b8f41099620b`                         | Low Duty Cycle profile (short bursts)  |

Use these commands to configure the radio mode before uplink transmissions.

---

### Typical Payloads by Configuration

Each configuration expects a message of specific length:

| Mode   | Payload Variable    | Example Payload                                          | Byte Length |
|--------|---------------------|----------------------------------------------------------|-------------|
| LDA2   | `TXpayload_LDA2`    | `cafebabe0000000000000000000000000000000000000000`       | 24 bytes    |
| LDA2L  | `TXpayload_LDA2L`   | `000000000000000000000000000000000000000000000000`       | 24 bytes    |
| LDK    | `TXpayload_LDK`     | `00000000000000000000000000000000000000`                 | 20 bytes    |
| VLDA4  | `TXpayload_VLDA4`   | `000000`                                                 | 3 bytes     |

> Note: Payloads must be provided as hexadecimal strings. The number of characters must match twice the byte length (e.g., 24 bytes → 48 hex characters).

The script allows switching between modes and injecting the correct payload accordingly.

---

## Files Included

| File Name             | Purpose                                            |
|-----------------------|----------------------------------------------------|
| `Serial-Argos-Demo.py`| Main Python script to test/configure the SMD module |
| `argos_log.txt`       | Auto-generated log of all communication events     |

---

## Next Steps / Ideas

- Export logs to `.csv` format
- Add GUI interface (Qt or web-based)
- Automatic parsing of TX_DONE and uplink timings
- REST API or BLE passthrough for remote triggering

