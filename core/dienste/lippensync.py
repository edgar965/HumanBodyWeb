# -*- coding: utf-8 -*-
"""Lippensync — Mundformen mit Zeiten aus einer Tondatei (Rhubarb Lip Sync).

WAS RHUBARB TUT (github.com/DanielSWolf/rhubarb-lip-sync, 1.14.0, MIT):
aus einer WAV-Datei die Folge der Mundformen des Preston-Blair-Satzes —
A (geschlossen, M/B/P), B (leicht offen, die meisten Konsonanten),
C (offen, E), D (weit offen, A), E (leicht gerundet, O), F (gespitzt, U/W),
G (Zaehne auf der Lippe, F/V), H (Zunge oben, L), X (Ruhe) — je mit
`start`/`end` in Sekunden. Der Erkenner `phonetic` kommt ohne Sprache aus
(PocketSphinx kann nur Englisch); Edgar spricht Deutsch. Gemessen: 184 s
Musik in 15,7 s.

Rhubarb liest nur WAV/OGG: eine MP3 wird vorher mit ffmpeg gewandelt
(mono, 16 kHz — mehr braucht der Erkenner nicht) und liegt als `.wav`
neben der Quelle; das Ergebnis als `<name>.lipsync.json` daneben. Beides
im Medienordner des Studios, nie in System-Temp.
"""

import json
import logging
import os
import subprocess

from django.conf import settings

logger = logging.getLogger('core')


class LipsyncFehler(RuntimeError):
    """Rhubarb fehlt, bricht ab oder die Tondatei ist nicht lesbar."""


class Lippensync:
    """Tondatei -> `{dauer, cues: [{start, end, form}]}`."""

    ZEITGRENZE = 900
    ERKENNER = 'phonetic'
    FORMEN = 'ABCDEFGHX'
    ENDUNG = '.lipsync.json'

    @staticmethod
    def programm():
        pfad = str(getattr(settings, 'RHUBARB_EXE', '') or '')
        return pfad if os.path.isfile(pfad) else None

    @staticmethod
    def flags():
        """Kein Konsolenfenster fuer ffmpeg und Rhubarb (Windows)."""
        return getattr(subprocess, 'CREATE_NO_WINDOW', 0)

    @classmethod
    def verfuegbar(cls):
        return cls.programm() is not None

    # ---------------------------------------------------------------- cues

    @classmethod
    def cues(cls, tonpfad, neu=False):
        """Die Mundformen einer Tondatei — aus der Ablage daneben, sonst
        gerechnet. `neu` erzwingt die Rechnung."""
        tonpfad = str(tonpfad)
        if not os.path.isfile(tonpfad):
            raise LipsyncFehler('Tondatei fehlt: %s' % os.path.basename(tonpfad))
        ablage = os.path.splitext(tonpfad)[0] + cls.ENDUNG
        if not neu and os.path.isfile(ablage):
            try:
                with open(ablage, encoding='utf-8') as datei:
                    daten = json.load(datei)
                if daten.get('cues'):
                    return daten
            except OSError, ValueError:
                pass
        daten = cls.rechnen(tonpfad, ablage)
        try:
            with open(ablage, 'w', encoding='utf-8') as datei:
                json.dump(daten, datei)
        except OSError as fehler:
            logger.warning('[lipsync] Ablage nicht schreibbar: %s', fehler)
        return daten

    @classmethod
    def rechnen(cls, tonpfad, ziel):
        """Rhubarb laufen lassen; das JSON geht ueber `-o` nach `ziel` (mit
        `-q` schweigt Rhubarb auch auf stdout, gemessen 18.09.2026)."""
        programm = cls.programm()
        if programm is None:
            raise LipsyncFehler('Rhubarb Lip Sync fehlt (RHUBARB_EXE)')
        wav = cls.als_wav(tonpfad)
        befehl = [programm, '-r', cls.ERKENNER, '-f', 'json', '-q', '-o', str(ziel), wav]
        try:
            lauf = subprocess.run(
                befehl,
                capture_output=True,
                text=True,
                timeout=cls.ZEITGRENZE,
                encoding='utf-8',
                errors='replace',
                creationflags=cls.flags(),
            )
        except subprocess.TimeoutExpired:
            raise LipsyncFehler('Rhubarb: Zeitgrenze von %d s überschritten' % cls.ZEITGRENZE)
        except OSError as fehler:
            raise LipsyncFehler('Rhubarb startet nicht: %s' % fehler)
        if lauf.returncode != 0 or not os.path.isfile(ziel):
            raise LipsyncFehler('Rhubarb bricht ab (%d): %s' % (lauf.returncode, (lauf.stderr or '')[-400:]))
        with open(ziel, encoding='utf-8') as datei:
            return cls.lesen(datei.read())

    @classmethod
    def lesen(cls, text):
        """Rhubarbs JSON -> `{dauer, cues}`; unbekannte Formen werden X."""
        try:
            roh = json.loads(text)
        except ValueError:
            raise LipsyncFehler('Rhubarb: Antwort nicht lesbar')
        cues = []
        for c in roh.get('mouthCues') or []:
            form = str(c.get('value') or 'X').upper()
            cues.append(
                {
                    'start': round(float(c.get('start', 0.0)), 3),
                    'end': round(float(c.get('end', 0.0)), 3),
                    'form': form if form in cls.FORMEN else 'X',
                }
            )
        dauer = float((roh.get('metadata') or {}).get('duration') or 0.0)
        if not dauer and cues:
            dauer = cues[-1]['end']
        return {'dauer': round(dauer, 3), 'cues': cues, 'erkenner': cls.ERKENNER}

    # ----------------------------------------------------------------- wav

    @classmethod
    def als_wav(cls, tonpfad):
        """Die WAV-Fassung neben der Quelle (mono, 16 kHz) — einmal gewandelt."""
        wurzel, endung = os.path.splitext(tonpfad)
        if endung.lower() == '.wav':
            return tonpfad
        ziel = wurzel + '.wav'
        if os.path.isfile(ziel) and os.path.getmtime(ziel) >= os.path.getmtime(tonpfad):
            return ziel
        from .videokodierer import Videokodierer

        befehl = [
            Videokodierer.programm(),
            '-y',
            '-loglevel',
            'error',
            '-i',
            tonpfad,
            '-ac',
            '1',
            '-ar',
            '16000',
            ziel,
        ]
        try:
            lauf = subprocess.run(
                befehl,
                capture_output=True,
                text=True,
                timeout=cls.ZEITGRENZE,
                encoding='utf-8',
                errors='replace',
                creationflags=cls.flags(),
            )
        except (OSError, subprocess.TimeoutExpired) as fehler:
            raise LipsyncFehler('ffmpeg wandelt nicht: %s' % fehler)
        if lauf.returncode != 0 or not os.path.isfile(ziel):
            raise LipsyncFehler('ffmpeg bricht ab: %s' % (lauf.stderr or '')[-400:])
        return ziel

    # ---------------------------------------------------------- Adressen

    @classmethod
    def pfad_aus_url(cls, url):
        """`/media/studio_audio/<name>` -> Pfad im Medienordner; alles andere None.

        Nur der Ordner des Studios: eine Adresse mit `..` oder ausserhalb
        liest keine fremde Datei."""
        text = str(url or '').split('?')[0]
        marke = 'studio_audio/'
        if marke not in text:
            return None
        name = os.path.basename(text.split(marke, 1)[1])
        if not name or name != text.split(marke, 1)[1]:
            return None
        ordner = os.path.join(str(settings.MEDIA_ROOT), 'studio_audio')
        pfad = os.path.normpath(os.path.join(ordner, name))
        if not pfad.startswith(os.path.normpath(ordner)):
            return None
        return pfad
