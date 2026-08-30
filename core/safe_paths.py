r"""SafePath — die EINE Stelle, an der Pfade aus HTTP-Anfragen geprüft werden.

(Dieser Docstring ist ein raw-String: Er enthält Windows-Pfade als Beispiel, und
`\x` wäre in einem normalen String der Anfang einer Hex-Escape-Folge — genau
daran ist die Datei beim ersten Übersetzen gescheitert.)

WARUM ES DIESE DATEI GIBT (12.08.2026)
--------------------------------------
Im Review fielen vier Endpunkte auf, die Pfade aus dem Request entgegennahmen:
`studio_project_save`, `studio_project_load`, `studio_project_list` und der
Video-Export in `cloth_export_api`. Drei prüften gar nichts — ein POST mit
`Content-Type: text/plain` (also ohne CSRF-Vorabfrage, auch von einer fremden
Webseite auslösbar) legte Verzeichnis und Datei an beliebiger Stelle an. Das war
kein theoretischer Befund, es wurde ausprobiert.

Der vierte Endpunkt (`save_bvh_text`) prüfte, aber falsch:

    if not str(sp).startswith(str(media)):     # ALT

Ein String-Präfix ist kein Pfad-Vergleich: `<media>_evil\x.bvh` besteht ihn.

DESHALB EIN HELFER UND KEIN FLICKEN JE ENDPUNKT: Dasselbe Muster — an einer
Stelle richtig, an den übrigen nicht — fand sich auch beim Zeichensatz der
Subprozesse (1 von 4) und beim Abräumen von stderr (5 von 6). Wer die nächste
Datei-Funktion baut, soll nicht wieder selbst nachdenken müssen, sondern hier
aufrufen.

WAS GEPRÜFT WIRD, UND WARUM GENAU DAS
-------------------------------------
UNC-Pfade (`\\\\server\\share`) werden abgelehnt, bevor das Dateisystem berührt
wird. Grund: Windows baut dafür eine SMB-Verbindung auf — das kann hängen und im
schlechtesten Fall Anmeldedaten nach außen tragen. (Im Test bog Windows
`\\\\127.0.0.1\\…` zwar in einen lokalen Pfad um; darauf verlässt sich hier
niemand.)

Gerätenamen (`NUL`, `CON`, `COM1` …) werden abgelehnt: Sie sind keine Dateien,
und ein Schreibversuch darauf verschwindet lautlos oder blockiert.

Verglichen wird mit `Path.is_relative_to()` auf aufgelösten Pfaden, unter Windows
zusätzlich case-normalisiert (`os.path.normcase`) — dort sind `A:\Media` und
`a:\media` dasselbe Verzeichnis, für einen String-Vergleich aber nicht.

Dateinamen dürfen nur Namen sein: Weicht `Path(name).name` vom Eingabewert ab,
steckte ein Verzeichnisanteil darin und der Wert wird abgelehnt — nicht
stillschweigend zurechtgeschnitten, sonst landet die Datei woanders als in der
Anzeige steht.

ERLAUBTE WURZELN
----------------
Die Studio-Verzeichnisse sind vom Nutzer einstellbar (`AppSettings.ui_prefs`:
`studio_project_path`, `studio_bvh_input`, `studio_bvh_output`,
`studio_video_output`). Sie gelten deshalb als erlaubt, auch wenn sie außerhalb
von `A:\3DTools` liegen — es ist eine bewusste eigene Einstellung, kein
Fremdeingabewert. Alles andere muss unter `TOOLS_ROOT`, `MEDIA_ROOT` oder der
BVH-Wurzel liegen.
"""
import logging
import os
from pathlib import Path

from django.conf import settings

from . import namensregeln
from .daten.pfadwurzeln import Pfadwurzeln
from .namensregeln import Namensregeln

logger = logging.getLogger('core')

#: Weitergereicht, damit `from .safe_paths import GERAETE` weiter geht — die
#: Listen und ihre Begruendung stehen seit dem 30.08.2026 in `namensregeln.py`,
#: weil `pruefe` und `dateiname` sie GEMEINSAM brauchen und die Regeln dazwischen
#: schon einmal auseinandergelaufen sind.
GERAETE = namensregeln.GERAETE
NAME_VERBOTEN = namensregeln.VERBOTEN


class PfadAbgelehnt(ValueError):
    """Der übergebene Pfad liegt außerhalb der erlaubten Wurzeln oder ist unsicher."""


class SafePath:
    """Prüft rohe Pfadangaben gegen eine Liste erlaubter Wurzeln.

    Aufruf über die Fabrikmethoden, nicht über den Konstruktor — so steht die
    Zweckbindung im aufrufenden Code:

        sp = SafePath.fuer_studio_projekte().pruefe(data.get('path'))
        name = SafePath.dateiname(payload.get('filename'), '.mp4')
    """

    def __init__(self, wurzeln):
        self.wurzeln = [w for w in (self._auflösen(w) for w in wurzeln) if w is
                        not None]

    # ------------------------------------------------------------ Fabrikmethoden

    @classmethod
    def fuer_studio_projekte(cls):
        """Projektdateien des BVH-Studios (.studio.json)."""
        return cls(Pfadwurzeln.studio_projekte())

    @classmethod
    def fuer_bvh(cls):
        """BVH-Dateien: die Kategorie-Wurzel plus die eingestellten Ordner."""
        return cls(Pfadwurzeln.bvh(cls.bvh_wurzel()))

    @classmethod
    def fuer_ausgabe(cls):
        """Render-Ausgaben (Video-Export)."""
        return cls(Pfadwurzeln.ausgabe())

    @classmethod
    def fuer_videos(cls):
        """Videodateien, aus denen ein Auftrag entstehen darf.

        Anlass (Sparring mit Nemotron, 18.08.2026): `create_job_from_file`
        uebernahm den `video_path` aus dem Rumpf UNGEPRUEFT — auch absolut.
        `BVHJob.video_file` haelt ihn dann, und `video_thumbnail` oeffnet
        `MEDIA_ROOT / str(job.video_file)`; bei einem absoluten Wert schluckt
        `pathlib` die Wurzel und uebrig bleibt genau der fremde Pfad. Der Weg
        ueber die Oberflaeche schickt nur Dateien aus dieser Liste, die Pruefung
        kostet also nichts — sie schliesst nur den direkten Aufruf aus.
        """
        return cls(Pfadwurzeln.videos())

    @classmethod
    def projekt_standard(cls):
        """Vorgabe-Verzeichnis der Studio-Projekte (wie in den Einstellungen)."""
        return Pfadwurzeln.projekt_standard()

    # ------------------------------------------------------------------- Wurzeln

    @staticmethod
    def bvh_wurzel():
        """Die Wurzel ÜBER den Kategorie-Ordnern (Aist, Bandai, Mixamo …).

        `settings.HUMANBODY_BVH_DIR` zeigt auf eine einzelne Kategorie
        (`…/bvh/MocapNET`), deshalb hier `.parent`. Das war schon vorher so und
        ist gewollt — aber fragil: Zeigt die Einstellung eines Tages direkt auf
        `…/bvh`, gäbe `.parent` plötzlich `data/animations` frei, wo auch
        Sicherungen liegen. Darum wird hier festgehalten, dass der Ordnername
        `bvh` erwartet wird, und andernfalls gewarnt."""
        b = Path(str(settings.HUMANBODY_BVH_DIR)).resolve()
        # Zeigt die Einstellung schon auf `…/bvh`, ist DAS die Wurzel — sonst
        # gäbe `.parent` das Elternverzeichnis `data/animations` frei, in dem
        # auch Sicherungen liegen (Einwand aus dem Sparring, 13.08.2026: vorher
        # wurde hier nur gewarnt und die zu weite Wurzel trotzdem geliefert).
        wurzel = b if b.name.lower() == 'bvh' else b.parent
        if wurzel.name.lower() != 'bvh':
            # Verschlossen scheitern: Lieber alle BVH-Endpunkte mit einer
            # eindeutigen Meldung ablehnen als stillschweigend ein zu weites
            # Verzeichnis zum Schreiben und Löschen freigeben.
            logger.error(
                'SafePath: BVH-Wurzel nicht bestimmbar — HUMANBODY_BVH_DIR=%r, '
                'erwartet wurde ein Ordner "bvh" oder eine Kategorie darunter.', str(b))
            raise PfadAbgelehnt('BVH-Wurzel nicht bestimmbar (HUMANBODY_BVH_DIR)')
        return wurzel

    @staticmethod
    def _auflösen(pfad):
        try:
            return Path(str(pfad)).resolve()
        # stumm gewollt: `None` ist hier die Antwort „kein auswertbarer Pfad“ —
        # der Aufrufer lehnt danach ab und DER protokolliert.
        except (OSError, ValueError):
            return None

    # -------------------------------------------------------------------- Prüfen

    def pruefe(self, roh, muss_existieren=False):
        """Rohangabe -> aufgelöster Path innerhalb der Wurzeln.

        Wirft `PfadAbgelehnt`, sonst nichts. Der Aufrufer muss NICHT selbst
        `resolve()` aufrufen; das Ergebnis ist bereits aufgelöst.

        DREI PRÜFUNGEN, in dieser Reihenfolge — sie bauen aufeinander auf:
        auflösen, die Namen prüfen, die Lage prüfen. Getrennt seit dem
        30.08.2026 (Rang C, zwölf Verzweigungen in einem Rumpf).
        """
        ziel = self._aufloesen(roh)
        self._namen_pruefen(ziel)
        self._lage_pruefen(ziel)
        if muss_existieren and not ziel.exists():
            raise PfadAbgelehnt('Datei oder Verzeichnis nicht gefunden')
        return ziel

    def _aufloesen(self, roh):
        """Rohangabe -> `Path`, aufgelöst. Prüft noch nichts über die Lage."""
        text = (str(roh) if roh is not None else '').strip()
        if not text:
            raise PfadAbgelehnt('Kein Pfad angegeben')
        self._grobpruefung(text)
        try:
            return Path(text).resolve()
        except (OSError, ValueError) as e:
            raise PfadAbgelehnt('Pfad nicht auflösbar: %s' % e) from e

    @staticmethod
    def _namen_pruefen(ziel):
        r"""JEDEN Namensbestandteil prüfen, nicht nur den letzten.

        `parts[0]` ist der Anker (`A:\`) und enthält den einen erlaubten
        Doppelpunkt. Die Regeln stehen in `namensregeln.py`; bis zum
        18.08.2026 wurde ein Gerätename als VERZEICHNIS
        (`…\COM1\datei.txt`) nicht bemerkt.
        """
        if Namensregeln.geraet(ziel.name):
            raise PfadAbgelehnt('Gerätename ist kein gültiges Ziel: %s'
                                % ziel.name)
        for teil in ziel.parts[1:]:
            grund = Namensregeln.teil(teil)
            if grund:
                raise PfadAbgelehnt(grund)

    def _lage_pruefen(self, ziel):
        """Liegt der Pfad in einer der erlaubten Wurzeln?

        Der abgelehnte Pfad gehört ins Protokoll, nicht in die Antwort: Eine
        Fehlermeldung mit vollem Pfad ist eine Auskunft über das Dateisystem
        (im Review als Read-Oracle benannt).
        """
        if any(self._liegt_in(ziel, w) for w in self.wurzeln):
            return
        logger.warning('SafePath: Pfad abgelehnt: %s (Wurzeln: %s)',
                       ziel, ', '.join(str(w) for w in self.wurzeln))
        raise PfadAbgelehnt(
            'Pfad liegt ausserhalb der erlaubten Verzeichnisse')

    @staticmethod
    def _grobpruefung(text):
        """UNC und Alternate Data Streams ablehnen, BEVOR das Dateisystem antwortet."""
        # Deckt UNC und die Gerätepfade `\\?\` / `\\.\` in einem ab — die
        # eigene Abfrage dafür stand hinter dieser hier und war unerreichbar.
        if text.startswith('\\\\') or text.startswith('//'):
            raise PfadAbgelehnt('Netzwerk- und Gerätepfade sind nicht erlaubt')
        # NTFS-Datenströme: "datei.json:versteckt" landet nicht als Datei.
        # Der Laufwerksbuchstabe (C:) ist der erlaubte Doppelpunkt.
        ohne_laufwerk = text[2:] if len(text) > 1 and text[1] == ':' else text
        if ':' in ohne_laufwerk:
            raise PfadAbgelehnt('Doppelpunkte im Pfad sind nicht erlaubt')

    @staticmethod
    def _liegt_in(ziel, wurzel):
        """`is_relative_to` statt `startswith` — unter Windows case-normalisiert."""
        z, w = Path(os.path.normcase(ziel)), Path(os.path.normcase(wurzel))
        try:
            return z == w or z.is_relative_to(w)
        # stumm gewollt: `ValueError` heißt bei `is_relative_to` schlicht
        # „liegt nicht darunter“ — genau der Rückgabewert.
        except ValueError:
            return False

    # ----------------------------------------------------------------- Dateiname

    @staticmethod
    def dateiname(roh, endung=None):
        """Reiner Dateiname ohne Verzeichnisanteil — oder `PfadAbgelehnt`.

        Bewusst KEIN stilles Zurechtschneiden: Wer `..\\..\\x.mp4` schickt, soll
        eine Absage bekommen und nicht eine Datei, die woanders liegt als der
        Name vermuten lässt."""
        text = (str(roh) if roh is not None else '').strip()
        if not text:
            raise PfadAbgelehnt('Kein Dateiname angegeben')
        if Path(text).name != text or text in ('.', '..'):
            raise PfadAbgelehnt('Dateiname darf keinen Pfadanteil enthalten')
        # DIESELBEN Regeln wie in `pruefe` (`namensregeln.py`). Sie fehlten
        # hier einmal, und ein Name wie `video:1.mp4` kam durch.
        grund = Namensregeln.datei(text)
        if grund:
            raise PfadAbgelehnt(grund)
        if endung and not text.lower().endswith(endung.lower()):
            text += endung
        return text
