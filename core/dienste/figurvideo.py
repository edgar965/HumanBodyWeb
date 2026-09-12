# -*- coding: utf-8 -*-
"""Figurvideo — ein Video der animierten, angezogenen Figur, vom Server.

WARUM (Edgar, 11.09.2026: „wie kann ich so ein Video aus dem UI erzeugen?"):
Der Weg, der die ersten brauchbaren Videos erzeugt hat, lief als Skript
mit fest verdrahteter Figur. Hier bekommt er die Figur der Szene — mit
ihren Morphs und ihren GarmentCode-Stuecken — und die dort gewaehlte
Animation.

Die Kleidung kommt AUS DER SZENE — jedes gehaeutete Netz, das dort an
der Figur haengt, als Binaerpaket (`figurvideostuecke.py`). Bis zum
11.09.2026 gingen nur GarmentCode-Stuecke ueber ihre Rig-Datei mit.

Der Lauf ist ein UNTERPROZESS (`ModelPhysik/filmlauf.py`, python14): Er
braucht einen OpenGL-Kontext und zwei bis drei Minuten. Der Server startet
ihn, merkt sich die Kennung und liest den Fortschritt aus einer Datei, die
der Prozess atomar fortschreibt.

Ablage je Auftrag unter MEDIA_ROOT/figurvideos/<kennung>/:
    auftrag.json      was gerechnet wird
    fortschritt.json  Phase, Anteil, Fehler
    video.mp4         das Ergebnis
    video.mp4.json    die Messwerte dazu (Ruheprobe, Gleichlauf, Zuschlag)
    ablage.json       wohin die Kopie fuer den Nutzer ging (`figurvideoablage.py`)
"""
import json
import logging
import os
import subprocess
import uuid

from django.conf import settings

from .figurvideostuecke import Figurvideostuecke
from .laufende_prozesse import LaufendeProzesse
from .figurvideoablage import Figurvideoablage

logger = logging.getLogger('core')


class Figurvideo:
    """Startet den Videolauf und liest seinen Stand."""

    #: Grenzen, die eine Anfrage nicht ueberschreiten darf — ein Video von
    #: 60 Sekunden bei 24 fps sind 1.440 Bilder und rund eine halbe Stunde.
    HOECHSTE_SEKUNDEN = 20.0
    HOECHSTE_PHYSIK_MM = 80.0

    @classmethod
    def wurzel(cls):
        return os.path.join(str(settings.MEDIA_ROOT), 'figurvideos')

    @classmethod
    def _skript(cls):
        return os.path.join(str(settings.BASE_DIR), 'TheatreJS', 'ModelPhysik',
                            'filmlauf.py')

    # ---------------------------------------------------------------- Start

    @classmethod
    def starten(cls, daten, dateien=None):
        """Auftrag anlegen, Unterprozess starten, Kennung zurueckgeben.

        `dateien` sind die Stueckpakete aus dem Formular (`request.FILES`);
        die Stueckliste in `daten['stuecke']` nennt je Stueck seine Datei.
        """
        kennung = uuid.uuid4().hex[:12]
        ordner = os.path.join(cls.wurzel(), kennung)
        os.makedirs(ordner, exist_ok=True)
        auftrag = cls._auftrag(daten, ordner)
        auftrag['stuecke'] = Figurvideostuecke.ablegen(
            dateien or {}, daten.get('stuecke') or [],
            daten.get('knochen') or [], ordner)
        auftrag_pfad = os.path.join(ordner, 'auftrag.json')
        with open(auftrag_pfad, 'w', encoding='utf-8') as datei:
            json.dump(auftrag, datei, indent=1, ensure_ascii=False)
        # Derselbe Python wie der Server: pyrender, trimesh und cv2 liegen
        # in python14. KEIN Fenster (`CREATE_NO_WINDOW`), auch wenn der
        # Server aus einer Konsole laeuft. Das Protokoll wird nach `Popen`
        # geschlossen — das Kind haelt ein eigenes Handle darauf; offen
        # bliebe im Server ein Deskriptor je Lauf (Befund `offene-datei`).
        flags = getattr(subprocess, 'CREATE_NO_WINDOW', 0)
        with open(os.path.join(ordner, 'lauf.log'), 'w',
                  encoding='utf-8') as protokoll:
            prozess = subprocess.Popen(
                [cls._python(), cls._skript(), auftrag_pfad],
                stdout=protokoll, stderr=subprocess.STDOUT,
                cwd=os.path.dirname(cls._skript()), creationflags=flags)
        LaufendeProzesse.eintragen('figurvideo_' + kennung, prozess)
        logger.info('Figurvideo %s gestartet: %d Stuecke, %.1f s, %.0f mm',
                    kennung, len(auftrag['stuecke']), auftrag['sekunden'],
                    auftrag['physik_mm'])
        return kennung

    @classmethod
    def _python(cls):
        import sys
        return sys.executable

    @classmethod
    def _auftrag(cls, daten, ordner):
        sekunden = min(float(daten.get('sekunden') or 5.0),
                       cls.HOECHSTE_SEKUNDEN)
        physik = min(max(float(daten.get('physik_mm') or 0.0), 0.0),
                     cls.HOECHSTE_PHYSIK_MM)
        return {
            'body_type': daten.get('body_type') or 'Female_Caucasian',
            'morphs': dict(daten.get('morphs') or {}),
            'bvh': cls._bvh_pfad(daten.get('bvh_url') or ''),
            'ab_sekunden': max(float(daten.get('ab_sekunden') or 0.0), 0.0),
            'sekunden': sekunden, 'fps': 24.0, 'physik_mm': physik,
            'ziel': os.path.join(ordner, 'video.mp4'),
            'fortschritt': os.path.join(ordner, 'fortschritt.json'),
            # Wohin die Kopie fuer den Nutzer geht — beim Start geprueft,
            # damit ein falsches Laufwerk nicht erst nach Minuten auffaellt.
            'ablage': {
                'ordner': Figurvideoablage.ordner_pruefen(daten.get('ablage')),
                'name': Figurvideoablage.dateiname(
                    daten.get('dateiname'), daten.get('figur'),
                    daten.get('animation')),
            },
        }

    @staticmethod
    def _bvh_pfad(url):
        """`/api/character/bvh/<kategorie>/<name>/` -> Datei der Bibliothek."""
        from ..api.bvhdateien import Bvhauslieferung
        teile = [t for t in url.split('/') if t]
        if len(teile) < 2:
            raise ValueError('Keine Animation gewaehlt.')
        wurzel = Bvhauslieferung.wurzel()
        pfad = os.path.abspath(os.path.join(wurzel, teile[-2],
                                            '%s.bvh' % teile[-1]))
        if not pfad.startswith(os.path.abspath(wurzel) + os.sep):
            raise ValueError('Animation ausserhalb der Bibliothek.')
        if not os.path.isfile(pfad):
            raise ValueError('Animation nicht gefunden: %s/%s'
                             % (teile[-2], teile[-1]))
        return pfad

    # ---------------------------------------------------------------- Stand

    @classmethod
    def stand(cls, kennung):
        """Fortschritt, und wenn fertig: Adresse des Videos und Messwerte."""
        ordner = os.path.join(cls.wurzel(), cls._sicher(kennung))
        pfad = os.path.join(ordner, 'fortschritt.json')
        if not os.path.isfile(pfad):
            return {'phase': 'Wartet', 'anteil': 0.0, 'fertig': False,
                    'fehler': None}
        with open(pfad, encoding='utf-8') as datei:
            stand = json.load(datei)
        prozess = LaufendeProzesse.holen('figurvideo_' + kennung)
        if (prozess is not None and prozess.poll() is not None
                and not stand.get('fertig') and not stand.get('fehler')):
            # Der Prozess ist weg, ohne sich abzumelden — abgestuerzt oder
            # von aussen beendet. Ohne diese Zeile stuende der Balken
            # fuer immer bei seinem letzten Wert.
            stand['fehler'] = ('Der Lauf endete ohne Ergebnis '
                               '(Exit %s). Siehe lauf.log.'
                               % prozess.returncode)
        if stand.get('fertig'):
            stand['video_url'] = ('%sfigurvideos/%s/video.mp4'
                                  % (settings.MEDIA_URL, kennung))
            bilanz = os.path.join(ordner, 'video.mp4.json')
            if os.path.isfile(bilanz):
                with open(bilanz, encoding='utf-8') as datei:
                    stand['bilanz'] = json.load(datei)
            try:
                stand['pfad'] = Figurvideoablage.fuer_auftrag(ordner)
            except (OSError, ValueError) as fehler:
                # Das Video IST fertig — nur die Kopie ging nicht. Das
                # steht dann daneben, statt das Ergebnis zu verstecken.
                logger.warning('Figurvideo %s: Ablage nicht kopiert: %s',
                               kennung, fehler)
                stand['ablage_fehler'] = str(fehler)
            LaufendeProzesse.entfernen('figurvideo_' + kennung)
        return stand

    # ------------------------------------------------ Browser-Bildfolge

    @classmethod
    def aus_bildfolge(cls, bilder, fps=24, physik_mm=0.0, ablage=None):
        """PNG-Bilder aus der Szene -> MP4 unter derselben Ablage wie Weg 1.

        Der Browser-Weg rendert selbst (Kamera, Licht, Texturen der Szene)
        und schickt die Bilder; kodiert wird hier mit ffmpeg, und das
        Ergebnis liegt neben den Server-Videos — mit fester Adresse statt
        einer Blob-URL, die mit dem Tab stirbt. `ablage` = {ordner, name,
        figur, animation}: dorthin geht die Kopie fuer den Nutzer.
        Rueckgabe: (kennung, video_url, pfad der Kopie oder None).
        """
        from ..daten.hochgeladen import Hochgeladen
        from .videokodierer import Videokodierer
        import shutil
        kennung = uuid.uuid4().hex[:12]
        ordner = os.path.join(cls.wurzel(), kennung)
        bilderordner = os.path.join(ordner, 'bilder')
        os.makedirs(bilderordner, exist_ok=True)
        try:
            for platz, datei in enumerate(bilder):
                Hochgeladen.ablegen(os.path.join(bilderordner, '%06d.png' % platz),
                                    datei)
            ziel = os.path.join(ordner, 'video.mp4')
            Videokodierer.ausfuehren(
                Videokodierer.aus_bildfolge(bilderordner, ziel, fps=int(fps),
                                            crf=20),
                zeitgrenze=300)
            with open(ziel + '.json', 'w', encoding='utf-8') as datei:
                json.dump({'quelle': 'szene', 'bilder': len(bilder),
                           'fps': int(fps), 'physik_mm': float(physik_mm)},
                          datei, indent=1)
            pfad = None
            if ablage:
                pfad = Figurvideoablage.ablegen(
                    ziel, ablage.get('ordner'),
                    Figurvideoablage.dateiname(
                        ablage.get('name'), ablage.get('figur'),
                        ablage.get('animation')))
        finally:
            # Die Einzelbilder sind nach dem Kodieren nur noch Platz —
            # 48 Bilder à 300 KB je Lauf, und niemand raeumt sie sonst weg.
            shutil.rmtree(bilderordner, ignore_errors=True)
        return (kennung, '%sfigurvideos/%s/video.mp4'
                % (settings.MEDIA_URL, kennung), pfad)

    @staticmethod
    def _sicher(kennung):
        """Nur Hex-Zeichen — die Kennung kommt aus der Adresse."""
        return ''.join(c for c in str(kennung) if c in '0123456789abcdef')[:12]
