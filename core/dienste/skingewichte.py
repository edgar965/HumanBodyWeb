# -*- coding: utf-8 -*-
"""Skingewichte — Knochengewichte des Basisnetzes, geladen und aufbereitet.

WARUM EINE KLASSE (Umbau 15.08.2026): `_get_base_skin_weights` und
`_get_base_skin_arrays` lagen mit drei `global`-Zwischenspeichern in
character_api.py und wurden von zwei Themen gebraucht (Netz UND SMPL). Beim
thematischen Schnitt waeren sie entweder doppelt entstanden oder in einem Modul
gelandet, das ein anderes importieren muss — beides falsch. Sie gehoeren
zusammen: laden, Nicht-DEF-Knochen ausfiltern, in kompakte Vierer-Felder
umrechnen, zwischenspeichern.

Die Zwischenspeicher sind Klassenattribute: eine Datenlage je Prozess.
"""
import json
import logging
import os

import numpy as np
from django.conf import settings

logger = logging.getLogger('core')


class Skingewichte:
    """Gewichte des Basisnetzes je Geschlecht — geladen, gefiltert, kompakt."""

    _basis = {}            # {'female': {...}, 'male': {...}}
    _arrays = {}           # {'female': (indices, weights)}
    _propagiert_json = {}  # {'female': '…'} — fertig kodiert, siehe propagiert_json

    #: So viele Knochen wirken hoechstens auf einen Vertex (Three.js-Grenze).
    EINFLUESSE = 4

    # ------------------------------------------------------------------ Pfade

    @staticmethod
    def _datenverzeichnis(geschlecht):
        pfad = str(settings.HUMANBODY_DATA_DIR)
        return pfad + '_male' if geschlecht == 'male' else pfad

    # ------------------------------------------------------------------ laden

    @classmethod
    def basis(cls, geschlecht='female'):
        """Rohgewichte aus `skin_weights_base.json`, ohne Nicht-DEF-Knochen."""
        if geschlecht in cls._basis:
            return cls._basis[geschlecht]
        verzeichnis = cls._datenverzeichnis(geschlecht)
        pfad = os.path.join(verzeichnis, 'skin_weights_base.json')
        if not os.path.isfile(pfad):
            return None
        with open(pfad, 'r', encoding='utf-8') as f:
            daten = json.load(f)
        cls._nicht_def_entfernen(daten, verzeichnis, geschlecht)
        cls._basis[geschlecht] = daten
        return daten

    @classmethod
    def _nicht_def_entfernen(cls, daten, verzeichnis, geschlecht):
        """Knochen wegwerfen, die es im DEF-Skelett nicht gibt.

        Der Browser bekommt das DEF-Skelett; bliebe ein fremder Knochen in der
        Liste, zeigten alle Indizes dahinter auf den falschen Knochen."""
        skelettpfad = os.path.join(verzeichnis, 'def_skeleton.json')
        if not os.path.isfile(skelettpfad):
            return
        with open(skelettpfad, 'r', encoding='utf-8') as f:
            skelett = json.load(f)
        erlaubt = {b['name'] for b in skelett['bones']}
        alte_namen = daten['bone_names']
        weg = {i for i, n in enumerate(alte_namen) if n not in erlaubt}
        if not weg:
            return
        umnummerierung = cls._umnummerierung(len(alte_namen), weg)
        daten['bone_names'] = [n for i, n in enumerate(alte_namen) if i not in weg]
        daten['weights'] = [cls._paare_umnummerieren(paare, umnummerierung, weg)
                            for paare in daten['weights']]
        logger.info('Basisgewichte (%s): %d Nicht-DEF-Knochen entfernt',
                    geschlecht, len(weg))

    @staticmethod
    def _umnummerierung(anzahl, weg):
        """{alter Index: neuer Index} nach dem Streichen von `weg`.

        Der Browser bekommt die verbleibenden Knochen LUECKENLOS durchgezaehlt.
        Ohne die Verschiebung zeigte jeder Index hinter einer gestrichenen
        Stelle auf den falschen Knochen — und zwar erst in Bewegung sichtbar.
        """
        umnummerierung, neu = {}, 0
        for alt in range(anzahl):
            if alt not in weg:
                umnummerierung[alt] = neu
                neu += 1
        return umnummerierung

    @staticmethod
    def _paare_umnummerieren(paare, umnummerierung, weg):
        gefiltert = [(umnummerierung[bi], w) for bi, w in paare
                     if bi not in weg and bi in umnummerierung]
        summe = sum(w for _, w in gefiltert)
        if summe > 0 and abs(summe - 1.0) > 1e-6:
            gefiltert = [(bi, w / summe) for bi, w in gefiltert]
        return gefiltert

    # -------------------------------------------------------------- aufbereiten

    @classmethod
    def arrays(cls, geschlecht='female'):
        """(indices, weights) als (N, 4)-Felder — fuer die Nachbarsuche.

        Die Felder sind SCHREIBGESCHUETZT: Sie liegen im Zwischenspeicher und
        werden von jeder folgenden Anfrage benutzt, auch gleichzeitig. Heute
        liest jede Aufrufstelle ueber Fancy-Indexing (das kopiert); das Flag
        kostet nichts und macht aus einem kuenftigen `indices[0, 0] = 99` einen
        sofortigen Fehler statt vergifteter Gewichte fuer alle weiteren
        Anfragen (Review 13.08.2026)."""
        if geschlecht in cls._arrays:
            return cls._arrays[geschlecht]
        gewichte = cls.basis(geschlecht)
        if gewichte is None:
            return None
        indices, werte = cls._vierer_felder(gewichte)
        indices.flags.writeable = False
        werte.flags.writeable = False
        cls._arrays[geschlecht] = (indices, werte)
        logger.info('Basisgewichte (%s) aufbereitet: %d Vertices, %d Einfluesse',
                    geschlecht, len(indices), cls.EINFLUESSE)
        return cls._arrays[geschlecht]

    @classmethod
    def _vierer_felder(cls, gewichte):
        anzahl = gewichte['vertex_count']
        k = cls.EINFLUESSE
        indices = np.zeros((anzahl, k), dtype=np.float32)
        werte = np.zeros((anzahl, k), dtype=np.float32)
        for v in range(anzahl):
            paare = gewichte['weights'][v]
            if not paare:
                continue
            staerkste = sorted(paare, key=lambda p: p[1], reverse=True)[:k]
            summe = sum(w for _, w in staerkste) or 1.0
            for j, (knochen, w) in enumerate(staerkste):
                indices[v, j] = knochen
                werte[v, j] = w / summe
        return indices, werte

    # ------------------------------------------------------------ propagiert

    @classmethod
    def propagiert_json(cls, geschlecht, unterteiler):
        """Die propagierten Gewichte als fertige JSON-Zeichenkette.

        PERFORMANCE 16.08.2026: `/api/character/skin-weights/` brauchte 148 ms,
        davon 144 ms allein in `json.encoder.iterencode` — die Antwort ist
        2,8 MB gross. Gerechnet wurde dabei nichts: das Ergebnis lag schon im
        Zwischenspeicher, nur eben als Python-Objekt, das jede Anfrage neu
        kodierte. Gespeichert wird deshalb die ZEICHENKETTE. Das spart auch
        Arbeitsspeicher: 70.851 Python-Listen mit Paaren wiegen ein Vielfaches
        ihrer Textform.

        Kompakte Trennzeichen: `json.dumps` setzt sonst hinter jedes Komma ein
        Leerzeichen, was bei dieser Menge an Zahlen mehrere hundert Kilobyte
        reines Fuellzeichen sind.
        """
        if geschlecht in cls._propagiert_json:
            return cls._propagiert_json[geschlecht]
        daten = cls._propagieren(geschlecht, unterteiler)
        if daten is None:
            return None
        cls._propagiert_json[geschlecht] = json.dumps(daten, separators=(',', ':'))
        return cls._propagiert_json[geschlecht]

    @classmethod
    def _propagieren(cls, geschlecht, unterteiler):
        basis = cls.basis(geschlecht)
        if basis is not None and unterteiler is not None:
            logger.info('Gewichte (%s) durch die Unterteilung reichen: '
                        '%d Basis- -> %d Untervertices',
                        geschlecht, basis['vertex_count'],
                        unterteiler.sub_vertex_count)
            return unterteiler.propagate_skin_weights(
                basis['weights'], basis['bone_names'])
        return cls._notfassung(geschlecht)

    @classmethod
    def _notfassung(cls, geschlecht):
        """`skin_weights.json` unveraendert — Reihenfolge passt womoeglich nicht.

        Greift nur, wenn `skin_weights_base.json` fehlt oder es keinen
        Unterteiler gibt. Die Vertexreihenfolge stimmt dann nicht mit dem
        unterteilten Netz ueberein, deshalb die Fehlermeldung im Log.
        """
        pfad = os.path.join(cls._datenverzeichnis(geschlecht), 'skin_weights.json')
        if not os.path.isfile(pfad):
            return None
        with open(pfad, 'r', encoding='utf-8') as f:
            daten = json.load(f)
        logger.error('Rohe skin_weights.json fuer %s benutzt — die '
                     'Vertexreihenfolge passt moeglicherweise nicht zur '
                     'Catmull-Clark-Unterteilung!', geschlecht)
        return daten
