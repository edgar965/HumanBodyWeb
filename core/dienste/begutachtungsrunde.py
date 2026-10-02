# -*- coding: utf-8 -*-
"""Begutachtungsrunde — Runden der Iterationen von „2D3D Kleider" im Modus „Begutachtung" (30.09.2026).

Edgar: „jede iteration wird von dir begutachtet, und dann neuer Code erzeugt." Der Code ist ein Rezept
(`G9rezept`: Aufrufe an `ModellMitKleidern`), das der Prüfer (Fable) oder der Nutzer nach dem Ansehen der Bilder
schreibt (`POST …/begutachtung/`) — oder das `IterationModell` (Ordner `2d3DIterationen`) aus dem Befund der
letzten Runde selbst schreibt (`naechste.automatisch`, bis zu `naechste.runden` Runden in einem Lauf). Eine Runde:

    1. das Modell der letzten Runde (`kreislauf.modell`) — oder, in der ersten Runde, der Ausgangszustand
    2. das nächste Rezept anwenden — ein Fehler darin wird abgelegt, das Modell bleibt
    3. bauen (`Kleidermodellbau`), rendern aus den Blickwinkeln der Vorlagen (`Genesishaarrender`), benoten gegen die
       Fotos (`Iterationsnote`) und in 3D gegen das Netz (`Iterationsnetznote`), messen (`Begutachtungsbefund`)
    4. ablegen wie `Iterationsrunde.ablegen` (Tafel, Renders, GLB, Eintrag in `ergebnis['iterationen']`) — dazu
       `aufrufe`, `kommentar`, `rezept` (die wirksam gewordenen Aufrufe), `fehler`, `befund`
    5. `begutachtung.zustand = 'wartet'`: der Lauf endet mit Status „Wartet auf Begutachtung" (`Engine2d3dKleiderlauf`)

Nach jeder Runde entscheidet `Begutachtungsstand` (Gesamtnote, `Rundenauswahl`, 01.10.2026): Der Stand
(`kreislauf.modell`, `ergebnis/modell.glb`, Export, Film, Speichern) ist die BESTE Runde, eine Probe läuft in
`kreislauf.weiter`. Je Runde prüft `Messpruefung`, ob den Messungen zu trauen ist (`befund.messguete`).
"""

import logging
import shutil
import time

import numpy as np
from django.utils import timezone
from Genesis9.haltungshaut import G9haltungshaut
from Genesis9.rezeptumgebung import Rezeptumgebung

from .aufloesungsstufe import Aufloesungsstufe
from .begutachtungsbefund import Begutachtungsbefund
from .begutachtungskritik import Begutachtungskritik
from .begutachtungsstand import Begutachtungsstand
from .engine2d3dkleidergrundfigur import Engine2d3dKleidergrundfigur
from .haarabgleich import Haarabgleich
from .haarzonen import Haarzonen
from .haltungsfotos import Haltungsfotos
from .iterationsbild import Iterationsbild
from .iterationsnetznote import Iterationsnetznote
from .iterationsnote import Iterationsnote
from .iterationsoptionen import Iterationsoptionen
from .iterationsreferenz import Iterationsreferenz
from .iterationsrunde import Iterationsrunde
from .pruefbilder import Pruefbilder

logger = logging.getLogger('core')

__all__ = ['Begutachtungsrunde']


class Begutachtungsrunde:
    GLB = 'modell.glb'
    #: Gewicht der 3D-Note in der Gesamtabweichung (die Fotonote liegt meist bei 0,2–0,6, die Netznote ebenso).
    NETZGEWICHT = 1.0
    VERLAUF_HOECHSTENS = 5000
    RUNDEN_HOECHSTENS = 50

    def __init__(self, lauf):
        self.lauf = lauf
        self.job = lauf.job
        self.ablage = lauf.ablage
        self.o = Iterationsoptionen.pruefen((self.job.optionen or {}).get('iterationen'))
        self._lage = (0, 1)
        from .begutachtungswerkzeug import Begutachtungswerkzeug
        self.werkzeug = Begutachtungswerkzeug(self.job, self.ablage)     # Sichtkörper, Stofflöser, Fotoprojektion, Haut
        self.stufe = Aufloesungsstufe(self.job, self.ablage, self.o)      # Auflösung der Note, steigt bei Stillstand

    def _melden(self, anteil, text):
        self.lauf.melden((self._lage[0] + anteil) / self._lage[1], text)
        self.werkzeug.takt(text)                        # Dauer des vorigen Abschnitts ins Log (Frage Edgar 02.10.2026)

    # --------------------------------------------------------------- Ablauf

    def ausfuehren(self):
        from Genesis9.modellmitkleidern import ModellMitKleidern
        if not self.ablage.arbeit(Engine2d3dKleidergrundfigur.DATEI).is_file():
            raise RuntimeError('Keine Grundfigur — erst den Schritt „Grundfigur" rechnen')
        from .blickwinkelschaetzung import Blickwinkelschaetzung
        z = Blickwinkelschaetzung(self.job, self.ablage).fuer_lauf()   # Fotos ohne Winkel: aus der Pose (01.10.2026)
        beg = dict(self.job.ergebnis.get('begutachtung') or {})
        referenzen, ausgelassen = Iterationsreferenz.laden(self.job)
        Haltungsfotos(self.job, self.ablage).fuer_lauf(z, referenzen)   # die Arme der Fotos (01.10.2026)
        z['ausgelassen'] = ausgelassen
        z['winkel'] = {r.original: r.winkel for r in referenzen}
        quelle = (z.get('weiter') or {}).get('modell') or z.get('modell')    # eine Probe läuft weiter (Rundenauswahl)
        modell = ModellMitKleidern.aus(quelle) if quelle else self._start()
        naechste = beg.pop('naechste', None) or {}
        runden = 1
        if naechste.get('automatisch'):
            runden = max(1, min(self.RUNDEN_HOECHSTENS, int(naechste.get('runden') or 1)))
        grund = naechste.get('kommentar') or 'automatisch (IterationModell)'
        for i in range(runden):
            if i and self.lauf.angehalten():
                break
            self._lage = (i, runden)
            if naechste.get('automatisch'):
                neu = None if z.get('weiter') else self.stufe.faellig(z, referenzen)     # Stillstand in der Stufe
                aufrufe, zusatz, fertig = ('', 'Stillstand', False) if neu else self._automatisch(modell, z, referenzen)
                if fertig:          # keine Änderung mehr: erst feiner messen (Edgar 02.10.2026), dann enden
                    neu = self.stufe.naechste(z, referenzen)
                    if not neu:
                        Begutachtungskritik.beenden(self.lauf, z, beg, zusatz)
                        break
                if neu:             # Messrunde: die BESTE Runde in der neuen Stufe, ohne Rezept
                    aufrufe = self.stufe.steigen(z, neu, self._letzte_runde() + 1, zusatz or 'Stillstand')
                    modell = ModellMitKleidern.aus(z['modell']) if z.get('modell') else modell
                    z.pop('weiter', None)
                zusatz = aufrufe.strip('# \n') if neu else zusatz
                naechste = dict(naechste, aufrufe=aufrufe, messrunde=bool(neu),
                                kommentar=grund + ' · ' + zusatz if zusatz else grund)
            modell = self._runde(z, beg, modell, naechste, referenzen)
        if naechste.get('automatisch'):     # automatische Runden enden „fertig", nicht „wartet" (Edgar 02.10.2026)
            self.job.ergebnis.setdefault('begutachtung', {})['zustand'] = 'fertig'

    def _automatisch(self, modell, z, referenzen):
        """Das Rezept der nächsten Runde aus dem Befund der letzten (`IterationModell`), ergänzt um die Prüf-KI, wenn
        sie fällig ist (`Begutachtungskritik`) → (aufrufe, Zusatz zum Kommentar, fertig)."""
        from iterationen2d3d.iterationmodell import IterationModell
        kandidaten = [k.get('kennung') for k in (self.job.ergebnis.get('frisur') or {}).get('kandidaten') or []
                      if k.get('kennung')]
        befund = dict(Begutachtungsstand.befund_fuer_regeln(z) or {}, haltung_foto=z.get('haltung_foto'))
        # Was nicht vom Render abhängt, gilt schon für Runde 1 (Edgar: „beim nächsten Modell in Runde 1"): Fotostücke,
        # Uhr, Bart — vorher trug Runde 1 Bibliotheksshirt und -shorts (Wiederholungsauftrag 2026.10.01.19.21.30).
        befund['zubehoer'] = self.werkzeug.zubehoer(referenzen)     # immer frisch: ein gespeicherter Befund kennt neue
        befund['fotostuecke'] = self.werkzeug.fotostuecke()        # Erkenner nicht (Bart, 01.10.2026 abends)
        befund['haarzonen'] = dict(self.job.ergebnis.get('haarzonen') or {})      # Fotofarbe je Kopfzone
        if not befund.get('teile'):
            befund['haar_netzfarbe'] = self.werkzeug.haarfarbe()
        rezept = IterationModell(modell, befund, z.get('verlauf_befunde'), kandidaten,
                                 form=self.o.get('form') == 'an').rezept()
        rezept = Begutachtungsstand.ohne_gesperrte(rezept, z)        # Zeilen, die aus dieser Lage schon verworfen sind
        rezept, zusatz, fertig = Begutachtungskritik(self.o, self.ablage).ergaenzen(rezept, modell, z)
        if not fertig and not rezept:
            return '', 'Rundenauswahl: aus der besten Runde %s geht keine Änderung mehr' % z.get('runde_bester'), True
        return rezept, zusatz, fertig

    def _runde(self, z, beg, modell, naechste, referenzen):
        from Genesis9.modellrezept import G9rezept

        from .genesishaarrender import Genesishaarrender
        from .kleidermodellbau import Kleidermodellbau
        start = time.perf_counter()
        runde = self._letzte_runde() + 1
        rezept, fehler = [], None
        # Der Sichtkörper der Vorlagen (Konzept 4.1) steht dem Rezept zur Verfügung (`kleid_huelle`, `koerper_huelle`)
        # — gebaut aus den Silhouetten der Note und der Höhe des Modells der LETZTEN Runde (erste Runde: Körper).
        sicht = self.werkzeug.sichtkoerper(referenzen, z)
        modell.umgebung = Rezeptumgebung(sicht, self.werkzeug.drapierer(), auftrag=Rezeptumgebung.kuerzel(self.job.kennung),
                                         haardynamik=self.werkzeug.haardynamik())
        if naechste.get('aufrufe'):
            try:
                rezept = [text for _zeile, text in G9rezept.anwenden(modell, naechste['aufrufe'])]
            except ValueError as f:
                fehler = str(f)
                logger.warning('2D3D Kleider %s: Rezept der Runde %d: %s', self.job.kennung, runde, fehler)
        self._melden(0.1, 'Runde %d: Modell bauen' % runde)
        # Gebaut in der A-Pose (GLB, Bühne); Render, Note, Befund und Fotoprojektion in der Haltung der Fotos — gehäutet,
        # damit die Ärmel den Armen folgen (`G9haltungshaut`, 01.10.2026).
        bau = Kleidermodellbau(self.job.stellung(), None, koerper=modell.koerper, kacheln=self.werkzeug.kacheln())
        teile = G9haltungshaut(bau.stellung, modell.drehung(), bau.boden).posieren(
            Haarzonen.anwenden(bau.teile(modell), modell.farben))           # Haarfarbe je Kopfzone (02.10.2026)
        z['modell_hoehe'] = round(float(max(float(np.asarray(t['punkte'])[:, 1].max()) for t in teile)), 4)
        # Note in der Auflösungsstufe, Befund auf 128 × 192, Renders mindestens in Prüfbreite (Edgar 02.10.2026).
        breite = self.stufe.breite(z)
        groesse = Aufloesungsstufe.groesse(max(breite, int(self.o.get('tafelbreite') or 384)))
        befundgroesse = (Iterationsbild.BREITE, Iterationsbild.HOEHE)
        render = Genesishaarrender(None)
        aus = self.ablage.arbeit('runden') / ('runde_%04d' % runde)
        netznote = Iterationsnetznote.laden(self.ablage)
        messung = Begutachtungsbefund(netznote, sicht)
        je_ansicht, renders, paare = [], {}, []
        fototextur = {}
        try:
            # 1. Kennfarben je Ansicht (Teilmasken für Befund und Fotoprojektion), 2. Fotoprojektion, wenn das Rezept sie
            # will (die Schicht liegt danach neben der Bibliothek, die Teile bekommen ihre Texturen neu),
            # 3. der Render mit Texturen, der benotet wird (30.09.2026, nachts).
            for r in referenzen:
                messung.masken(render, teile, r, aus / ('kennung_%+04d.png' % int(round(r.winkel))), befundgroesse)
            self._melden(0.25, 'Runde %d: Fotoprojektion (Haut je Körper einmal, Stücke auf Wunsch: %s)' % (
                runde, ', '.join(sorted(getattr(modell, 'fotowuensche', None) or [])) or '–'))
            fototextur = self.werkzeug.fototextur(modell, teile, referenzen, render, bau, aus)
            for nummer, r in enumerate(referenzen):
                self._melden(0.3 + 0.4 * nummer / max(1, len(referenzen)),
                             'Runde %d: Rendern %d von %d' % (runde, nummer + 1, len(referenzen)))
                pfad = aus / ('ansicht_%+04d.png' % int(round(r.winkel)))
                render.bild_teile([(t['punkte'], t['dreiecke'], t['farbe'], Genesishaarrender.extra(t)) for t in teile],
                                  r.winkel, pfad, groesse=groesse)
                bild = Iterationsbild.aus_render(pfad)
                fein = bild if breite == Iterationsbild.BREITE else Iterationsbild.aus_render(
                    pfad, Aufloesungsstufe.groesse(breite))
                note = Iterationsnote.vergleichen(self.stufe.vorlage(r, breite), fein)
                renders[r.datei] = bild
                je_ansicht.append({'datei': r.datei, 'original': r.original, 'winkel': r.winkel, 'bild': pfad,
                                   'nur_form': not r.farbe, **note})
                paare.append((r.gewicht, note, r.farbe))
                messung.render_dazu(r, bild)
        finally:
            render.schliessen()
        foto = Iterationsnote.gesamt_getrennt(paare) if paare else {'abweichung': 0.0, 'iou': 0.0, 'farbe': 0.0}
        netz = netznote.vergleichen(teile) if netznote is not None else None
        note = dict(foto, netz=netz, foto=foto['abweichung'] if paare else None)
        note['abweichung'] = round(float(foto['abweichung'] if paare else 0.0)
                                   + self.NETZGEWICHT * float(netz['abweichung'] if netz else 0.0), 4)
        befund = messung.befund(teile)
        from iterationen2d3d.messpruefung import Messpruefung         # Punkt 3: Selbsttest und Deckung der Runde
        befund['messguete'] = Messpruefung.pruefen([(r.winkel, r.bild.maske, renders[r.datei].maske) for r in referenzen
                                                    if r.datei in renders], z['modell_hoehe'], teile[0]['punkte'])
        if fototextur:
            befund['fototextur'] = fototextur
        befund.update(haltung_foto=z.get('haltung_foto'), motor=render.motor,     # Renderer: `befund_fuer_regeln`
                      zubehoer=self.werkzeug.zubehoer(referenzen),                # Uhr usw. (`Uhrerkennung`)
                      fotostuecke=self.werkzeug.fotostuecke())                    # Kleider aus dem Netz
        from .gesichtsmasse import Gesichtsmasse    # Foto gegen Kopf-Render (01.10.2026, `IterationGesicht`)
        try:
            Gesichtsmasse(self.ablage, render).eintragen(befund, teile, referenzen, aus)
            self._melden(0.75, 'Runde %d: Prüfbilder' % runde)
            kopf = Pruefbilder(self.ablage, groesse[0]).kopf(render, teile, referenzen, z['modell_hoehe'], aus,
                                                             aus / 'kopf.png')
            Haarabgleich(self.ablage, render).eintragen(befund, teile, referenzen, z['modell_hoehe'], aus)
        finally:
            render.schliessen()
        self._melden(0.8, 'Runde %d: ablegen (Abweichung %.3f)' % (runde, note['abweichung']))
        erg = {'werte': modell.als_dict(), 'note': note, 'je_ansicht': je_ansicht, 'renders': renders,
               'teile': {t['sorte']: 1 for t in teile if t['art'] != 'koerper'}, 'befund': befund,
               'kopf': kopf, 'aufloesung': breite, 'tafelbreite': groesse[0]}
        self._ablegen(runde, erg, naechste, rezept, fehler, teile, bau, start)
        weiter = Begutachtungsstand(self).fortschreiben(z, beg, modell, runde, note, rezept, naechste, fehler, befund)
        shutil.rmtree(aus, ignore_errors=True)
        self._melden(1.0, 'Runde %d: Gesamtnote %.4f — wartet auf Begutachtung' % (runde, note['gesamt']))
        return weiter

    def _start(self):
        """Der Ausgangszustand: die Frisur, die „Mesh to 3D" als beste gemessen hat (sonst die Vorgabe), keine
        Kleider."""
        from Genesis9.haargenerisch import G9haargenerisch
        from Genesis9.modellmitkleidern import ModellMitKleidern
        modell = ModellMitKleidern()
        kandidaten = (self.job.ergebnis.get('frisur') or {}).get('kandidaten') or []
        frisur = (kandidaten[0].get('kennung') if kandidaten else None) or G9haargenerisch.VORGABE
        modell.haar_nur(frisur)
        return modell

    def _letzte_runde(self):
        ergebnis = self.job.ergebnis
        eintraege = [int(r.get('runde') or 0) for r in ergebnis.get('iterationen') or []]
        verlauf = [int(p[0]) for p in (ergebnis.get('kreislauf') or {}).get('verlauf') or [] if p]
        return max(eintraege + verlauf + [0])

    # -------------------------------------------------------------- ablegen

    def _ablegen(self, runde, erg, naechste, rezept, fehler, teile, bau, start):
        ziel = self.ablage.iterationen()
        ziel.mkdir(parents=True, exist_ok=True)
        dateien = {}
        tafel = 'runde_%03d_vergleich.png' % runde       # Prüfbilder in Prüfbreite, nicht auf der Fläche der Note
        if Pruefbilder(self.ablage, erg['tafelbreite']).tafel(
                [(a['winkel'], a['datei'], a['bild'], a['iou']) for a in erg['je_ansicht']], ziel / tafel):
            dateien['vergleich'] = tafel
        if erg.get('kopf'):
            dateien['kopf'] = 'runde_%03d_kopf.png' % runde
            shutil.copyfile(erg['kopf'], ziel / dateien['kopf'])
        je_ansicht = []
        for a in erg['je_ansicht']:
            bild = 'runde_%03d_%s' % (runde, a['bild'].name)
            if a['bild'].is_file():
                Iterationsrunde.zuschneiden(a['bild'], ziel / bild)
            je_ansicht.append({k: a[k] for k in ('original', 'winkel', 'iou', 'farbe')} | {'render': bild})
        # Keine GLB je Runde (Edgar 02.10.2026: „ich brauche kein GLB je Runde, ich brauche den Vergleich … aus den
        # gleichen Winkeln wie die Vorlagenfotos") — 56 MB je Runde; die Bühne zeigt das Standmodell des Laufs.
        dateien['formbezug'] = bau.formbezug(ziel, runde)     # Anker des Form-Pinsels (01.10.2026)
        netz = erg['note'].get('netz') or {}
        notiz = naechste.get('kommentar') or ('Ausgangslage: Frisur aus „Mesh to 3D", keine Kleider' if runde == 1
                                              else '')
        if netz:
            notiz = (notiz + ' · ' if notiz else '') + 'Netz: Stoff %s mm zum Netz, Deckung %.0f %%' % (
                netz.get('modell_mm'), 100.0 * float(netz.get('deckung') or 0))
        eintrag = {
            'runde': runde,
            'zeit': timezone.localtime().strftime('%Y-%m-%d %H:%M:%S'),
            'sekunden': round(time.perf_counter() - start, 1),
            'art': 'begutachtung' if naechste else 'ausgang',
            'uebernommen': fehler is None,
            'notiz': notiz,
            'note': erg['note'],
            'je_ansicht': je_ansicht,
            'werte': erg['werte'],
            'aenderungen': {},
            'teile': erg['teile'],
            'dateien': dateien,
            'aufrufe': naechste.get('aufrufe') or '',
            'kommentar': naechste.get('kommentar') or '',
            'automatisch': bool(naechste.get('automatisch')),
            'aufloesung': erg['aufloesung'],                   # Breite der Notenfläche (`Aufloesungsstufe`)
            'rezept': rezept,
            'befund': erg['befund'],
        }
        if fehler:
            eintrag['fehler'] = fehler
        self.job.ergebnis.setdefault('iterationen', []).append(eintrag)
