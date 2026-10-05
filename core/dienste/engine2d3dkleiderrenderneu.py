# -*- coding: utf-8 -*-
"""Engine2d3dKleiderrenderneu — Render-Läufe NOCH EINMAL rechnen, einzeln oder alle (04.10.2026).

Edgar: „auf der Render Tabelle brauche ich Buttons, um einen oder alle Render Jobs neu zu generieren." Ein Lauf wird mit seinen eigenen Einstellungen
(Länge, Kamera, Größe, Proben je Pixel, Ton, Anmerkung) und dem Modell von HEUTE wiederholt; das Ergebnis ERSETZT die Zeile des Laufs (gleiche Nummer,
Video und Bogen neu, Erstellungszeit neu). Es gibt nur eine Grafikkarte: Mehrere Läufe laufen nacheinander — der erste geht als `auftrag.json` an den
Arbeitsprozess, der Rest steht in `arbeit/render/warteschlange.json`, die der Arbeitsprozess nach jedem fertigen Lauf abarbeitet.
"""

import json
import logging

__all__ = ['Engine2d3dKleiderrenderneu']

logger = logging.getLogger('core')


class Engine2d3dKleiderrenderneu:
    DATEI = 'warteschlange.json'

    def __init__(self, render):
        self.render = render
        self.pfad = render._datei(self.DATEI)

    # ---------------------------------------------------------------- Auftrag

    def auftrag(self, lauf, ton_vorgabe=''):
        """Der Auftrag für `Engine2d3dKleiderrender.pruefen` und den Arbeitsprozess aus einem abgelegten Lauf (`laeufe.json`); `ValueError` mit Meldung für die Seite.

        Den Ton hält der Eintrag seit dieser Änderung als Pfad (`ton_pfad`); ältere Läufe kennen nur „mit Ton" — dann gilt `ton_vorgabe` (der Audio-Pfad der Seite).
        """
        from .studioton import Studioton
        render = self.render
        sekunden, kamera, (breite, hoehe) = render.pruefen(lauf.get('sekunden'), str(lauf.get('kamera') or ''), str(lauf.get('groesse') or ''))
        ton = ''
        if lauf.get('ton'):
            ton = str(Studioton.pruefen(lauf.get('ton_pfad') or ton_vorgabe))
        return {'sekunden': sekunden, 'kamera': kamera, 'breite': breite, 'hoehe': hoehe, 'ton': ton, 'name': str(lauf.get('name') or '')[:120],
                'spp': int(lauf.get('spp') or render.SPP), 'anmerkung': str(lauf.get('anmerkung') or '')[:600], 'neu_nr': int(lauf['nr'])}

    def vormerken(self, laeufe, nummern, ton_vorgabe=''):
        """Alle `nummern` prüfen, den Rest hinter dem ersten in die Warteschlange legen. → der erste Auftrag.

        Geprüft wird VOR dem Start, nicht erst im Arbeitsprozess: Ein Lauf mit fehlendem Ton oder zu langer Länge soll als Meldung auf der Seite
        stehen, nicht als abgebrochene Warteschlange nach Stunden.
        """
        je_nr = {int(e['nr']): e for e in laeufe}
        fehlend = [n for n in nummern if n not in je_nr]
        if fehlend:
            raise ValueError('Lauf %s gibt es nicht' % ', '.join('#%d' % n for n in fehlend))
        auftraege = []
        for n in nummern:
            try:
                auftraege.append(self.auftrag(je_nr[n], ton_vorgabe))
            except ValueError as fehler:
                raise ValueError('Lauf #%d: %s' % (n, fehler)) from None
        if not auftraege:
            raise ValueError('Kein Lauf gewählt')
        self.schreiben(auftraege[1:])
        return auftraege[0]

    # ------------------------------------------------------------ Warteschlange

    def lesen(self):
        try:
            return json.loads(self.pfad.read_text(encoding='utf-8')) if self.pfad.is_file() else []
        except (OSError, ValueError) as fehler:
            logger.warning('2D3D Kleider %s: render/%s nicht lesbar (%s)', self.render.job.kennung, self.DATEI, fehler)
            return []

    def schreiben(self, auftraege):
        if not auftraege:
            self.pfad.unlink(missing_ok=True)
            return
        zwischen = self.pfad.with_name(self.DATEI + '.teil')
        zwischen.write_text(json.dumps(auftraege, ensure_ascii=False, indent=1), encoding='utf-8')
        zwischen.replace(self.pfad)

    def naechster(self):
        """Den vordersten Auftrag aus der Warteschlange nehmen (und sie kürzen); None, wenn sie leer ist."""
        rest = self.lesen()
        if not rest:
            return None
        self.schreiben(rest[1:])
        return rest[0]

    def wartend(self):
        return len(self.lesen())

    def leeren(self):
        self.pfad.unlink(missing_ok=True)
