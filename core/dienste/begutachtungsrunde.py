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
    4. ablegen: Tafel, Renders, Eintrag in `ergebnis['iterationen']` (`aufrufe`, `kommentar`, `rezept`, `fehler`, `befund`), Prompts
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
from Genesis9.rezeptumgebung import Rezeptumgebung

from .ansichtsrender import Ansichtsrender
from .aufloesungsstufe import Aufloesungsstufe
from .begutachtungsausgang import Begutachtungsausgang
from .begutachtungsautomatik import Begutachtungsautomatik
from .begutachtungsbefund import Begutachtungsbefund
from .begutachtungskritik import Begutachtungskritik
from .begutachtungsstand import Begutachtungsstand
from .engine2d3dkleidergrundfigur import Engine2d3dKleidergrundfigur
from .engine2d3dkleiderprompts import Engine2d3dKleiderprompts
from .haarabgleich import Haarabgleich
from .haltungsansichten import Haltungsansichten
from .haltungsfotos import Haltungsfotos
from .iterationsbild import Iterationsbild
from .iterationsnetznote import Iterationsnetznote
from .iterationsnote import Iterationsnote
from .iterationsoptionen import Iterationsoptionen
from .iterationsoptionenfoto import Iterationsoptionenfoto
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
        vorlauf, ohne_rezept = 0, not (naechste.get('aufrufe') or naechste.get('automatisch'))
        erste = not quelle and Begutachtungsausgang.fehlt(self.job)
        if Begutachtungsausgang.verlangt(naechste) or (erste and ohne_rezept):         # Iteration 0: auf Bestellung, oder als Ausgangslage („Neu berechnen" ohne Rezept)
            return self._ausgang(z, beg, referenzen)
        runden = 1
        if naechste.get('automatisch'):
            runden = max(1, min(self.RUNDEN_HOECHSTENS, int(naechste.get('runden') or 1)))
        if erste:               # die erste Runde mit Rezept: erst Iteration 0 — Vorlage und Modell, vor jeder Änderung
            vorlauf, self._lage = 1, (0, runden + 1)
            modell = self._runde(z, beg, modell, Begutachtungsausgang.bestellung(self.job), referenzen)
        grund = naechste.get('kommentar') or 'automatisch (IterationModell)'
        for i in range(runden):
            if i and self.lauf.angehalten():
                break
            self._lage = (i + vorlauf, runden + vorlauf)
            if naechste.get('automatisch'):
                neu = None if z.get('weiter') else self.stufe.faellig(z, referenzen)     # Stillstand in der Stufe
                aufrufe, zusatz, fertig = ('', 'Stillstand', False) if neu else Begutachtungsautomatik(self).rezept(modell, z, referenzen)
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

    def _runde(self, z, beg, modell, naechste, referenzen):
        from Genesis9.modellrezept import G9rezept

        from .genesishaarrender import Genesishaarrender
        from .kleidermodellbau import Kleidermodellbau
        start = time.perf_counter()
        runde = Begutachtungsausgang.RUNDE if Begutachtungsausgang.verlangt(naechste) else self._letzte_runde() + 1
        rezept, fehler = [], None
        # Der Sichtkörper der Vorlagen (Konzept 4.1) steht dem Rezept zur Verfügung (`kleid_huelle`, `koerper_huelle`)
        # — gebaut aus den Silhouetten der Note und der Höhe des Modells der LETZTEN Runde (erste Runde: Körper).
        sicht = self.werkzeug.sichtkoerper(referenzen, z)
        modell.umgebung = Rezeptumgebung(sicht, self.werkzeug.drapierer(), auftrag=Rezeptumgebung.kuerzel(self.job.kennung),
                                         haardynamik=self.werkzeug.haardynamik(), stellung=self.job.stellung(),
                                         seitenprofil=lambda: self.werkzeug.seitenprofil(referenzen, z))
        if naechste.get('aufrufe'):
            try:
                rezept = [text for _zeile, text in G9rezept.anwenden(modell, naechste['aufrufe'])]
            except ValueError as f:
                fehler = str(f)
                logger.warning('2D3D Kleider %s: Rezept der Runde %d: %s', self.job.kennung, runde, fehler)
        self._melden(0.1, 'Runde %d: Modell bauen' % runde)
        # Gebaut in der A-Pose (GLB, Bühne); Render, Note, Befund und Fotoprojektion in der Haltung der Fotos — gehäutet, damit die Ärmel den Armen folgen (`G9haltungshaut`, 01.10.2026),
        # mit der Hose aus dem Körpernetz (`Hosenteil`, 04.10.2026) und je Foto in dessen eigener Haltung, wo sie sich unterscheidet (`Haltungsansichten`, 08.10.2026).
        bau = Kleidermodellbau(self.job.stellung(), None, koerper=modell.koerper, kacheln=self.werkzeug.kacheln(), ablage=self.ablage,
                               haarumbau=Iterationsoptionen.haarart(self.o.get('haarumbau')))
        ansichten = Haltungsansichten.bauen(modell, bau, referenzen, z.get('haltung_foto'), self.ablage.arbeit('runden') / ('runde_%04d' % runde),
                                            je_foto=Iterationsoptionenfoto.haltung_je_foto(self.job))
        teile = ansichten.teile
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
                messung.masken(render, ansichten.von(r), r, aus / ('kennung_%+04d.png' % int(round(r.winkel))), befundgroesse)
            self._melden(0.25, 'Runde %d: Fotoprojektion (Haut je Körper einmal, Stücke auf Wunsch: %s)' % (
                runde, ', '.join(sorted(getattr(modell, 'fotowuensche', None) or [])) or '–'))
            fototextur = self.werkzeug.fototextur(modell, teile, referenzen, render, bau, aus, ansichten)
            pfade, faktoren = Ansichtsrender.rendern(render, teile, referenzen, aus, groesse, self._melden, runde,
                                                     abgleichen=self.o.get('belichtung') != 'aus', teile_von=ansichten.von)   # Belichtung je Ansicht an das Foto (06.10.2026)
            for r, pfad, faktor in zip(referenzen, pfade, faktoren):
                bild = Iterationsbild.aus_render(pfad)
                fein = bild if breite == Iterationsbild.BREITE else Iterationsbild.aus_render(
                    pfad, Aufloesungsstufe.groesse(breite))
                note = Iterationsnote.vergleichen(self.stufe.vorlage(r, breite), fein)
                renders[r.datei] = bild
                je_ansicht.append({'datei': r.datei, 'original': r.original, 'winkel': r.winkel, 'bild': pfad,
                                   'nur_form': not r.farbe, 'belichtung': round(faktor, 3), **note})
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

    def _ausgang(self, z, beg, referenzen):
        """Iteration 0 (`Begutachtungsausgang`): das Modell der Ausgangslage neben den Fotos. Hat der Auftrag schon Runden, bleibt ihr Stand, wie er war."""
        nachtraeglich = not Begutachtungsausgang.fehlt(self.job)
        vorher = Begutachtungsausgang.vorher(self.job) if nachtraeglich else None
        self._runde(z, beg, self._start(), Begutachtungsausgang.bestellung(self.job), referenzen)
        if nachtraeglich:
            Begutachtungsausgang.nachher(self.job, vorher)
            self.lauf.sichern('ergebnis')

    def _start(self):
        """Der Ausgangszustand: die Frisur, die „Mesh to 3D" als beste gemessen hat (sonst die Vorgabe), keine Kleider."""
        from Genesis9.haargenerisch import G9haargenerisch
        from Genesis9.modellmitkleidern import ModellMitKleidern
        kandidaten = (self.job.ergebnis.get('frisur') or {}).get('kandidaten') or []
        modell = ModellMitKleidern()
        modell.haar_nur((kandidaten[0].get('kennung') if kandidaten else None) or G9haargenerisch.VORGABE)
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
                [(a['winkel'], a['datei'], a['bild'], a['iou'], a.get('belichtung', 1.0)) for a in erg['je_ansicht']], ziel / tafel):
            dateien['vergleich'] = tafel
        if erg.get('kopf'):
            dateien['kopf'] = 'runde_%03d_kopf.png' % runde
            shutil.copyfile(erg['kopf'], ziel / dateien['kopf'])
        je_ansicht = []
        for a in erg['je_ansicht']:
            bild = 'runde_%03d_%s' % (runde, a['bild'].name)
            if a['bild'].is_file():
                Iterationsrunde.zuschneiden(a['bild'], ziel / bild)
            je_ansicht.append({k: a[k] for k in ('original', 'winkel', 'iou', 'farbe')} | {'render': bild, 'belichtung': a.get('belichtung', 1.0)})
        # Keine GLB je Runde (Edgar 02.10.2026: 56 MB je Runde, gebraucht wird der Vergleich); die Bühne zeigt das Standmodell.
        dateien['formbezug'] = bau.formbezug(ziel, runde)     # Anker des Form-Pinsels (01.10.2026)
        netz = erg['note'].get('netz') or {}
        notiz = naechste.get('kommentar') or ''
        if netz:
            notiz = (notiz + ' · ' if notiz else '') + 'Netz: Stoff %s mm zum Netz, Deckung %.0f %%' % (
                netz.get('modell_mm'), 100.0 * float(netz.get('deckung') or 0))
        eintrag = {
            'runde': runde,
            'zeit': timezone.localtime().strftime('%Y-%m-%d %H:%M:%S'),
            'sekunden': round(time.perf_counter() - start, 1),
            'art': 'begutachtung' if naechste and not Begutachtungsausgang.verlangt(naechste) else 'ausgang',
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
        Engine2d3dKleiderprompts(self.ablage).runde(eintrag, naechste.get('nutzer'))     # Kommentar und Nachrichten der Runde
