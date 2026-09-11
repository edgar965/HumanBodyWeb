# -*- coding: utf-8 -*-
"""Figurvideoablage — das fertige Figurvideo dort ablegen, wo der Nutzer es haben will.

WARUM (Edgar, 11.09.2026: „Auswahl des Pfades des Videos"): Beide Wege
legen ihr MP4 unter `MEDIA_ROOT/figurvideos/<kennung>/video.mp4` ab — ein
Ordner mit zwoelfstelligem Hex-Namen, in dem niemand ein Video wiederfindet.
Im Videobereich stehen deshalb ein Ordner und ein Dateiname; ist das Video
fertig, kommt eine Kopie dorthin, und die Antwort nennt den Pfad.

KOPIE, NICHT UMZUG: Die Datei unter MEDIA bleibt — von dort spielt der
Browser sie ab (`MEDIA_URL`); ein Ordner ausserhalb ist fuer ihn
unerreichbar. NICHT `videoablage.Videoablage` — die legt Studio-Videos in
`AppSettings.video_output_dir`; hier waehlt der Nutzer je Video den Ort.

Der Name entsteht aus Figur, Animation und Uhrzeit, wenn der Nutzer keinen
nennt: `FemaleGarmentCode_Walk_136_28_20260911-1142.mp4`. Eine vorhandene
Datei wird NIE ueberschrieben — es kommt `-2`, `-3` an den Stamm. Und ein
Name mit Pfadtrennern (`..\\x`) wird zu einem Namen ohne: Der Nutzer waehlt
den Ordner im Ordnerfeld, nicht im Dateinamen.
"""
import json
import os
import re
import shutil
from datetime import datetime

from django.conf import settings


class Figurvideoablage:
    """Ordner pruefen, Namen bilden, Kopie anlegen."""

    ENDUNG = '.mp4'
    #: Was im Dateinamen bleiben darf: Buchstaben (auch Umlaute), Ziffern,
    #: Punkt, Bindestrich, Unterstrich, Leerzeichen. Alles andere wird `_`.
    _UNERLAUBT = re.compile(r'[^\w.\- ]', re.UNICODE)
    #: Marke im Auftragsordner: das Video ist schon abgelegt (Server-Weg,
    #: `stand()` wird alle zwei Sekunden gefragt — kopiert wird einmal).
    MARKE = 'ablage.json'

    @classmethod
    def vorgabe_ordner(cls):
        return os.path.join(str(settings.MEDIA_ROOT), 'figurvideos')

    # --------------------------------------------------------------- Ordner

    @classmethod
    def ordner_pruefen(cls, ordner):
        """Absoluter Pfad, vorhanden oder anlegbar — sonst `ValueError`.

        Leer heisst Vorgabe. Geprueft wird beim START, nicht erst nach zwei
        Minuten Rechnen: Ein Tippfehler im Laufwerk soll sofort auffallen.
        """
        ordner = (ordner or '').strip().strip('"')
        if not ordner:
            return cls.vorgabe_ordner()
        if not os.path.isabs(ordner):
            raise ValueError('Die Ablage muss ein vollständiger Pfad sein '
                             '(z. B. A:\\Videos), nicht: %s' % ordner)
        try:
            os.makedirs(ordner, exist_ok=True)
        except OSError as fehler:
            raise ValueError('Ablage nicht anlegbar: %s (%s)'
                             % (ordner, fehler.strerror or fehler))
        if not os.path.isdir(ordner):
            raise ValueError('Ablage ist kein Ordner: %s' % ordner)
        return ordner

    # ----------------------------------------------------------------- Name

    @classmethod
    def dateiname(cls, name='', figur='', animation='', zeit=None):
        """Der Wunschname, bereinigt — oder Figur_Animation_Zeit."""
        stamm = cls._sauber(name)
        if stamm.lower().endswith(cls.ENDUNG):
            stamm = stamm[:-len(cls.ENDUNG)].rstrip(' ._')
        if not stamm:
            zeit = zeit or datetime.now()
            stamm = '_'.join([cls._sauber(figur) or 'figur',
                              cls._sauber(animation) or 'animation',
                              zeit.strftime('%Y%m%d-%H%M')])
        return stamm + cls.ENDUNG

    @classmethod
    def _sauber(cls, text):
        text = cls._UNERLAUBT.sub('_', str(text or '')).strip(' ._')
        return text[:80]

    # ---------------------------------------------------------------- Kopie

    @classmethod
    def ablegen(cls, quelle, ordner, name):
        """Kopie unter `<ordner>/<name>`; gibt den Pfad der Kopie zurueck."""
        ordner = cls.ordner_pruefen(ordner)
        ziel = cls._frei(os.path.join(ordner, name))
        shutil.copy2(quelle, ziel)
        return ziel

    @classmethod
    def _frei(cls, pfad):
        if not os.path.exists(pfad):
            return pfad
        stamm, endung = os.path.splitext(pfad)
        n = 2
        while os.path.exists('%s-%d%s' % (stamm, n, endung)):
            n += 1
        return '%s-%d%s' % (stamm, n, endung)

    @classmethod
    def fuer_auftrag(cls, auftragsordner):
        """Server-Weg: das fertige `video.mp4` gemaess `auftrag.json` ablegen.

        Einmal — danach steht der Pfad in `ablage.json`. Gibt den Pfad
        zurueck, oder `None`, wenn der Auftrag keine Ablage nennt.
        """
        marke = os.path.join(auftragsordner, cls.MARKE)
        if os.path.isfile(marke):
            with open(marke, encoding='utf-8') as datei:
                return json.load(datei).get('pfad')
        with open(os.path.join(auftragsordner, 'auftrag.json'),
                  encoding='utf-8') as datei:
            ablage = json.load(datei).get('ablage') or {}
        if not ablage.get('name'):
            return None
        pfad = cls.ablegen(os.path.join(auftragsordner, 'video.mp4'),
                           ablage.get('ordner'), ablage['name'])
        with open(marke, 'w', encoding='utf-8') as datei:
            json.dump({'pfad': pfad}, datei)
        return pfad
