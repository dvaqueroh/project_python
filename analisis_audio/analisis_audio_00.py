import librosa
import numpy as np
import pretty_midi

# === CONFIGURACIÓN ===
AUDIO_FILE = "tema_IA_01.mp3"   # tu archivo de audio
MIDI_OUT   = "tema_IA_01.mid"   # salida MIDI

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

def extract_melody(y, sr):
    """Extraer la melodía aproximada usando pitch tracking"""
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

def save_midi(melody, output_file):
    """Guardar melodía como archivo MIDI"""
    midi = pretty_midi.PrettyMIDI()
    piano = pretty_midi.Instrument(program=0)  # piano

    last_time = 0
    for time, note in melody:
        if last_time != 0:
            note_obj = pretty_midi.Note(velocity=100,
                                        pitch=note,
                                        start=last_time,
                                        end=time)
            piano.notes.append(note_obj)
        last_time = time

    midi.instruments.append(piano)
    midi.write(output_file)

# === PROCESO ===
print("Cargando audio...")
y, sr = librosa.load(AUDIO_FILE, sr=44100, mono=True)

print("Estimando tonalidad...")
key = estimate_key(y, sr)
print(f"Tonalidad estimada: {key}")

print("Extrayendo melodía...")
melody = extract_melody(y, sr)

print(f"Notas extraídas: {len(melody)}")
print("Generando MIDI...")
save_midi(melody, MIDI_OUT)

print(f"¡Listo! Archivo MIDI generado: {MIDI_OUT}")
