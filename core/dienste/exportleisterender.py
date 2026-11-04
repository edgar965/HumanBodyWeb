# -*- coding: utf-8 -*-
"""Exportleisterender — der Render-Schritt der Exportleiste: die Figur der Seite mit der BVH-Bewegung und dem Ton als Video (31.10.2026, `Exportleiste`).

Dieselben Stufen wie bei „2D3D Kleider" (`Engine2d3dKleiderrender`, Arbeitsprozess `manage.py exportleiste_render <bereich> <kennung>`): Bewegung schneiden → Figurcache (CPU) →
Stoff und Strähnen → Mitsuba mit Entrauscher, mit den Programmen des Rezepts (`arbeit/render/rezept.json` des Modells, sonst das allgemeine: `Figurfilm/standfilm`,
`Engine2d3dKleiderrenderallgemein`, je Modell nach `arbeit/render/film/` kopiert) und den Reglern der Leiste. Die Seite schickt die GLB mit dem Start, sie liegt als
`ergebnis/seite_<Fingerabdruck>.glb` mit ihrer Stellung daneben (`.stellung.json` — Mimik und Gelenkkorrektur lesen sie dort statt aus der Datenbank); `figur` baut daraus die
Render-GLB. Mit `EIGENES_MODELL` (2D3D Kleider) rendert die Leiste das Modell des Bereichs unverändert (`quelle.modell()`, Stellung aus dessen Datenbank wie bisher).
Stand in `arbeit/render/zustand.json`, Läufe in `laeufe.json` (`Engine2d3dKleiderrenderlaeufe`, liest `job.kennung`, `ablage`, `_datei`, `FPS` von hier). „Neu rendern" (`neu`):
abgelegte Läufe mit ihren Einstellungen und dem Modell von heute, nacheinander — der erste als `auftrag.json`, der Rest in `warteschlange.json` (`Engine2d3dKleiderrenderneu`).
"""

import hashlib
import json
import logging
import sys
import time
from pathlib import Path

from django.conf import settings

from .engine2d3dkleiderrenderallgemein import Engine2d3dKleiderrenderallgemein
from .engine2d3dkleiderrenderlaeufe import Engine2d3dKleiderrenderlaeufe
from .exportleistebewegung import Exportleistebewegung

logger = logging.getLogger('core')

__all__ = ['Exportleisterender']


class Exportleisterender:
    ORDNER = 'render'
    VIDEO = 'render_video.mp4'
    FPS = 30
    KAMERAS = ('zoom_ein', 'zoom_aus', 'zoom_ein_langsam', 'gesicht', 'brust')
    GRENZEN_PX = (64, 4096)
    #: „ohne Physik" (MP4-Export und Rendern, 31.10.2026): die Schalter des Katalogs `Figurfilm.Filmregler` (renderqualitaet `stoff.modus`: haut | hybrid | sim; renderphysik `*.an`)
    PHYSIK_AUS = {('renderqualitaet', 'stoff.modus'): 'haut', ('renderphysik', 'haar.an'): False, ('renderphysik', 'bart.an'): False,
                  ('renderphysik', 'uhr.an'): False, ('renderphysik', 'wind.staerke'): 0.0}
    MIN_SEKUNDEN = 10 / 30
    SPP, SPP_MIN, SPP_MAX = 96, 8, 256
    BEFEHL = 'exportleiste_render'

    def __init__(self, leiste):
        self.leiste = leiste
        self.job = leiste.quelle                 # `Engine2d3dKleiderrenderlaeufe` schreibt `job.kennung` ins Protokoll
        self.ablage = leiste.ablage

    def _datei(self, name):
        ordner = self.ablage.arbeitsordner(self.ORDNER)
        return ordner / name if name else ordner

    def rezept(self):
        """Das eigene Rezept des Modells (`arbeit/render/rezept.json`, z. B. Randy mit Stoff- und Strähnenwerten) — sonst das allgemeine; None, wenn auch dessen Vorlage fehlt."""
        pfad = self._datei('rezept.json')
        try:
            if pfad.is_file():
                return json.loads(pfad.read_text(encoding='utf-8'))
        except (OSError, ValueError) as fehler:
            logger.warning('Exportleiste %s: render/rezept.json nicht lesbar (%s)', self.job.kennung, fehler)
            return None
        return Engine2d3dKleiderrenderallgemein(self._datei('')).rezept()

    # ------------------------------------------------------------------- Stand

    def laeuft(self):
        from ..pipelines.prozesspruefung import Prozesspruefung
        pfad = self._datei('render.pid')
        try:
            return pfad.is_file() and Prozesspruefung.lebt(int(pfad.read_text().strip() or 0))
        except (OSError, ValueError):
            return False

    def bericht(self):
        """`{moeglich, status, schritt, fortschritt, ausgabe, fehler, laeufe}` für die Seite."""
        aus = {'moeglich': self.rezept() is not None, 'status': 'leer'}
        pfad = self._datei('zustand.json')
        try:
            if pfad.is_file():
                aus.update(json.loads(pfad.read_text(encoding='utf-8')))
        except (OSError, ValueError) as fehler:
            logger.info('Exportleiste %s: render/zustand.json nicht lesbar (%s)', self.job.kennung, fehler)
        aus.setdefault('quelle', 'rendern')          # Zustände vor dem 01.11.2026 ohne `quelle` stammen aus dem Block „Rendern“
        aus['laeufe'] = Engine2d3dKleiderrenderlaeufe(self).neueste()
        if aus.get('status') == 'laeuft' and not self.laeuft():
            aus.update(status='fehler', fehler=aus.get('fehler') or 'Der Render-Prozess ist abgebrochen (siehe %s)' % self.ablage.log())
        return aus

    def melden(self, **felder):
        pfad = self._datei('zustand.json')
        try:
            alt = json.loads(pfad.read_text(encoding='utf-8')) if pfad.is_file() else {}
        except (OSError, ValueError):
            alt = {}
        alt.update(felder, aktualisiert=time.strftime('%H:%M:%S'))
        zwischen = pfad.with_name('zustand.json.teil')
        zwischen.write_text(json.dumps(alt, ensure_ascii=False, indent=1), encoding='utf-8')
        zwischen.replace(pfad)

    # ------------------------------------------------------------------ Start

    def pruefen(self, angaben):
        """→ der Auftrag für den Arbeitsprozess (ohne GLB) oder ValueError mit der Meldung für die Seite."""
        from .modellexportziel import Modellexportziel
        from .studioton import Studioton
        if self.rezept() is None:
            raise ValueError('Die Programme des allgemeinen Render-Rezepts fehlen (Figurfilm/standfilm)')
        if self.job.sperre():
            raise ValueError(self.job.sperre())
        bvh = Exportleistebewegung.pfad(angaben.get('bvh'))
        _bilder, ganz = Exportleistebewegung.dauer(bvh)
        try:
            sekunden = float(angaben.get('sekunden'))
            spp = int(angaben.get('spp') or self.SPP)
        except (TypeError, ValueError):
            raise ValueError('Länge in Sekunden und Proben je Pixel: Zahlen') from None
        if round(sekunden * self.FPS) < round(self.MIN_SEKUNDEN * self.FPS) or round(sekunden * self.FPS) > round(ganz * self.FPS):
            raise ValueError('Länge: %.2f bis %.1f Sekunden (10 Bilder bis zur ganzen BVH)' % (self.MIN_SEKUNDEN, ganz))
        kamera = str(angaben.get('kamera') or '')
        if kamera not in self.KAMERAS:
            raise ValueError('Kamera: %s' % ', '.join(self.KAMERAS))
        ton = str(Studioton.pruefen(angaben.get('ton'))) if str(angaben.get('ton') or '').strip() else ''
        breite, hoehe = self._groesse(angaben)
        # Dictionary gewollt: geht als `auftrag.json` an den Arbeitsprozess. `physik` aus: Stoff, Haar, Bart, Wind starr (`ohne_physik`).
        return {'sekunden': sekunden, 'kamera': kamera, 'breite': breite, 'hoehe': hoehe, 'ton': ton, 'spp': max(self.SPP_MIN, min(self.SPP_MAX, spp)),
                'physik': angaben.get('physik') is not False,
                'name': str(angaben.get('name') or self.job.name())[:120], 'anmerkung': str(angaben.get('anmerkung') or '').strip()[:600],
                'datei': str(angaben.get('datei') or '').strip()[:120],          # Dateiname des Videos ohne Endung (leer: `<name>_render`)
                'bvh': str(bvh), 'bvh_sekunden': ganz, 'stellung': angaben.get('stellung') or {},
                # welcher Knopf startete (01.11.2026, Edgar: „warum sind zwei Sanduhren am laufen? ich habe nur den Render button geklickt“) — die Sanduhr nur dort
                'quelle': 'mp4' if angaben.get('quelle') == 'mp4' else 'rendern',
                'ordner': str(Modellexportziel.pruefen(angaben.get('ordner') or str(self.job.exportordner())))}

    def _laeuft_schon(self):
        """Die Meldung, wenn schon ein Render läuft — mit Start, Schritt und Länge (31.10.2026: Edgar sah nur „läuft schon“, während ein Lauf aus einem anderen Tab rechnete)."""
        b = self.bericht()
        start = time.strftime('%H:%M', time.localtime(b['start'])) if b.get('start') else '?'
        return 'Für dieses Modell läuft schon ein Render (seit %s: %s, %s Bilder) — der nächste geht, wenn er fertig ist; der Stand steht im Block „Rendern“' % (
            start, b.get('schritt') or 'läuft', b.get('bilder') or '?')

    @classmethod
    def _groesse(cls, angaben):
        """(breite, hoehe) aus `breite`/`hoehe` oder `groesse` ('1920x1080', auch aus einem alten Lauf) — gerade Zahlen (H.264, yuv420p) in `GRENZEN_PX`; sonst ValueError.
        Frei seit 31.10.2026 (Edgar: „mp4 video … mit Auflösung die man einstellen kann“); vorher nur 960 × 1200 und 480 × 600."""
        try:
            if angaben.get('breite') and angaben.get('hoehe'):
                breite, hoehe = int(angaben['breite']), int(angaben['hoehe'])
            else:
                breite, hoehe = (int(x) for x in str(angaben.get('groesse') or '960x1200').lower().split('x'))
        except (TypeError, ValueError):
            raise ValueError('Größe: Breite × Höhe in Pixeln, z. B. 1920x1080') from None
        lo, hi = cls.GRENZEN_PX
        if not (lo <= breite <= hi and lo <= hoehe <= hi):
            raise ValueError('Größe: je Seite %d bis %d Pixel' % (lo, hi))
        return breite - breite % 2, hoehe - hoehe % 2

    @classmethod
    def ohne_physik(cls, optionen):
        """Die Regler ohne Physik (`{gruppe: {schluessel: wert}}`, Kopie): Stoff gehäutet, keine Strähnen in Haar und Bart, kein Wind, die Uhr starr (`PHYSIK_AUS`)."""
        aus = {g: dict(w) for g, w in optionen.items()}
        for (gruppe, schluessel), wert in cls.PHYSIK_AUS.items():
            aus.setdefault(gruppe, {})[schluessel] = wert
        return aus

    def starten(self, glb_datei, angaben):
        """GLB ablegen, Auftrag schreiben, Arbeitsprozess starten → `bericht()`. ValueError bei falscher Eingabe oder laufendem Render."""
        from .engine2d3dkleiderrenderneu import Engine2d3dKleiderrenderneu
        if self.laeuft():
            raise ValueError(self._laeuft_schon())
        auftrag = self.pruefen(angaben)
        auftrag['glb'] = self._glb(glb_datei, auftrag['stellung'])
        Engine2d3dKleiderrenderneu(self).leeren()                 # ein frischer Render verwirft eine Warteschlange von „Neu rendern"
        return self._los(auftrag)

    def neu(self, glb_datei, angaben):
        """„Neu rendern": `angaben.nummern` (oder `alle`) — die Läufe mit ihren eigenen Einstellungen (Länge, Kamera, Größe, Proben, Ton, Anmerkung; BVH des Laufs, sonst die
        der Seite) und dem Modell von heute; der erste startet, der Rest wartet. Geprüft wird vor dem Start (Regel aus `Engine2d3dKleiderrenderneu.vormerken`)."""
        from .engine2d3dkleiderrenderneu import Engine2d3dKleiderrenderneu
        if self.laeuft():
            raise ValueError(self._laeuft_schon())
        laeufe = {int(e['nr']): e for e in Engine2d3dKleiderrenderlaeufe(self).lesen()}
        try:
            nummern = sorted(laeufe) if angaben.get('alle') else [int(n) for n in angaben.get('nummern') or []]
        except (TypeError, ValueError):
            raise ValueError('Laufnummern: ganze Zahlen') from None
        if not nummern or any(n not in laeufe for n in nummern):
            raise ValueError('Lauf %s gibt es nicht' % ', '.join('#%d' % n for n in nummern if n not in laeufe) if nummern else 'Kein Lauf gewählt')
        auftraege = []
        for n in nummern:
            lauf = laeufe[n]
            ton = (lauf.get('ton_pfad') or angaben.get('ton') or '') if lauf.get('ton') else ''
            eigen = dict(angaben, sekunden=lauf.get('sekunden'), kamera=lauf.get('kamera'), groesse=lauf.get('groesse'), breite=None, hoehe=None,
                         physik=lauf.get('physik') is not False, spp=lauf.get('spp'), ton=ton,
                         anmerkung=lauf.get('anmerkung') or '', name=lauf.get('name') or angaben.get('name'), bvh=lauf.get('bvh') or angaben.get('bvh'))
            try:
                auftraege.append(dict(self.pruefen(eigen), neu_nr=n))
            except ValueError as fehler:
                raise ValueError('Lauf #%d: %s' % (n, fehler)) from None
        glb = self._glb(glb_datei, auftraege[0]['stellung'])
        auftraege = [dict(a, glb=glb) for a in auftraege]
        warteschlange = Engine2d3dKleiderrenderneu(self)
        warteschlange.schreiben(auftraege[1:])
        return self._los(auftraege[0], wartend=warteschlange.wartend())

    def _los(self, auftrag, wartend=0):
        """`auftrag.json` ablegen, Stand „läuft", Arbeitsprozess starten → `bericht()`."""
        from .auftragsarbeiter import Auftragsarbeiter
        self._datei('auftrag.json').write_text(json.dumps(auftrag, ensure_ascii=False, indent=1), encoding='utf-8')
        self.melden(status='laeuft', schritt='Startet …', fortschritt=0.0, ausgabe=None, fehler=None, bilder=int(round(auftrag['sekunden'] * self.FPS)),
                    sekunden=auftrag['sekunden'], neu_nr=auftrag.get('neu_nr'), wartend=wartend, start=time.time(), quelle=auftrag.get('quelle', 'rendern'))
        befehl = [sys.executable, str(Path(settings.BASE_DIR) / 'manage.py'), self.BEFEHL, self.job.BEREICH, self.job.kennung]
        with open(self.ablage.log(), 'ab') as protokoll:
            prozess = Auftragsarbeiter._popen(befehl, protokoll)
        self._datei('render.pid').write_text(str(prozess.pid))
        logger.info('Exportleiste %s/%s: Render gestartet (Prozess %s, %.2f s, %s%s)', self.job.BEREICH, self.job.kennung, prozess.pid, auftrag['sekunden'], auftrag['kamera'],
                    ', neu: Lauf #%s, %d wartend' % (auftrag['neu_nr'], wartend) if auftrag.get('neu_nr') else '')
        return self.bericht()

    def _glb(self, glb_datei, stellung):
        """Die GLB für den Render (Text des Pfads): das Modell des Bereichs (`EIGENES_MODELL`) oder die GLB der Seite (`_modell`)."""
        if self.job.EIGENES_MODELL:
            return str(self.job.modell())
        if glb_datei is None:
            raise ValueError('Die Figur fehlt (GLB)')
        return str(self._modell(glb_datei, stellung))

    def figur(self, eingang, stellung):
        """Die Render-GLB (Path): das Modell des Bereichs unverändert, sonst neben der GLB der Seite `<stamm>_render.glb` (geht mit ihr weg) — Figur wie der Stand von 2D3D Kleider,
        Stücke aus der Seite (`Exportleisterendermodell`), Bericht als `.bericht.json` daneben."""
        import os
        import shutil

        from .exportleisterendermodell import Exportleisterendermodell
        if self.job.EIGENES_MODELL:
            return eingang
        ziel = eingang.with_name(eingang.stem + '_render.glb')
        teil = ziel.with_name(ziel.name + '.teil')
        t = time.time()
        bericht = Exportleisterendermodell(self.job.kacheln()).bauen(eingang, stellung, teil)
        os.replace(teil, ziel)
        shutil.copyfile(eingang.with_suffix('.stellung.json'), ziel.with_suffix('.stellung.json'))
        bericht['sekunden'] = round(time.time() - t, 1)
        ziel.with_suffix('.bericht.json').write_text(json.dumps(bericht, ensure_ascii=False, indent=1), encoding='utf-8')
        logger.info('Exportleiste %s: Render-Figur %s (%s)', self.job.kennung, ziel.name, bericht)
        return ziel

    def _modell(self, glb_datei, stellung):
        """Die GLB der Seite als `ergebnis/seite_<Fingerabdruck>.glb` (Regel artefakte-benennen: Mimik- und Korrekturdaten hängen am Dateinamen) — ältere Fassungen gehen weg.
        Nicht `modell_*`: Bei 2D3D Kleider ist `ergebnis/` der Ordner des Auftrags, dort liegen `modell.glb` und `modell_animiert.*` (`Engine2d3dKleideranimexport`)."""
        roh = b''.join(glb_datei.chunks())
        if roh[:4] != b'glTF':
            raise ValueError('Die Figur kam nicht als GLB an')
        stamm = 'seite_%s' % hashlib.md5(roh).hexdigest()[:12]
        for alt in self.ablage.ergebnis().glob('seite_*'):
            if not alt.name.startswith(stamm):
                alt.unlink(missing_ok=True)
        ziel = self.ablage.ergebnis(stamm + '.glb')
        ziel.write_bytes(roh)
        ziel.with_suffix('.stellung.json').write_text(json.dumps(stellung, ensure_ascii=False), encoding='utf-8')
        return ziel
