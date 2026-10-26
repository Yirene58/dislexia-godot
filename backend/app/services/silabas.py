"""Separación en sílabas del español por reglas (no depende de la IA)."""
import unicodedata

VOCALES_FUERTES = set("aeoáéóíú")   # í y ú con tilde forman hiato
VOCALES_DEBILES = set("iuü")
VOCALES = VOCALES_FUERTES | VOCALES_DEBILES
GRUPOS_INSEPARABLES = {
    "bl", "br", "cl", "cr", "dr", "fl", "fr", "gl", "gr",
    "kl", "kr", "pl", "pr", "tr", "ch", "ll", "rr",
}


def _es_vocal(palabra, i):
    c = palabra[i]
    if c not in VOCALES:
        return False
    # la u de "que, qui, gue, gui" no suena: se trata como parte de la consonante
    if c == "u" and i > 0 and palabra[i - 1] in "qg" and i + 1 < len(palabra) and palabra[i + 1] in "eéií":
        return False
    return True


def _hay_hiato(a, b):
    if a in VOCALES_FUERTES and b in VOCALES_FUERTES:
        return True
    return a in "íú" or b in "íú"


def silabear(palabra):
    p = palabra.strip().lower()
    if not p or not p.isalpha():
        return []
    # núcleos vocálicos
    nucleos = []  # (inicio, fin) inclusive
    i = 0
    while i < len(p):
        if _es_vocal(p, i):
            ini = i
            while i + 1 < len(p) and _es_vocal(p, i + 1) and not _hay_hiato(p[i], p[i + 1]):
                i += 1
            nucleos.append((ini, i))
        i += 1
    if not nucleos:
        return [p]
    cortes = []
    for (_, fin), (ini_sig, _) in zip(nucleos, nucleos[1:]):
        cons = p[fin + 1:ini_sig]
        n = len(cons)
        if n == 0:
            corte = ini_sig
        elif n == 1:
            corte = fin + 1
        elif n == 2:
            corte = fin + 1 if cons in GRUPOS_INSEPARABLES else fin + 2
        elif n == 3:
            corte = fin + 2 if cons[1:] in GRUPOS_INSEPARABLES else fin + 3
        else:
            corte = fin + 3 if cons[2:] in GRUPOS_INSEPARABLES else fin + 4
        cortes.append(corte)
    partes, prev = [], 0
    for c in cortes:
        partes.append(p[prev:c])
        prev = c
    partes.append(p[prev:])
    return partes


# ---------------------------------------------------------------------------
# Análisis de dificultades de una palabra (para la IA adaptativa)
# ---------------------------------------------------------------------------
GRUPOS_CONSONANTICOS = GRUPOS_INSEPARABLES - {"ch", "ll", "rr"}
LETRAS_ESPEJO = set("bdpq")

NOMBRES_DIFICULTAD = {
    "grupo_consonantico": "sílabas con dos consonantes juntas (bl, br, cl, tr...)",
    "diptongo": "dos vocales juntas en la misma sílaba (ie, ue, ua...)",
    "hiato": "dos vocales seguidas que van en sílabas distintas (rí-o, le-ón)",
    "silaba_trabada": "sílabas que terminan en consonante (sol, car, pan)",
    "silaba_inversa": "sílabas que empiezan en vocal y terminan en consonante (al, es, in)",
    "letras_espejo": "letras que se confunden por su forma (b, d, p, q)",
    "palabra_larga": "palabras de 4 o más sílabas",
}


def _vocal(c):
    return c in VOCALES


def dificultades(palabra):
    """Devuelve el conjunto de dificultades que tiene una palabra."""
    p = palabra.strip().lower()
    sil = silabear(p)
    tipos = set()
    if len(sil) >= 4:
        tipos.add("palabra_larga")
    if LETRAS_ESPEJO & set(p):
        tipos.add("letras_espejo")
    for i, s in enumerate(sil):
        if s[:2] in GRUPOS_CONSONANTICOS:
            tipos.add("grupo_consonantico")
        limpia = s.replace("qu", "q").replace("gue", "ge").replace("gui", "gi")
        if any(_vocal(a) and _vocal(b) for a, b in zip(limpia, limpia[1:])):
            tipos.add("diptongo")
        if i > 0 and _vocal(sil[i - 1][-1]) and _vocal(s[0]):
            tipos.add("hiato")
        if not _vocal(s[-1]):
            if _vocal(s[0]):
                tipos.add("silaba_inversa")
            else:
                tipos.add("silaba_trabada")
    return tipos


def tipo_de_error(silabas_correctas, respuesta):
    """Compara lo que armó el niño con lo correcto (si el juego lo envía).

    Sirve tanto para respuestas completas como para respuestas cortadas en el
    momento del error (como hace el minijuego: se detiene en la sílaba errada).
    """
    if not respuesta or respuesta == silabas_correctas:
        return None
    if len(respuesta) == len(silabas_correctas) and sorted(respuesta) == sorted(silabas_correctas):
        return "orden"
    # primera sílaba donde se equivocó
    k = next((i for i, (r, c) in enumerate(zip(respuesta, silabas_correctas)) if r != c), None)
    if k is None:
        return "omision" if len(respuesta) < len(silabas_correctas) else "separacion"
    elegida, esperada = respuesta[k], silabas_correctas[k]
    if elegida == esperada[::-1]:
        return "inversion"        # te -> et, al -> la
    if elegida not in silabas_correctas:
        return "sustitucion"      # eligió una sílaba trampa (b/d, m/n...)
    return "orden"                # eligió una sílaba correcta en mal lugar


# ---------------------------------------------------------------------------
# Distractores: sílabas "trampa" con las confusiones típicas de la dislexia
# ---------------------------------------------------------------------------
CAMBIOS_ESPEJO = [
    ("b", "d"), ("d", "b"), ("p", "b"), ("b", "p"), ("m", "n"), ("n", "m"),
    ("t", "d"), ("d", "t"), ("s", "z"), ("z", "s"),
    ("l", "r"), ("r", "l"), ("f", "v"), ("ll", "y"),
]


def _variantes(silaba):
    """Sílabas parecidas: letras espejo/sonido parecido e inversiones (te -> et)."""
    res = []
    for a, b in CAMBIOS_ESPEJO:
        if a in silaba:
            res.append(silaba.replace(a, b, 1))
    if len(silaba) == 2 and silaba[0] not in VOCALES and silaba[1] in VOCALES:
        res.append(silaba[::-1])  # inversión: te -> et
    if len(silaba) == 2 and silaba[0] in VOCALES and silaba[1] not in VOCALES:
        res.append(silaba[::-1])  # inversión: al -> la
    return res


def opciones_con_distractores(silabas, extra=2, rng=None, dificultad=None):
    """Devuelve las sílabas correctas + distractores, todo mezclado.

    Si se pasa "dificultad" (RF4), manda sobre "extra":
      1 -> 1 distractor muy distinto (fácil)
      2 -> 2 distractores, uno parecido (b/d, inversión...)
      3 -> 3 distractores, todos parecidos (difícil)
    """
    import random as _random
    rng = rng or _random
    correctas = set(silabas)
    parecidos = []
    for s in silabas:
        for v in _variantes(s):
            mismas_vocales = sum(c in VOCALES for c in v) == sum(c in VOCALES for c in s)
            if v not in correctas and v not in parecidos and v.isalpha() and mismas_vocales:
                parecidos.append(v)
    rng.shuffle(parecidos)
    relleno = ["ma", "pa", "la", "sa", "ta", "no", "mi", "lo", "fe", "ru", "ca", "ve"]
    relleno = [r for r in relleno if r not in correctas and r not in parecidos]
    rng.shuffle(relleno)

    if dificultad is None:
        cuantos_parecidos, total = extra, extra
    else:
        dificultad = max(1, min(3, int(dificultad)))
        total = dificultad
        cuantos_parecidos = {1: 0, 2: 1, 3: 3}[dificultad]

    elegidos = parecidos[:cuantos_parecidos]
    for r in parecidos[cuantos_parecidos:] if dificultad is None else []:
        if len(elegidos) >= total:
            break
        elegidos.append(r)
    for r in relleno:
        if len(elegidos) >= total:
            break
        elegidos.append(r)
    opciones = list(silabas) + elegidos
    rng.shuffle(opciones)
    return opciones
