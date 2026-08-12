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

logger = logging.getLogger('core')

#: Windows-Gerätenamen. Ein Schreibversuch darauf ist nie gewollt.
GERAETE = {
    'CON', 'PRN', 'AUX', 'NUL', 'CLOCK$',
    *(f'COM{i}' for i in range(1, 10)),
    *(f'LPT{i}' for i in range(1, 10)),
}


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
        self.wurzeln = [w for w in (self._auflösen(w) for w in wurzeln) if w is not None]

    # ------------------------------------------------------------ Fabrikmethoden

    @classmethod
    def fuer_studio_projekte(cls):
        """Projektdateien des BVH-Studios (.studio.json)."""
        return cls([Path(settings.MEDIA_ROOT), cls.projekt_standard()]
                   + cls._prefs_wurzeln('studio_project_path', 'studio_bvh_input',
                                        'studio_bvh_output'))

    @classmethod
    def fuer_bvh(cls):
        """BVH-Dateien: die Kategorie-Wurzel plus die eingestellten Ordner."""
        return cls([cls.bvh_wurzel(), Path(settings.MEDIA_ROOT)]
                   + cls._prefs_wurzeln('studio_bvh_input', 'studio_bvh_output'))

    @classmethod
    def fuer_ausgabe(cls):
        """Render-Ausgaben (Video-Export)."""
        return cls([Path(settings.MEDIA_ROOT)]
                   + cls._prefs_wurzeln('studio_video_output'))

    @classmethod
    def projekt_standard(cls):
        """Vorgabe-Verzeichnis der Studio-Projekte (wie in den Einstellungen)."""
        return Path(settings.TOOLS_ROOT) / 'HumanBody' / 'data' / 'studio_projects'

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
        wurzel = b.parent
        if wurzel.name.lower() != 'bvh':
            logger.warning(
                'SafePath: BVH-Wurzel heisst %r, erwartet wurde "bvh" — pruefen, '
                'ob HUMANBODY_BVH_DIR noch auf eine Kategorie zeigt.', wurzel.name)
        return wurzel

    # `TOOLS_ROOT` ist BEWUSST KEINE Wurzel. Der erste Wurf hatte sie drin — die
    # Live-Prüfung zeigte sofort, dass damit `A:\3DTools\evil.json`,
    # `…\HumanBodyWeb\media_evil\…` und jeder Pfad im Projekt durchgehen, also
    # auch `ui/settings.py`, `.git/` und die `.npy`-Morphdaten. Ein Wächter, der
    # das gesamte Arbeitsverzeichnis freigibt, ist keiner (12.08.2026).

    @classmethod
    def _prefs_wurzeln(cls, *schluessel):
        """Vom Nutzer eingestellte Verzeichnisse (leer, wenn nicht gesetzt)."""
        try:
            from .models import AppSettings
            prefs = AppSettings.load().ui_prefs or {}
        except Exception:                                        # noqa: BLE001
            logger.exception('SafePath: Einstellungen nicht lesbar')
            return []
        return [Path(prefs[k]) for k in schluessel if (prefs.get(k) or '').strip()]

    @staticmethod
    def _auflösen(pfad):
        try:
            return Path(str(pfad)).resolve()
        except (OSError, ValueError):
            return None

    # -------------------------------------------------------------------- Prüfen

    def pruefe(self, roh, muss_existieren=False):
        """Rohangabe -> aufgelöster Path innerhalb der Wurzeln.

        Wirft `PfadAbgelehnt`, sonst nichts. Der Aufrufer muss NICHT selbst
        `resolve()` aufrufen; das Ergebnis ist bereits aufgelöst."""
        text = (str(roh) if roh is not None else '').strip()
        if not text:
            raise PfadAbgelehnt('Kein Pfad angegeben')
        self._grobpruefung(text)

        try:
            ziel = Path(text).resolve()
        except (OSError, ValueError) as e:
            raise PfadAbgelehnt('Pfad nicht auflösbar: %s' % e) from e

        if ziel.name.split('.')[0].upper() in GERAETE:
            raise PfadAbgelehnt('Gerätename ist kein gültiges Ziel: %s' % ziel.name)

        if not any(self._liegt_in(ziel, w) for w in self.wurzeln):
            # Der abgelehnte Pfad gehört ins Protokoll, nicht in die Antwort:
            # eine Fehlermeldung mit vollem Pfad ist eine Auskunft über das
            # Dateisystem (im Review als Read-Oracle benannt).
            logger.warning('SafePath: Pfad abgelehnt: %s (Wurzeln: %s)',
                           ziel, ', '.join(str(w) for w in self.wurzeln))
            raise PfadAbgelehnt('Pfad liegt ausserhalb der erlaubten Verzeichnisse')

        if muss_existieren and not ziel.exists():
            raise PfadAbgelehnt('Datei oder Verzeichnis nicht gefunden')
        return ziel

    @staticmethod
    def _grobpruefung(text):
        """UNC und Alternate Data Streams ablehnen, BEVOR das Dateisystem antwortet."""
        if text.startswith('\\\\') or text.startswith('//'):
            raise PfadAbgelehnt('Netzwerkpfade (UNC) sind nicht erlaubt')
        if text.startswith('\\\\?\\') or text.startswith('\\\\.\\'):
            raise PfadAbgelehnt('Gerätepfade sind nicht erlaubt')
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
        if text.split('.')[0].upper() in GERAETE:
            raise PfadAbgelehnt('Gerätename ist kein gültiger Dateiname')
        # Fuehrender Bindestrich: Der Name landet in Kommandozeilen (ffmpeg im
        # Video-Export). Dort wuerde "-i.mp4" als OPTION gelesen, nicht als Datei.
        # Praktisch schuetzt hier schon der vorangestellte Verzeichnispfad, aber
        # ein Dateiname, der wie ein Schalter aussieht, ist nie gewollt — und die
        # naechste Aufrufstelle stellt den Pfad vielleicht nicht davor
        # (Einwand aus dem Sparring, 12.08.2026).
        if text.startswith('-'):
            raise PfadAbgelehnt('Dateiname darf nicht mit einem Bindestrich beginnen')
        # Windows schneidet Punkte und Leerzeichen am Ende ab — dann zeigt die
        # Oberfläche einen anderen Namen an als auf der Platte steht.
        if text != text.rstrip(' .'):
            raise PfadAbgelehnt('Dateiname darf nicht auf Punkt oder Leerzeichen enden')
        if endung and not text.lower().endswith(endung.lower()):
            text += endung
        return text
