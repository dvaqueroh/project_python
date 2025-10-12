import librosa
import numpy as np
import pretty_midi
import os
import subprocess

# === CONFIGURACIÓN ===
AUDIO_FILE = "Uncontrollable.mp3" # fichero audio
OUTPUT_DIR = "separated"  # carpeta donde Demucs genera resultados

# === FUNCIONES ===
def estimate_key(y, sr):
    """Estimar la tonalidad usando cromagrama y perfiles de Krumhansl"""
    major_profile = np.array([6.35, 2.23, 3.48, 2.33, 4.38,
                              4.09, 2.52, 5.19, 2.39, 3.66,
                              2.29, 2.88])
    minor_profile = np.array([6.33, 2.68, 3.52, 5.38, 2.60,
                              3.53, 2.54, 4.75, 3.98, 2.69,
                              3.34, 3.17])
    chroma = librosa.feature.chroma_cqt(y=y, sr=sr)
    chroma_mean = np.mean(chroma, axis=1)
    notes = ['C', 'C#', 'D', 'D#', 'E', 'F',
             'F#', 'G', 'G#', 'A', 'A#', 'B']

    tonalidades = []
    for i in range(12):
        corr_major = np.corrcoef(chroma_mean, np.roll(major_profile, i))[0, 1]
        corr_minor = np.corrcoef(chroma_mean, np.roll(minor_profile, i))[0, 1]
        tonalidades.append((notes[i] + " mayor", corr_major))
        tonalidades.append((notes[i] + " menor", corr_minor))

    return max(tonalidades, key=lambda x: x[1])[0]

def detect_tempo(y, sr):
    tempo, _ = librosa.beat.beat_track(y=y, sr=sr)
    # Asegurar que tempo sea escalar
    if isinstance(tempo, (list, np.ndarray)):
        tempo = tempo[0] if len(tempo) > 0 else 120.0
    return round(float(tempo))

def extract_melody(y, sr):
    pitches, magnitudes = librosa.piptrack(y=y, sr=sr)
    melody = []
    times = librosa.frames_to_time(np.arange(pitches.shape[1]), sr=sr)
    for t, pitch_col in enumerate(pitches.T):
        index = pitch_col.argmax()
        pitch = pitch_col[index]
        if pitch > 0:
            note = librosa.hz_to_midi(pitch)
            melody.append((times[t], int(round(note))))
    return melody

def save_track_as_midi(melody, program, track_name, tempo, filename):
    midi = pretty_midi.PrettyMIDI(initial_tempo=tempo)
    instrument = pretty_midi.Instrument(program=program, name=track_name)
    last_time = 0
    for time, note in melody:
        if last_time != 0:
            note_obj = pretty_midi.Note(velocity=100,
                                        pitch=note,
                                        start=last_time,
                                        end=time)
            instrument.notes.append(note_obj)
        last_time = time
    midi.instruments.append(instrument)
    midi.write(filename)

# === PROCESO ===
print("Separando pistas con Demucs...")
subprocess.run(f"demucs {AUDIO_FILE}", shell=True)

# Mapear instrumentos de Demucs -> General MIDI
stems = {
    "vocals.wav": {"program": 52, "name": "Voz"},       # Choir
    "drums.wav":  {"program": 0,  "name": "Bateria"},   # Acoustic Grand Piano (nota: MIDI drums van en canal 10, pero lo simplificamos)
    "bass.wav":   {"program": 32, "name": "Bajo"},      # Bass
    "other.wav":  {"program": 25, "name": "Guitarra"},  # Guitar
}

# Carpeta que genera Demucs
song_name = os.path.splitext(os.path.basename(AUDIO_FILE))[0]
demucs_folder = os.path.join("separated", "htdemucs", song_name)

# Procesar cada instrumento y generar un MIDI
for stem_file, info in stems.items():
    path = os.path.join(demucs_folder, stem_file)
    if not os.path.exists(path):
        print(f"No encontrado: {path}, se omite.")
        continue

    print(f"\nProcesando {info['name']}...")

    # Cargar audio del stem
    y, sr = librosa.load(path, sr=44100, mono=True)

    # Analizar tonalidad y tempo
    key = estimate_key(y, sr)
    tempo = detect_tempo(y, sr)
    print(f" - Tonalidad: {key}, Tempo: {tempo} BPM")

    # Extraer melodía
    melody = extract_melody(y, sr)

    # Guardar cada instrumento como MIDI independiente
    midi_filename = f"{song_name}_{info['name']}.mid"
    save_track_as_midi(melody, info["program"], info["name"], tempo, midi_filename)
    print(f"   ✅ MIDI generado: {midi_filename}")
