import csv
import re
from pathlib import Path

import fitz  # PyMuPDF


CARPETA_SCRIPT = Path(__file__).resolve().parent

PDF_EXAMEN = CARPETA_SCRIPT / "Cuestionario_TAI-L-ModeloA.pdf"
PDF_PLANTILLA = CARPETA_SCRIPT / "Plantilla_respuestas_TAI-L-ModeloA.pdf"
ARCHIVO_SALIDA = CARPETA_SCRIPT / "mazo_anki_examen_A.csv"

# Importar csv en ANKI para tipo de notas MCQ Ultimate V2.1 

def extraer_texto(pdf_path: Path) -> str:
    """Extrae el texto de todas las páginas de un PDF."""
    if not pdf_path.exists():
        raise FileNotFoundError(f"No se encontró el archivo: {pdf_path}")

    with fitz.open(pdf_path) as documento:
        return "\n".join(pagina.get_text("text") for pagina in documento)


def normalizar(texto: str) -> str:
    """Normaliza saltos y espacios para facilitar el análisis."""
    texto = texto.replace("\u00a0", " ")
    texto = texto.replace("\r", "\n")
    texto = re.sub(r"[ \t]+", " ", texto)
    return texto


def extraer_respuestas(texto: str) -> dict[str, dict[int, str]]:
    texto = normalizar(texto)

    bloques = {}
    bloque_actual = "Primera parte"
    posicion_inicio = 0

    # Delimita las secciones de la plantilla según sus encabezados.
    encabezados = list(re.finditer(
        r"Primera parte|Preguntas de reserva|Supuesto I|Supuesto II",
        texto,
        re.IGNORECASE,
    ))

    for i, encabezado in enumerate(encabezados):
        fin = encabezados[i + 1].start() if i + 1 < len(encabezados) else len(texto)
        nombre = encabezado.group(0).lower()

        if nombre == "primera parte":
            bloque_actual = "Primera parte"
        elif nombre == "supuesto i":
            bloque_actual = "Supuesto I"
        elif nombre == "supuesto ii":
            bloque_actual = "Supuesto II"
        elif nombre == "preguntas de reserva":
            # La reserva pertenece al bloque de supuesto que aparece antes;
            # si no hay ninguno, corresponde a la primera parte.
            antes = texto[:encabezado.start()].upper()
            if "SUPUESTO II" in antes:
                bloque_actual = "Supuesto II - Reserva"
            elif "SUPUESTO I" in antes:
                bloque_actual = "Supuesto I - Reserva"
            else:
                bloque_actual = "Primera parte - Reserva"

        # Extrae todas las respuestas dentro del tramo de esta sección.
        tramo = texto[encabezado.start():fin]
        pares = re.findall(r"(?<!\d)(\d{1,2})\s*[.)]\s*([a-d])\b", tramo, re.I)

        if pares:
            mapa = bloques.setdefault(bloque_actual, {})
            for numero, letra in pares:
                mapa[int(numero)] = letra.lower()

    return bloques



def detectar_bloque_pregunta(texto: str, posicion: int, bloque_actual: str) -> str:
    """Determina el bloque al que pertenece una pregunta según los encabezados cercanos."""
    encabezados = [
        (m.start(), m.group(0).strip())
        for m in re.finditer(
            r"Primera parte|Preguntas de reserva|SUPUESTO I|SUPUESTO II",
            texto,
            re.IGNORECASE,
        )
        if m.start() < posicion
    ]

    if not encabezados:
        return bloque_actual

    encabezado = encabezados[-1][1].lower()

    if "supuesto i" in encabezado:
        return "Supuesto I"
    if "supuesto ii" in encabezado:
        return "Supuesto II"
    if "reserva" in encabezado:
        # Distingue reservas de la primera parte y de los supuestos.
        if "SUPUESTO I" in texto[:posicion].upper():
            if "SUPUESTO II" in texto[:posicion].upper():
                return "Supuesto II - Reserva"
            return "Supuesto I - Reserva"
        return "Primera parte - Reserva"

    return "Primera parte"


def extraer_preguntas(texto: str) -> list[dict]:
    """
    Divide el examen en preguntas numeradas y extrae las opciones a), b), c), d).
    La numeración se reinicia en cada bloque.
    """
    texto = normalizar(texto)

    # El número de pregunta debe estar al inicio de una línea.
    inicios = list(re.finditer(r"(?m)^\s*(\d{1,2})\.\s+", texto))
    preguntas = []

    for i, inicio in enumerate(inicios):
        fin = inicios[i + 1].start() if i + 1 < len(inicios) else len(texto)
        fragmento = texto[inicio.start():fin].strip()
        numero = int(inicio.group(1))
        bloque = detectar_bloque_pregunta(texto, inicio.start(), "Primera parte")

        # Retira el número inicial.
        contenido = re.sub(r"^\s*\d{1,2}\.\s+", "", fragmento, count=1)

        # Elimina pies de página frecuentes.
        contenido = re.sub(
            r"\s*2025\s*-\s*TAI-L.*?(?=\n|$)",
            " ",
            contenido,
            flags=re.IGNORECASE,
        )

        # Busca las opciones a), b), c) y d).
        opciones_encontradas = list(
            re.finditer(r"(?<!\w)([a-d])\)\s*", contenido, re.IGNORECASE)
        )

        #    continue
        
        if len(opciones_encontradas) < 4:
            print(
                f"\nNo se pudieron extraer las 4 opciones "
                f"de la pregunta {numero} ({bloque})."
            )
            print("Texto extraído:", repr(contenido[:500]))
            continue

        enunciado = contenido[:opciones_encontradas[0].start()].strip()
        opciones = {}

        for j, opcion_match in enumerate(opciones_encontradas):
            letra = opcion_match.group(1).lower()
            inicio_opcion = opcion_match.end()
            fin_opcion = (
                opciones_encontradas[j + 1].start()
                if j + 1 < len(opciones_encontradas)
                else len(contenido)
            )
            opciones[letra] = contenido[inicio_opcion:fin_opcion].strip()

        if all(letra in opciones for letra in "abcd"):
            preguntas.append({
                "bloque": bloque,
                "numero": numero,
                "enunciado": limpiar_texto(enunciado),
                "opciones": opciones,
            })

    return preguntas


def limpiar_texto(texto: str) -> str:
    texto = re.sub(r"\s+", " ", texto)
    return texto.strip()


def buscar_respuesta(bloque: str, numero: int, respuestas: dict) -> str | None:
    """Busca la respuesta en el bloque correspondiente, con alternativas de nombre."""
    candidatos = [bloque]

    # Algunos encabezados se extraen con mayúsculas o con pequeñas variaciones.
    if "Reserva" in bloque:
        candidatos.append("Primera parte - Reserva")
        candidatos.append("Supuesto I - Reserva")
        candidatos.append("Supuesto II - Reserva")

    for nombre in candidatos:
        if nombre in respuestas and numero in respuestas[nombre]:
            return respuestas[nombre][numero]

    return None


def main():
    texto_examen = extraer_texto(PDF_EXAMEN)
    texto_plantilla = extraer_texto(PDF_PLANTILLA)

    respuestas = extraer_respuestas(normalizar(texto_plantilla))
    preguntas = extraer_preguntas(texto_examen)

    tarjetas = []
    sin_respuesta = []

    for pregunta in preguntas:
        letra_correcta = buscar_respuesta(
            pregunta["bloque"],
            pregunta["numero"],
            respuestas,
        )

        # Intenta resolver bloques de reserva cuyo título se haya detectado de otra forma.
        if letra_correcta is None and "Reserva" in pregunta["bloque"]:
            for bloque_reserva, mapa in respuestas.items():
                if "Reserva" in bloque_reserva and pregunta["numero"] in mapa:
                    letra_correcta = mapa[pregunta["numero"]]
                    break

        if letra_correcta not in pregunta["opciones"]:
            sin_respuesta.append(
                f'{pregunta["bloque"]}, pregunta {pregunta["numero"]}'
            )
            continue

        enunciado_tarjeta = (
            f'{pregunta["bloque"]} — Pregunta {pregunta["numero"]}<br>'
            f'{pregunta["enunciado"]}'
        )

        tarjetas.append([
            enunciado_tarjeta,
            pregunta["opciones"]["a"],
            pregunta["opciones"]["b"],
            pregunta["opciones"]["c"],
            pregunta["opciones"]["d"],
            letra_correcta.upper(),
        ])

        # La respuesta correcta debe ser solo la letra: A, B, C o D.
        respuesta_correcta = letra_correcta.upper()

        
    with ARCHIVO_SALIDA.open("w", newline="", encoding="utf-8-sig") as archivo:
        escritor = csv.writer(archivo, delimiter=";")
        escritor.writerow([
            "Question",
            "option_1 (A)",
            "option_2 (B)",
            "option_3 (C)",
            "option_4 (D)",
            "Ans",
        ])
        escritor.writerows(tarjetas)    

    print(f"Tarjetas creadas: {len(tarjetas)}")
    print(f"Archivo generado: {ARCHIVO_SALIDA.resolve()}")

    if sin_respuesta:
        print("\nPreguntas que no encontraron respuesta en la plantilla:")
        for item in sin_respuesta:
            print(f" - {item}")

    if not preguntas:
        print(
            "\nNo se pudieron extraer preguntas. "
            "Comprueba que el PDF permite seleccionar/copiar texto."
        )
        
    Path("texto_extraido.txt").write_text(texto_examen, encoding="utf-8")    


if __name__ == "__main__":
    main()
