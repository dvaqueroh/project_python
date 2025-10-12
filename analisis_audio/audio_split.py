import librosa
import numpy as np
import pretty_midi
import os
import subprocess

# === CONFIGURACIÓN ===
# RUTA C:\Users\HP\separated\htdemucs\separated\htdemucs
AUDIO_FILE = "Decrepit.mp3" # fichero audio
OUTPUT_DIR = "separated"  # carpeta donde Demucs genera resultados

# === FUNCIONES ===


# === PROCESO ===
print("Separando pistas con Demucs...")
subprocess.run(f"demucs {AUDIO_FILE}", shell=True)

# Mapear instrumentos de Demucs -> General MIDI
stems = {
    "vocals.wav": {"program": 52, "name": "Voz"},        # Voice
    "drums.wav":  {"program": 0,  "name": "Bateria"},    # Acoustic Grand Piano (nota: MIDI drums van en canal 10, pero lo simplificamos)
    "bass.wav":   {"program": 32, "name": "Bajo"},       # Bass
    "guitar.wav": {"program": 25, "name": "Guitarra"},   # Guitar
}

# Carpeta que genera Demucs
song_name = os.path.splitext(os.path.basename(AUDIO_FILE))[0]
demucs_folder = os.path.join("separated", "htdemucs", song_name)
