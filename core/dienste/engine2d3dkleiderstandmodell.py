# -*- coding: utf-8 -*-
"""Engine2d3dKleiderstandmodell — das 3D-Modell des LETZTEN Stands eines Auftrags „2D3D Kleider" als fertige GLB
(01.10.2026).

Edgar: „das laden des 3d modells dauert immer lange, meldung: es wird gebaut. Baue beim letzten stand ein 3d modell
(Genesis mit assets) und lades es gleich, das muss schnell gehen."

Der Stand: die Stellung des Auftrags (Körper-Fit), darüber die Körper- und Gesichtsregler der Iterationen
(`kreislauf.modell.koerper`, wie `Engine2d3dKleiderexport.stellung`), die gebackenen Kacheln samt Augenbild und — wenn
Iterationen gelaufen sind — Kleider und Haar des Modells der letzten Runde (`kreislauf.modell`). Geschrieben wird es
von `Standmodellglb`; gebaut im Arbeitsprozess (am Ende eines Laufs, `Engine2d3dKleiderlauf._standmodell`, oder einzeln über
`manage.py engine2d3dkleider_standmodell`), nie im Server — die Bühne lädt nur noch die Datei.

Ablage (Regel artefakte-benennen): `ergebnis/stand_<fassung>.glb` und `ergebnis/stand.json`. Die Fassung ist der
Fingerabdruck des Stands; ändert er sich (neue Runde, neue Kacheln, neuer Schreiber), ist die Datei veraltet
(`eintrag()['aktuell']`) und wird neu gebaut. Die Seite lädt `?v=<fassung>` — der Browser behält die Datei, bis sich
der Stand ändert.
"""

import hashlib
import json
import logging
import os
import time

from ..daten.engine2d3dkleiderablage import Engine2d3dKleiderablage
from .standhaut import Standhaut
from .standvorabkleider import Standvorabkleider

logger = logging.getLogger('core')

__all__ = ['Engine2d3dKleiderstandmodell']


class Engine2d3dKleiderstandmodell:
    BERICHT = 'stand.json'
    #: Ein gescheiterter Bau dieser Fassung (`{fassung, fehler}`) — die Bühne baut die Figur dann im Browser.
    FEHLER = 'stand_fehler.json'
    MUSTER = 'stand_%s.glb'
    #: Gehört zur Fassung: Ändert sich der Schreiber (`Standmodellglb`), werden alte Dateien neu gebaut.
    #: 8 (04.10.2026): weiße Hose mit Falten (`Hosenfalten`) und ohne Flecken (`Stoffweissung`).
    #: 9 (04.10.2026): Seitenstreifen der Vorlage aus der Geometrie auf der Hose (`Hosenstreifen`).
    #: 10 (04.10.2026): Hose aus dem Körpernetz statt aus den Schnittbahnen (`Hosenkoerper`: geschlossen, lockerer, Hautgewichte des Körpers, Streifen im Hosenbild).
    #: 11 (04.10.2026): Hose aus dem VERSCHWEISSTEN Körpernetz (die UV-Nähte hatten Beine und Rumpf zu Inseln getrennt: nur ein Hosenstummel).
    #: 12 (04.10.2026): Ringmitte der Hose als Fenstermittel (glatter Streifen), stärkere Glättung, kräftigere Falten.
    #: 13 (04.10.2026): Hose lockerer (Saum 20 mm, Oberschenkel 30 mm), Schrittwölbung stärker geglättet.
    #: 14 (04.10.2026): Hose etwas schmaler (Oberschenkel 22 mm statt 30).
    #: 15 (04.10.2026): Hautdetails der Arme und Hände (`Standhandhaut`: Normalenkarte `normalTexture` + Farbvariation der Armkachel 1004).
    #: 16 (04.10.2026): Hemd geputzt (`Netzputz`: Löcher am Ärmel geschlossen, Saum und Ärmelenden geglättet).
    #: 17 (04.10.2026, Edgar: „Beine viel zu dick"): Hose enger an der Haut (Oberschenkel 12, Knie 8, Wade 10 mm statt 22/14/16), Falten schwächer (`Hosenfalten`).
    #: 18 (04.10.2026, Edgar: „riesen Geschlechtsteil", graue Flecken): Die Hose liegt überall mindestens 7 mm AUSSERHALB der Körperfläche (`Hosenkoerper._ausserhalb`) —
    #: vorher drückte der Körper im Schritt bis 43 mm durch.
    #: 19 (04.10.2026): Der Stand zeigt die LETZTE übernommene Runde statt der besten nach Note (`_kreislaufmodell`).
    #: 20 (04.10.2026, Edgar zum dritten Mal: „Haar oben viel zu lang", „Haar seitlich braun", „Textur bei Beinen und Armen verwaschen", „Hände wie angenäht", „T-Shirt verfranst"): Die Frisur ist an die Hülle des
    #: Fotohaars geklemmt (`Haarklemme`), ihre Strähnengruppen sind angeglichen, das Oberteil ist vor den Iterationen das Genesis-Hemd (Option `koerper.oberteil`), die Hand hat den Ton des Unterarms
    #: (`Standhandangleich`), Beine und Arme zeigen ruhigere Flecken mit feiner Zeichnung (`Standhautdetail`).
    #: 21 (05.10.2026, Edgar zum vierten Mal: „Unterhose ist viel zu weit, in der Vorlage ist sie eng anliegend", „Haar immer noch zu hoch in der Mitte", „Haare seitlich braun, ein Haarmodell, das alles beinhaltet
    #: und eine einheitliche Farbe hat"): Die Hose der Fotostücke liegt eng am Körper an (`Standhose`), das Haar vor den Iterationen ist EINE Haarkappe in der Haarfarbe der Fotos (`Haarkappe`).
    #: 22 (05.10.2026, Edgar: „diese Unterhose ist total aufgebläht, sie muss am Körper liegen"): Die enge Hose liegt 4 statt 8 mm über der Haut und wird kaum noch geglättet (`Hosenkoerper.ABSTAND_ENG`).
    #: 23 (05.10.2026, Edgar: „das Haar der Vorlage perfekt auf ein Haar aus Genesis umbauen"): Das Haar der Runden ist an der Haarlinie geschnitten und sitzt auf der Haarkappe (`Haarumbau`); Kopfkachel
    #: bleibt gebacken, Fotohaut Fassung 2 (`Koerperfotoprojektion`).
    #: 24 (05.10.2026, Edgar: „Haar ist eine Linie über den Ohren", „ein Haar für einen normalen mittelalten Mann"): Haarlinie nach Ohr, Koteletten und Nacken (`Haarlinie`), das Haar vor den Iterationen ist das eigene Kurzhaar (`Herrenhaar`).
    #: 25 (07.10.2026, Edgar: „mach alle 5" — Prioliste aus „Andere Modelle"): Die Haut des Körpers (`Standhaut`): Hautsatz nach Grundfigur (masculine → `G9 Masculine Skin 01 MAT`), Kacheln 2048² (Kopf 4096²)
    #: statt 1024², die Daz-Normalenkarte je Kachel als `normalTexture` (auf den Armen unter dem Handrelief).
    SCHREIBER = 25

    def __init__(self, job, ablage=None):
        self.job = job
        self.ablage = ablage or Engine2d3dKleiderablage(job.kennung)

    # ------------------------------------------------------------------ Stand

    def _beste(self):
        """Die BESTE Runde der Iterationen (`kreislauf.runde_bester`, nach `Rundenauswahl`) mit ihrem Modell — None ohne Runde oder ohne Angabe.

        `uebernommen` heißt nur „ohne Fehler"; eine verworfene oder nur probeweise Runde ist nicht der Stand (06.10.2026: Runde 5 einer Probe mit 0,4255
        gegen beste Runde 3 mit 0,4021). Der Stand ist, was auch Export, Film und Speichern lesen."""
        erg = self.job.ergebnis or {}
        nummer = (erg.get('kreislauf') or {}).get('runde_bester')
        beste = [r for r in (erg.get('iterationen') or []) if r.get('werte') and nummer is not None and r.get('runde') == nummer]
        return beste[-1] if beste else None

    def _kreislaufmodell(self):
        """Das Modell des Stands: das der BESTEN Runde (06.10.2026, Edgar: „die Bühne soll das beste Modell zeigen"). Am 04.10.2026 war es die LETZTE Runde
        („Modell ist nicht wie die letzte Iteration"); die zeigte am 06.10. in `…14.10.22` eine Probe (Runde 5, 0,4255) schlechter als jede andere Runde.
        Ohne Runde bleibt `kreislauf.modell` — das Begutachtungsstand schon auf die beste Runde setzt."""
        beste = self._beste()
        return (beste or {}).get('werte') or ((self.job.ergebnis or {}).get('kreislauf') or {}).get('modell') or None

    def stellung(self):
        stellung = dict(self.job.stellung() or {})
        stellung.update({str(k): v for k, v in ((self._kreislaufmodell() or {}).get('koerper') or {}).items()})
        return stellung

    def baubar(self):
        return bool(self.job.stellung())

    def _beste_runde(self):
        """Die Runde, aus der der Stand kommt: die beste (`_beste`), sonst `kreislauf.runde_bester`."""
        beste = self._beste()
        return beste['runde'] if beste else ((self.job.ergebnis or {}).get('kreislauf') or {}).get('runde_bester')

    def fassung(self):
        """Fingerabdruck des Stands — 12 Zeichen. Mit der besten Runde: Eine neue Runde kann Stoff, Zubehör und Maße des Modells ändern,
        ohne dass `kreislauf.modell` (Körperwerte, Stücke) sich ändert — Runde 53 (Hemd anliegend, 04.10.2026) baute `stand_3e76741ccddd.glb`
        unter demselben Namen neu, und ein offener Tab behielt die alte Datei aus dem Browser-Cache (`artefakte-benennen`).

        07.10.2026, Edgar 8: derselbe Fehler nochmal, andere Ursache — ein `eigen:<kennung>`-Regler wird unter DEMSELBEN
        Namen neu abgelegt (Direktmorph-Nachbesserung), `self.stellung()` liefert `{regler: wert}` unveraendert, die
        Fassung blieb bitgleich (`486a5147eb22` vor UND nach dem Mund-Fix) — der Browser behielt die kaputte Datei unter
        derselben `?v=`-URL fuer immer. `G9formung.fingerabdruck()` hat das schon fuer SEINEN Cache geloest
        (`G9eigenmorphe.dateistand`); hier fehlte dieselbe Absicherung."""
        f = (self.job.ergebnis or {}).get('fototextur') or {}
        teile = [self.SCHREIBER, self.stellung(), self._eigen_dateistand(), self._kreislaufmodell(), f.get('kacheln'), f.get('augen'),
                 f.get('stand'), self._beste_runde(), self._zubehoer(), Standhaut.fassung(self.job)]
        schichten = self._fotoschichten()
        if schichten:                       # nur mit Fotoschichten: Aufträge ohne sie behalten ihre Fassung
            teile.append(schichten)
        # Vor den Iterationen tragen die Fotostücke (Schritt „Kleiderstücke") die Kleider — nur dann zählen sie zur Fassung, die Fassung der Aufträge mit Iterationen bleibt dieselbe.
        vorab = None if self._kreislaufmodell() else Standvorabkleider.fingerabdruck(self.job)
        roh = json.dumps(teile + ([vorab] if vorab else []), sort_keys=True, default=str)
        return hashlib.md5(roh.encode('utf-8')).hexdigest()[:12]

    def _eigen_dateistand(self):
        """`[(reglername, dateistand_ns)]` je `eigen:`-Regler der Stellung — sortiert, fuer die Fassung (siehe `fassung()`,
        07.10.2026). Ohne das aendert sich die Fassung NICHT, wenn ein Eigenmorph unter demselben Namen neu abgelegt wird."""
        from Genesis9.eigenmorphe import G9eigenmorphe
        return sorted(
            (k, G9eigenmorphe.dateistand(k)) for k in self.stellung() if G9eigenmorphe.ist_eigen(k)
        )

    def _fotoschichten(self):
        """Die Atlanten der Fotoschichten DIESES Auftrags (`kleidtexturen/*foto_<kürzel>_f*.png`) als `[(Name, Größe, Änderungszeit)]` — leer ohne sie.
        Das Modell der Runde nennt nur den Regler `bild.foto_<kürzel>` (immer 1,0), nicht den Inhalt des Atlas: `stand_ab281e7b38b5.glb` von „Edgar - Sapiens 4"
        (06.10.2026) trug das Hemd weiß, ohne Foto und ohne die Farbe des Saums, und blieb es unter derselben Fassung, obwohl der heutige Bau dasselbe Modell mit
        Foto baut (Hemdtextur Mittel 191 gegen 82/78/76); eine neu gerechnete Schicht änderte die Fassung ebenso wenig."""
        from Genesis9.kleidtexturen import G9kleidtexturen
        from Genesis9.rezeptumgebung import Rezeptumgebung
        kuerzel = Rezeptumgebung.kuerzel(self.job.kennung)
        ordner = G9kleidtexturen.ordner()
        if not kuerzel or not ordner.is_dir():
            return []
        return sorted((p.name, p.stat().st_size, p.stat().st_mtime_ns) for p in ordner.glob('*foto_%s_f*.png' % kuerzel))

    @staticmethod
    def _zubehoer():
        """Name und Änderungszeit der eigenen Zubehör-Stücke (`<Bibliothek>/data/EIGEN/*/*.dsf`: Hut, Federn, Stiefel, Manschetten …): Wer ein Stück neu schreibt, ohne dass sich
        eine Runde ändert, bekam bis 04.10.2026 dieselbe Fassung und damit dieselbe Datei (Federn und Hut der Bühne blieben alt). Fehlt der Ordner, bleibt die Liste leer."""
        try:
            from Genesis9.pfade import G9pfade
            ordner = G9pfade.eigene() / 'data' / 'EIGEN'
            return [[p.parent.name, p.stat().st_mtime_ns] for p in sorted(ordner.glob('*/*.dsf'))] if ordner.is_dir() else []
        except (ImportError, OSError) as fehler:
            logger.info('Stand-Fassung: Zubehör-Dateien nicht gelesen (%s)', fehler)
            return []

    def bericht(self, name=BERICHT):
        pfad = self.ablage.ergebnis(name)
        try:
            return json.loads(pfad.read_text(encoding='utf-8')) if pfad.is_file() else None
        except (OSError, ValueError) as fehler:
            logger.warning('2D3D Kleider %s: %s nicht lesbar (%s)', self.job.kennung, pfad.name, fehler)
            return None

    def eintrag(self):
        """Für den Zustand der Seite: None, solange es keine Figur gibt; sonst `{datei, fassung, aktuell, bytes, …}`
        — `datei` None, wenn noch keine gebaut ist; `fehler`, wenn der Bau DIESER Fassung gescheitert ist."""
        if not self.baubar():
            return None
        jetzt = self.fassung()
        b = self.bericht() or {}
        if not b.get('datei') or not self.ablage.ergebnis(b['datei']).is_file():
            b = {'datei': None}
        # `fassung`: die der Datei (die Seite lädt sie mit `?v=`); `soll`: die des Stands — darauf bestellt die Seite.
        aus = dict(b, fassung=b.get('fassung') or jetzt, soll=jetzt,
                   aktuell=bool(b.get('datei')) and b.get('fassung') == jetzt)
        f = self.bericht(self.FEHLER) or {}
        if f.get('fassung') == jetzt and not aus['aktuell']:
            aus['fehler'] = f.get('fehler') or 'unbekannt'
        return aus

    def scheitern(self, fehler):
        """Den Fehler dieser Fassung merken — die Seite bestellt sie dann nicht wieder und baut im Browser."""
        try:
            self.ablage.ergebnis(self.FEHLER).write_text(
                json.dumps({'fassung': self.fassung(), 'fehler': str(fehler)[:500]}, ensure_ascii=False),
                encoding='utf-8')
        except OSError as nicht:
            logger.warning('2D3D Kleider %s: Fehler des Modells nicht gemerkt (%s)', self.job.kennung, nicht)

    # ------------------------------------------------------------------ Bauen

    def _kacheln(self):
        aus = {}
        for k, name in (((self.job.ergebnis or {}).get('fototextur') or {}).get('kacheln') or {}).items():
            if str(k).isdigit() and self.ablage.ergebnis(name).is_file():
                aus[int(k)] = str(self.ablage.ergebnis(name))
        return aus

    def _augenbild(self):
        name = ((self.job.ergebnis or {}).get('fototextur') or {}).get('augen')
        return str(self.ablage.ergebnis(name)) if name and self.ablage.ergebnis(name).is_file() else None

    def bauen(self):
        """`ergebnis/stand_<fassung>.glb` schreiben → Bericht (steht auch in `stand.json`)."""
        from Genesis9.charaktere import G9charaktere
        from Genesis9.formung import G9formung
        from Genesis9.koerpernetz import G9koerpernetz

        from .standmodellglb import Standmodellglb
        if not self.baubar():
            raise ValueError('Noch keine Figur — erst nach dem Schritt „Körper"')
        t = time.perf_counter()
        fassung = self.fassung()
        # Die Netze bleiben in der A-Pose (`{}`); die Haltung der Iterationen kommt unten als Gelenkdrehung dazu (`Standhaltung`). Sie in den
        # Bau des Körpers zu geben (Versuch 03.10.2026) ließ den Körper gesenkt, aber Hemd, Hose, Stiefel und Zubehör in der A-Pose stehen.
        netz = G9koerpernetz(G9formung.aus_abfrage(self.stellung(), {}), G9charaktere.eintrag('basis'),
                             hautpreset=Standhaut.preset(self.job), anhaenge=True, stufen=0).bauen()      # der Hautsatz folgt der Grundfigur (`Standhaut`)
        glb = Standmodellglb(netz['skelett']['knochen'])
        glb.hautdetail = not self._kreislaufmodell()        # ruhigere Haut (`Standhautdetail`) nur vor den Iterationen: eine laufende Reihe soll ihren Film nicht ändern
        kacheln = self._kacheln()
        glb.koerper(netz, kacheln)
        daten = self._kreislaufmodell()
        from .brauenfarbe import Brauenfarbe  # Brauen/Wimpern in der Haarfarbe (statt Daz-Schwarz)
        from .koerperanhaenge import Koerperanhaenge
        Brauenfarbe().anwenden(netz, ((daten or {}).get('farben') or {}).get('haar'))
        if Koerperanhaenge.brauen_gemalt(kacheln):          # Fotohaut im Kopf: die Brauen stehen im Gesicht
            netz['anhaenge'] = [a for a in netz.get('anhaenge') or [] if a.get('schluessel') != 'brauen']
        glb.anhaenge(netz, self._augenbild())
        teile = []
        # Ohne Iteration die Fotostücke des Schritts „Kleiderstücke" (`Standvorabkleider`) — nur Kleidung, kein Standardhaar, A-Pose; das Haar ist die Haarkappe, wenn die Hülle des Fotohaars da ist.
        kappe = None if daten else self._haarkappe(netz)
        vorab = None if daten else Standvorabkleider.modell(self.job, ohne_haar=kappe is not None)
        if daten or vorab:
            from Genesis9.modellmitkleidern import ModellMitKleidern

            from .haarzonen import Haarzonen
            from .kleidermodellbau import Kleidermodellbau
            modell = ModellMitKleidern.aus(daten or vorab)
            from .iterationsoptionen import Iterationsoptionen
            bau = Kleidermodellbau(self.job.stellung(), None, koerper=modell.koerper, ablage=self.ablage,
                                   haarumbau=bool(daten) and Iterationsoptionen.haarumbau(self.job), ohne_haar=bool(vorab) and kappe is not None)
            teile = [x for x in Haarzonen.anwenden(bau.teile(modell), modell.farben) if x.get('art') != 'koerper']
            if vorab:
                teile = [x for x in teile if x.get('art') in Standvorabkleider.ARTEN]       # Kleidung UND die gewählte Frisur (websites-40, 04.10.2026)
                if kappe is not None:       # das eigene Haar (Kappe oder Herrenhaar, eine Liste von Teilen) ersetzt die Kopfhaare, nicht den Bart
                    teile = [x for x in teile if x.get('art') != 'haar' or any(o in str(x.get('sorte')) for o in ('_beard',))] + kappe
            glb.teile(teile)
        if daten:
            # Die Haltung der Iterationen als Drehung der Gelenkknoten (`Standhaltung`): Netze und Bindematrizen bleiben in der A-Pose.
            from Genesis9.haltungshaut import G9haltungshaut

            from .standhaltung import Standhaltung
            haltung = Standhaltung.anwenden(glb, G9haltungshaut(bau.stellung, modell.drehung(), bau.boden), bau.boden)
            logger.info('2D3D Kleider %s: Haltung der Iterationen auf %d Gelenke gelegt', self.job.kennung, haltung)
        name = self.MUSTER % fassung
        ziel = self.ablage.ergebnis(name)
        ziel.parent.mkdir(parents=True, exist_ok=True)
        zwischen = ziel.with_name(name + '.teil')
        laenge = glb.schreiben(zwischen)
        os.replace(zwischen, ziel)
        bericht = {'datei': name, 'fassung': fassung, 'bytes': int(laenge),
                   'sekunden': round(time.perf_counter() - t, 1), 'knochen': len(glb.knochen),
                   'knochen_ohne_gelenk': sorted(glb.fehlend), **glb.zahl,
                   'teile': sorted({'%s:%s' % (x.get('art'), x.get('sorte')) for x in teile}),
                   # Der Stand ist die LETZTE übernommene Runde (seit 04.10.2026; davor die beste nach Note, `Begutachtungsstand`, 01.10.2026).
                   'runde': self._beste_runde() or ((self.job.ergebnis or {}).get('kreislauf') or {}).get('letzte_runde')}
        zettel = self.ablage.ergebnis(self.BERICHT + '.teil')
        zettel.write_text(json.dumps(bericht, ensure_ascii=False, indent=1), encoding='utf-8')
        os.replace(zettel, self.ablage.ergebnis(self.BERICHT))
        self.ablage.ergebnis(self.FEHLER).unlink(missing_ok=True)
        self._aufraeumen(name)
        logger.info('2D3D Kleider %s: Modell des Stands %s (%.1f MB, %d Netze, %.1f s)', self.job.kennung, name,
                    laenge / 1e6, glb.zahl['netze'], bericht['sekunden'])
        return bericht

    def _haarkappe(self, netz):
        """Das Haar vor den Iterationen als Liste von Teilen: bei der Option `haarumbau = herren` das eigene Kurzhaar (`Herrenhaar`: Kappe und Strähnen), sonst EIN Teil in EINER Farbe über dem ganzen Haarbereich (`Haarkappe`) —
        None ohne Hülle des Fotohaars oder ohne Haarfarbe (dann trägt der Stand die Frisur der Garderobe). Ein Fehler hält den Bau nicht auf."""
        from .haarkappe import Haarkappe
        from .herrenhaar import Herrenhaar
        from .iterationsoptionen import Iterationsoptionen
        try:
            rgb = Standvorabkleider.kappenfarbe(self.job)
            if not rgb:
                return None
            if Iterationsoptionen.haarumbau(self.job) == 'herren':
                herren = Herrenhaar(self.ablage, netz, laenge=Iterationsoptionen.haarlaenge(self.job))
                return herren.teile(rgb) if herren.kappe.kurzhaarig() else None
            teil = Haarkappe(self.ablage, netz).teil(rgb)
            return [teil] if teil is not None else None
        except Exception:  # noqa: BLE001 — ohne Kappe bleibt die Frisur der Garderobe
            logger.exception('2D3D Kleider %s: Haarkappe nicht gebaut', self.job.kennung)
            return None

    def _aufraeumen(self, behalten):
        """Ältere Fassungen weg — eine, die der Server gerade ausliefert, bleibt bis zum nächsten Bau liegen."""
        for pfad in self.ablage.ergebnis().glob(self.MUSTER % '*'):
            if pfad.name == behalten:
                continue
            try:
                pfad.unlink()
            except OSError as fehler:
                logger.info('2D3D Kleider %s: %s bleibt vorerst (%s)', self.job.kennung, pfad.name, fehler)
