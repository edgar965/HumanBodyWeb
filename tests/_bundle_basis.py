# -*- coding: utf-8 -*-
"""Beiwerk der Bundle-Tests: Multipart-Upload, Abruf und drei Kunstdateien.

Fuehrender Unterstrich mit Absicht: `testaufbau` erkennt daran, dass das keine
Testdatei ist. Aus `scene_object_bundle_tests.py` herausgeloest (17.08.2026,
416 Zeilen).

Die drei Kunstdateien (`OBJ`, `MTL`, `PNG`) sind absichtlich winzig und
trotzdem gueltig: Ein OBJ mit `mtllib`-Verweis, ein MTL mit `map_Kd`-Verweis
und ein 1x1-PNG. Damit laesst sich die ganze Kette OBJ -> MTL -> PNG pruefen,
ohne ein echtes Modell hochzuladen.

UMBAU 27.08.2026 (Befund `freie-funktionen`): Die beiden Sende-Funktionen
stehen jetzt als `Bundelruf`; die Kunstdateien sind Klassenfelder daneben.
"""

# `json`, `urllib` und `BASE_URL` sind mit dem 28.08.2026 entfallen: Der
# Upload geht jetzt durch den Kanal, und der kennt beides.
import re

from .kanal import Kanal

# EINE Adresse für alle Tests. Hier stand eine zweite Kopie mit `localhost` —
# die kostete 2 s je Anfrage. Sie kommt aus `kanal.py`, wo auch der Netzkanal
# sie liest; `base.py` reicht sie nicht mehr durch (Befund `tote-importe`,
# 18.08.2026 — und dieser Import hier war der Beleg, dass sie doch gebraucht
# wird: der Testlauf brach danach mit ImportError ab).
#
# BIS ZUM 28.08.2026 SCHICKTE DIESE DATEI SELBST und nicht über `Kanal`. Der
# Satz „Im in-process-Lauf greift sie damit ins Netz“ stand hier als
# Feststellung — er war die Fehlerbeschreibung: Die Fälle brauchten einen
# laufenden Dev-Server, kippten bei Nebenlast um und schrieben in die echten
# Mediendaten. Jetzt entscheidet der Kanal.


class Bundelruf:
    """Multipart-Upload und Abruf — DURCH den Kanal.

    BIS ZUM 28.08.2026 GING DAS AM KANAL VORBEI: `urllib` an
    `127.0.0.1:8081`, also an den laufenden Dev-Server. Das hat dreimal einen
    Fehlschlag erzeugt, der beim naechsten Lauf verschwand („Upload HTTP:
    0/0") — reproduzierbar erst, als die Testsuite waehrend laufender
    Browser-Proben gestartet wurde. Dazu schrieben die Faelle in die ECHTEN
    Mediendaten statt in die des Laufs.

    Jetzt entscheidet der Kanal: im Testlauf in-process ueber
    `django.test.Client` (Testdatenbank, eigener Medienordner), ausserhalb
    weiter ueber das Netz.
    """

    #: Wie lange auf eine Antwort gewartet wird.
    FRIST_UPLOAD_S = 15
    FRIST_ABRUF_S = 10

    @classmethod
    def hochladen(cls, pfad, felder):
        """Sendet ein Multipart-Formular.

        `felder` = [(name, dateiname|None, inhalt, inhaltstyp)];
        `dateiname=None` -> normales Textfeld, sonst Datei.
        Rueckgabe: `(Status, JSON oder {'_raw': Text})`.
        """
        return Kanal.aktueller().senden(pfad, method='POST', files=list(felder),
                                        timeout=cls.FRIST_UPLOAD_S)

    @classmethod
    def abrufen(cls, adresse):
        """Laedt den Inhalt einer Adresse als Bytes."""
        return Kanal.aktueller().rohabruf(adresse, timeout=cls.FRIST_ABRUF_S)


class Mtlbezug:
    """Die `map_Kd`-Zeile einer MTL lesen — wie der Parser der Anwendung.

    BEFUND (30.08.2026): Dieselbe Auswertung stand in DREI Tests
    (`bundle_mtl_tests` zweimal, `bundle_upload_tests` einmal), jedes Mal als
    dieselbe Kette aus regulaerem Ausdruck, Optionsfilter und
    Pfad-Normalisierung. Zwei der drei Faelle lagen deshalb bei Rang C —
    elf und vierzehn Verzweigungen in einer Testmethode.

    Nachgebaut ist die Logik aus `scene_extras.js`. Wer sie hier anders
    schreibt als dort, prueft etwas, das die Anwendung nie tut.
    """

    #: `map_Kd` steht am Zeilenanfang; der Rest der Zeile ist die Angabe.
    ZEILE = re.compile(r'^\s*map_Kd\s+(.+?)\s*$',
                       re.IGNORECASE | re.MULTILINE)

    @classmethod
    def aus_text(cls, mtl_text):
        """(rohe Angabe, Wortteile ohne Optionen) — oder (`''`, [])."""
        treffer = cls.ZEILE.search(mtl_text)
        if not treffer:
            return '', []
        angabe = treffer.group(1).strip()
        # Optionen wie `-s 1 1` oder `-o 0 0 0` stehen VOR dem Dateinamen.
        return angabe, [w for w in angabe.split()
                        if w and not w.startswith('-')]

    @classmethod
    def aus_adresse(cls, adresse):
        """Dieselbe Auswertung, aber die MTL wird erst geladen."""
        _status, roh = Bundelruf.abrufen(adresse)
        return cls.aus_text(roh.decode('utf-8', errors='ignore'))

    @staticmethod
    def dateiname(rohangabe, wortteile):
        """Der reine Dateiname: Backslashes, `./` und Unterpfade weg."""
        angabe = wortteile[-1] if wortteile else rohangabe
        return angabe.replace('\\', '/').lstrip('./').split('/')[-1]


# Synthetische Test-Dateien — minimal, aber syntaktisch gültig. Sie bleiben
# Modulkonstanten: Das sind DATEN, kein Verhalten.
_OBJ_CONTENT = b"""# Bundle-Test OBJ
mtllib bundle_test.mtl
v 0.0 0.0 0.0
v 1.0 0.0 0.0
v 0.0 1.0 0.0
vt 0.0 0.0
vt 1.0 0.0
vt 0.0 1.0
usemtl Mat01
f 1/1 2/2 3/3
"""

_MTL_CONTENT = b"""# Bundle-Test MTL
newmtl Mat01
Kd 0.8 0.8 0.8
map_Kd bundle_tex.png
"""

# 1x1 PNG (rot) — minimales gültiges PNG
_PNG_CONTENT = bytes([
    0x89, 0x50, 0x4E, 0x47, 0x0D, 0x0A, 0x1A, 0x0A,  # PNG signature
    0x00, 0x00, 0x00, 0x0D, 0x49, 0x48, 0x44, 0x52,  # IHDR chunk
    0x00, 0x00, 0x00, 0x01, 0x00, 0x00, 0x00, 0x01,  # 1x1
    0x08, 0x02, 0x00, 0x00, 0x00, 0x90, 0x77, 0x53,
    0xDE, 0x00, 0x00, 0x00, 0x0C, 0x49, 0x44, 0x41,
    0x54, 0x08, 0x99, 0x63, 0xF8, 0xCF, 0xC0, 0x00,
    0x00, 0x00, 0x03, 0x00, 0x01, 0x5B, 0xFC, 0x2A,
    0x73, 0x00, 0x00, 0x00, 0x00, 0x49, 0x45, 0x4E,
    0x44, 0xAE, 0x42, 0x60, 0x82,
])
