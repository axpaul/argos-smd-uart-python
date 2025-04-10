# Python Demonstrator – Arribada Argos SMD Module

## Acknowledgements

This demonstrator was developed at the **CNES (Centre National d'Études Spatiales)** – the French Space Agency – as part of internal testing and prototyping activities involving the **Arribada Argos SMD module**.

Although developed within CNES, this project is released as **open source** for the benefit of the scientific, maker, and educational communities.  
Feel free to contribute, adapt, and extend it.

> © 2025 CNES – Open source under GPL-3.0 license.

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

This project uses the **FTDI TTL-232RG-VREG3V3-WE** USB-to-UART cable to interface with the Arribada Argos SMD Wing module.

- Provides a direct UART interface over USB
- Operates at **3.3V logic level** (TTL)
- Can supply up to **250 mA on VCC**
- Includes integrated USB-to-Serial chip (FT232R)
- Compatible with all major platforms (Windows, macOS, Linux)

![FTDI Wiring](https://github.com/axpaul/argos-smd-uart-python/blob/main/Image/Synoptique.png)

| Arribada Wing Pin | FTDI Cable Wire           | Description                      |
|-------------------|---------------------------|----------------------------------|
| `3V3`             | VCC (red)                 | Power supply (3.3V)              |
| `TX`              | RX (yellow)               | UART TX (Wing → PC)    |
| `RX`              | TX (orange)               | UART RX (PC → Wing)       |
| `GND`             | GND (black)               | Ground / common reference        |

> **Important:** Always verify voltage compatibility. This version provides 3.3V logic and power. Do not connect to 5V devices.

You can find the complete technical documentation from FTDI here:  
[FTDI TTL-232RG Cables – Datasheet (PDF)](https://www.ftdichip.com/Support/Documents/DataSheets/Cables/DS_TTL-232RG_CABLES.pdf)

---

## Script Features (`Serial-Argos-Demo.py`)

- Automatic UART initialization
- Radio configuration (e.g. LDA2 mode)
- Periodic Argos uplink transmission (every 60 seconds)
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

The Argos SMD module supports multiple radio configurations, depending on the selected profile (LDA2, VLDA4, LDK).  
Each mode expects a specific uplink message format and length (payload).

### Supported Radio Configurations (`AT+RCONF=...`)

| Mode   | AT Command                                                           | Description                            |
|--------|----------------------------------------------------------------------|----------------------------------------|
| LDA2   | `AT+RCONF=3d678af16b5a572078f3dbc95a1104e7`                         | Standard LDA2 profile (27 dBm)         |
| VLDA4  | `AT+RCONF=03921fb104b92859209b18abd009de96`                         | Very Low Data Rate (VLDA4, 22 dBm)     |
| LDK    | `AT+RCONF=550b4bec21009c7a7b5bebaa937cdb41`                         | Low Duty Cycle profile (short bursts)  |

Use these commands to configure the radio mode before uplink transmissions.

---

### Typical Payloads by Configuration

Each configuration expects a message of specific length:

| Mode   | Payload Variable    | Example Payload                                          | Byte Length |
|--------|---------------------|----------------------------------------------------------|-------------|
| LDA2   | `TXpayload_LDA2`    | `cafebabe0000000000000000000000000000000000000000`       | 24 bytes    |
| LDK    | `TXpayload_LDK`     | `00000000000000000000000000000000000000`                 | 16 bytes    |
| VLDA4  | `TXpayload_VLDA4`   | `000000`                                                 | 3 bytes     |

> Note: Payloads must be provided as hexadecimal strings. The number of characters must match twice the byte length (e.g., 24 bytes → 48 hex characters).

The script allows switching between modes and injecting the correct payload accordingly.

---

## Files Included

| File Name             | Purpose                                            |
|-----------------------|----------------------------------------------------|
| `Serial-Argos-Demo.py`| Main Python script to test/configure the SMD module |
| `argos_log.txt`       | Auto-generated log of all communication events     |
| `Serial-Argos-Test-All-AT.py`| Main Python script to test all command |
| `argos_log_test_command.txt`       | Auto-generated log of test communication events     |

---

## Next Steps / Ideas

- Export logs to `.csv` format
- Add GUI interface (Qt or web-based)
- Automatic parsing of TX_DONE and uplink timings
- REST API or BLE passthrough for remote triggering

## References & Resources

- **Arribada Initiative** – Official site  
  https://arribada.org

- **Official Argos SMD Arduino Demo** – by Arribada  
  The full Arduino-based demonstration for the Argos SMD module is available on GitHub:  
  https://github.com/arribada/argos-smd-test-arduino

This Python project offers a minimal command-line alternative to the Arduino-based demo, using direct serial AT commands and USB–UART connection.


