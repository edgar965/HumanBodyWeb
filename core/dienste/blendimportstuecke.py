# -*- coding: utf-8 -*-
"""Blendimportstuecke — Kleider und Haar einer .blend als eigene Genesis-9-Stücke in der Bibliothek.

Derselbe Weg wie `Fotostuecke` (Form „netz"): Punkte des Stücks → Ruhelage der Figur (`Blendimportlage`) → OBJ mit
Textur → `G9eigenstueck.schreiben` (Gewichte der 3 nächsten Hautpunkte; die Gewichte der .blend gehören zu einem
anderen Rig und fallen weg) → Ruhelage auf der GRUNDFIGUR zurückrechnen (`G9gcfigurbau.ruhelage`) → neu schreiben. So
passt das Stück jeder Genesis-Figur und folgt allen Körpermorphs (`G9folger`); Kleider bekommen die Passform-Regler
(Länge, Weite), Frisuren die Haarachsen — beides von selbst über die Garderobe.

Das Haar hängt im Original nur am Kopfknochen (alle 34.637 Punkte tragen Gewicht allein in `head.x`, 0,77–0,85, gemessen
08.10.2026): Es geht starr mit dem Kopf in die Ruhelage
(`Blendimportlage.kopf_starr`) und wird ganz an `head` gebunden, Art `Hair` — wie `Herrenhaarstueck`. Sein Alpha-Bild
kommt als `alpha_bild` ins Material.

Kategorie: Kleider über `G9mbkategorien.fuer(ordner, Name)` (Ordner aus `Blendimportrollen.kategorie`), das Haar
`Follower/Hair`. Namen: „<Figur> <Art>" (z. B. „cute girl Shorts") — die Namensregel von `G9dazkategorien` greift.

Die Scham (Einstellung `scham` = `objekt`): der Teil des Körpers, den die Figur nicht trägt, als Stück „<Name> Scham" unter Zubehör
(`scham_stueck`, `Blendimportscham`) — ohne Abstimmung der Flächenrichtung gegen die Haut und mit `haut_tiefe_mm` neben der `.duf`.
"""

import logging

import numpy as np

from .blendimportbilder import Blendimportbilder
from .blendimportfuss import Blendimportfuss
from .blendimportlage import Blendimportlage
from .blendimportpruefung import Blendimportpruefung
from .blendimportrequisit import Blendimportrequisit
from .blendimportschamgewichte import Blendimportschamgewichte
from .blendimportteile import Blendimportteile

logger = logging.getLogger('core')

__all__ = ['Blendimportstuecke']


class Blendimportstuecke:
    HAAR_KATEGORIE = ('Follower/Hair', '/Default/Hair')
    #: Die Originalaugen stehen unter „Zubehör"; was sie ersetzen, sagt die Datei neben der `.duf` (`G9stueckersatz`).
    AUGEN_KATEGORIE = ('Follower/Accessory', '/Default/Accessories')
    #: Name des Stücks je Rolle/Art: „<Figur> <Zusatz>".
    HAAR_ZUSATZ = 'Haar'
    AUGEN_ZUSATZ = 'Augen'
    SCHAM_ZUSATZ = 'Scham'
    GENITAL_ZUSATZ = 'Genitalien'
    #: Blenders Augen haben Rauheit 0 (Hornhaut): als `shininess` an den Schreiber, der daraus Rauheit 0,05 macht.
    AUGEN_GLANZ = 0.95
    #: Folgt das geschriebene Stück dem Ziel schlechter als so (p99, mm), rechnet ein zweiter Durchgang gegen die gelesene Datei nach.
    NACHRECHNEN_MM = 3.0
    BROWSER_FORMATE = Blendimportbilder.BROWSER_FORMATE

    def __init__(self, ablage, job, inventar, rollen, figurname, melden=None, augen='original', zusatz=None, scham='aus'):
        self.ablage = ablage
        self.job = job
        self.inventar = {n['name']: n for n in inventar['netze']}
        self.rollen = rollen
        self.figurname = figurname
        self.melden = melden or (lambda anteil, text: None)
        self.lage = Blendimportlage(job, zusatz)
        self._fuss = None
        self._pruefung = None
        #: Der Kontaktbogen aller geprüften Stücke (`Blendimportbogen`) nach `bauen()` — None ohne.
        self.bogen_pfad = None
        #: `objekt`: die Originalaugen werden ein eigenes Stück (Einstellung „Augen" des Dialogs).
        self.augen_objekt = augen == 'objekt'
        #: `objekt`: der Teil des Körpers, den die Figur nicht trägt, wird das Stück „<Name> Scham" (`Blendimportscham`);
        #: `mann`: dasselbe Stück als „<Name> Genitalien" mit `anatomie = penis` — ohne die weiblichen Scham-Regler.
        self.scham_objekt = scham in ('objekt', 'mann')
        self.anatomie = 'penis' if scham == 'mann' else 'scham'

    def _netz(self, rolle):
        """Das Netz einer Rolle; eine Rolle mit mehreren Netzen (`namen`: beide Augen) wird zu EINEM zusammengelegt."""
        teile = []
        for name in rolle.get('namen') or [rolle['name']]:
            with np.load(self.ablage.export(self.inventar[name]['datei'])) as d:
                teile.append({k: d[k] for k in d.files})
        if len(teile) == 1:
            return teile[0]
        anfang = np.cumsum([0] + [len(t['punkte']) for t in teile[:-1]])
        return {'punkte': np.concatenate([t['punkte'] for t in teile]),
                'dreiecke': np.concatenate([t['dreiecke'] + int(a) for t, a in zip(teile, anfang, strict=True)]),
                'uv_ecken': np.concatenate([t['uv_ecken'] for t in teile])}

    def fuss(self):
        """Die Absatzhaltung der Füße (`Blendimportfuss`), einmal je Lauf — None ohne Körper."""
        if self._fuss is None:
            koerper = next((r for r in self.rollen if r['rolle'] == 'koerper'), None)
            if koerper is None:
                return None
            d = self._netz(koerper)
            _, teile = self.lage.koerper_ruhelage(d['punkte'], d['dreiecke'], mit_teilen=True)
            schuhe = [self.lage.ins_netz(self._netz(r)['punkte']) for r in self.rollen if r.get('ordner') == 'shoes']
            self._fuss = Blendimportfuss(self.lage, self.lage.ins_netz(d['punkte']), teile, np.concatenate(schuhe) if schuhe else None)
        return self._fuss

    def pruefung(self):
        """Die Abnahme der Stücke (`Blendimportpruefung`), einmal je Lauf — Haltung und Figur werden nur einmal gebaut."""
        if self._pruefung is None:
            self._pruefung = Blendimportpruefung(self.lage)
        return self._pruefung

    def bauen(self):
        """`({rolle_name: garderobenkennung}, bericht)` für alle Kleider, das Haar und (Einstellung) die Augen."""
        wahl = [r for r in self.rollen if r['rolle'] in ('kleid', 'haar')]
        augen = [r for r in self.rollen if r['rolle'] == 'auge']
        if self.augen_objekt and augen:
            wahl.append({'name': augen[0]['name'], 'namen': [a['name'] for a in augen], 'rolle': 'auge'})
        koerper = next((r for r in self.rollen if r['rolle'] == 'koerper'), None)
        if self.scham_objekt and koerper:
            # Schlüssel `scham`, nicht der Name des Körpers: der Körper selbst ist kein Stück.
            wahl.append({'name': koerper['name'], 'rolle': 'scham', 'schluessel': 'scham'})
        stuecke, bericht = {}, {}
        for i, rolle in enumerate(wahl):
            schluessel = rolle.get('schluessel') or rolle['name']
            self.melden(i / max(len(wahl), 1), 'Stück %s' % schluessel)
            try:
                kennung, b = self.stueck(rolle)
            except Exception as fehler:  # noqa: BLE001 — ein Stück darf scheitern, die Figur bleibt
                logger.exception('Blender-Import %s: Stück %s gescheitert', self.ablage.kennung, schluessel)
                bericht[schluessel] = {'fehler': str(fehler)[:300]}
                continue
            if kennung is None:                       # das Stück entfällt mit Grund (Scham: die Figur trifft das Original)
                bericht[schluessel] = b
                continue
            stuecke[schluessel] = kennung
            bericht[schluessel] = b
        if self._pruefung is not None:
            try:
                ziel = self.ablage.ergebnis('stuecke_bogen.png')
                ziel.parent.mkdir(parents=True, exist_ok=True)
                self.bogen_pfad = self._pruefung.bogen.schreiben(ziel)
            except Exception:  # noqa: BLE001 — das Bild ist Beigabe, kein Teil des Ergebnisses
                logger.exception('Blender-Import %s: Kontaktbogen nicht geschrieben', self.ablage.kennung)
        return stuecke, bericht

    def anzeige(self, rolle):
        scham = self.GENITAL_ZUSATZ if self.anatomie == 'penis' else self.SCHAM_ZUSATZ
        zusatz = ({'haar': self.HAAR_ZUSATZ, 'auge': self.AUGEN_ZUSATZ, 'scham': scham}.get(rolle['rolle'])
                  or rolle.get('art') or rolle['name'])
        return '%s %s' % (self.figurname, zusatz)

    @staticmethod
    def loch_angabe(loch):
        """Das Loch des Scham-Stücks für die `.ersetzt.json` (`G9stueckersatz.loch`): Dreiecke der Haut und die Verschiebung der
        Ringpunkte (m, auf Mikrometer gerundet) — oder None, wenn das Stück ohne Naht gebaut wurde."""
        if not loch:
            return None
        def meter(feld):
            return [[round(float(x), 6) for x in z] for z in feld]

        v = loch['verschiebung']
        # `ring`: die Ecken des Rings — Lage im Bau, Nummer des Hautpunkts, Verschiebung der Glättung: der Browser rückt den Rand des
        # Stücks auf die Haut, wie sie jetzt ist (`stuecknaht.js`).
        return {'dreiecke': loch['dreiecke'].tolist(), 'von': loch['von'],
                'verschiebung': {'punkte': v['punkte'].tolist(), 'd': meter(v['d'])},
                'ring': {'lage': meter(loch['ring']), 'punkte': [int(p) for p in loch['ring_punkte']], 'd': meter(loch['ring_d'])}}

    def scham_stueck(self, rolle):
        """Das Stück „<Name> Scham": Fläche und Haut des Originalkörpers dort, wo die Figur ihn nicht trägt
        (`Blendimportscham`). `(None, {'aus': Grund})`, wenn die Figur das Original schon trifft."""
        import trimesh
        from Genesis9.eigenstueck import G9eigenstueck
        from Genesis9.objleser import G9objleser
        from Genesis9.stueckersatz import G9stueckersatz

        from .blendimportscham import Blendimportscham

        kennung, anzeige = G9eigenstueck.kennung_und_name(self.anzeige(rolle))
        ordner = G9eigenstueck.arbeitsordner(kennung)
        ordner.mkdir(parents=True, exist_ok=True)
        figur = self.lage.genesis()
        flaeche = trimesh.Trimesh(figur['punkte'], figur['dreiecke'], process=False)
        materialien = self.inventar[rolle['name']]['materialien'] or [{}]      # alle: das Stück nimmt das seiner Dreiecke
        d = Blendimportscham(self.lage, self._netz(rolle), materialien).bauen(ordner, kennung, flaeche)
        if 'aus' in d:
            return None, d
        np.save(self.ablage.arbeit('scham_punkte.npy'), d['punkte'])        # der Schritt „haut" füllt die Kachel darum mit Originalfarbe
        material = self.material(kennung, d['quelle'], ordner)
        netz = G9objleser.lesen(str(self.obj(ordner, d['punkte'], d['dreiecke'], d['uv_ecken'], material)))
        roh = np.asarray(netz['punkte'], dtype=np.float64)
        kategorie = self.AUGEN_KATEGORIE
        # `wicklung=False`: die Fläche liegt teils HINTER der Haut — die Abstimmung gegen die Haut drehte sie um.
        # Gewichte: die der Hautpunkte der FIGUR dieses Imports, die das Stück verdecken (`Blendimportschamgewichte`) — die der drei
        # im Raum nächsten Punkte der Grundfigur hielten es zu 98 % am Becken, bei 25° gespreizten Beinen bewegte es sich 0 mm gegen 6,6 mm
        # der Haut (gemessen 09.10.2026). Die LAGE folgt dem Körper nicht (`G9stueckteile.netze`, Hauttiefe), darum keine Rückrechnung
        # auf die Grundfigur (`G9gcfigurbau`): die gespeicherte Lage IST die Ruhelage der Figur dieses Imports.
        haut = Blendimportschamgewichte.fuer_figur(figur)
        loch = d.get('loch')
        # Verschweißt (`Blendimportschamnaht`): der Rand trägt die Gewichte der Haut auf dem Ring des Lochs, sonst folgte er einer Haltung anders.
        gewichte = haut.gewichte(roh, np.asarray(netz['flaechen'], dtype=np.int64),
                                 ring=(loch['ring'], loch['ring_punkte']) if loch else None)
        d['bericht']['gewichte'] = haut.bericht
        bilanz = G9eigenstueck.schreiben(roh, netz, kennung, anzeige, kategorie, material, heben=False, wicklung=False,
                                         gewichte=gewichte)
        G9stueckersatz.schreiben(bilanz['duf'], [], haut_tiefe_mm=Blendimportscham.HAUT_TIEFE_MM, anatomie=self.anatomie,
                                 eigene_gewichte=True, loch=self.loch_angabe(loch))
        bericht = dict(d['bericht'], stueck=bilanz['stueck'], name=anzeige, flaechen=bilanz['flaechen'], kategorie=list(kategorie),
                       punkte=bilanz['punkte'], knochen=bilanz['knochen'])
        logger.info('Blender-Import %s: Scham-Stück → %s (%s)', self.ablage.kennung, bilanz['stueck'], d['bericht'])
        return bilanz['stueck'], bericht

    def stueck(self, rolle):
        from Genesis9.eigenstueck import G9eigenstueck
        from Genesis9.gcfigurbau import G9gcfigurbau
        from Genesis9.mbkategorien import G9mbkategorien
        from Genesis9.objleser import G9objleser
        from Genesis9.stueckersatz import G9stueckersatz

        if rolle['rolle'] == 'scham':
            return self.scham_stueck(rolle)
        haar = rolle['rolle'] == 'haar'
        auge = rolle['rolle'] == 'auge'
        d = self._netz(rolle)
        # Haar und Augen hängen im Original starr am Kopf: sie gehen mit dem Kopf in die Ruhelage.
        schuh = rolle.get('ordner') == 'shoes'
        fuss = self.fuss() if schuh else None
        absatz = fuss is not None and bool(fuss.aktiv())
        requisit = None if (haar or auge or schuh) else Blendimportrequisit(self.lage).erkennen(d['punkte'])
        if haar or auge:
            punkte = self.lage.kopf_starr(d['punkte'])
        elif requisit:
            # Zu weit vom Körper für die Käfig-Nachbarschaft (Waffe in der Hand, Helm): starr mit dem Teil, das es berührt.
            punkte, requisit['rundlauf_mm'] = Blendimportrequisit(self.lage).ruhelage(d['punkte'], requisit['nummer'])
        else:
            # Jedes Kleid sieht nur die Körperteile, die es tragen darf (Hände nie): sonst hing der Saum an der Hand auf der Hüfte. Ein Schuh
            # geht in den Käfig mit den Füßen in Absatzhaltung (`Blendimportfuss`); die Figur stellt beim Tragen ihre Füße dazu.
            erlaubt = Blendimportteile.erlaubt(rolle.get('ordner'), '%s %s' % (rolle['name'], rolle.get('art', '')))
            punkte = (fuss.stueck_ruhelage(d['punkte'], d['dreiecke'], erlaubt) if absatz
                      else self.lage.stueck_ruhelage(d['punkte'], d['dreiecke'], erlaubt))
        kennung, anzeige = G9eigenstueck.kennung_und_name(self.anzeige(rolle))
        ordner = G9eigenstueck.arbeitsordner(kennung)
        ordner.mkdir(parents=True, exist_ok=True)
        material = self.material(kennung, (self.inventar[rolle['name']]['materialien'] or [{}])[0] or {}, ordner, haar)
        if auge:
            material['shininess'] = self.AUGEN_GLANZ
        obj = self.obj(ordner, punkte, d['dreiecke'], d['uv_ecken'], material)
        netz = G9objleser.lesen(str(obj))
        roh = np.asarray(netz['punkte'], dtype=np.float64)
        if haar:
            kategorie, art, knochen = self.HAAR_KATEGORIE, 'Hair', 'head'
        elif auge:
            kategorie, art, knochen = self.AUGEN_KATEGORIE, 'Clothing', 'head'
        else:
            kategorie, art, knochen = (G9mbkategorien.fuer(rolle.get('ordner') or 'tops', anzeige), 'Clothing',
                                       requisit['knochen'] if requisit else None)
        bilanz = G9eigenstueck.schreiben(roh, netz, kennung, anzeige, kategorie, material, heben=False,
                                         knochen=knochen, art_ordner=art)
        figur = self.lage.stellung()
        ruhe, bericht = G9gcfigurbau.ruhelage(bilanz['stueck'], figur, roh, roh)
        schreiben = lambda lage_ruhe: G9eigenstueck.schreiben(lage_ruhe, netz, kennung, anzeige, kategorie, material,  # noqa: E731
                                                              heben=False, knochen=knochen, art_ordner=art)
        bilanz = schreiben(ruhe)
        angezogen = G9gcfigurbau.pruefen(bilanz['stueck'], figur, roh)
        if angezogen['p99_mm'] > self.NACHRECHNEN_MM and not (haar or auge):
            # Das geschriebene Stück folgt dem Ziel schlechter, als die Rückrechnung meldete (Hemd: Rest 3,0 mm, `pruefen` p99 13,2 / max 20,1 mm; Ursache
            # vermutet: andere Bindung der Datei an die Körperteile). Ein zweiter Durchgang gegen die gelesene Datei hilft (Hemd: p99 1,0 / max 14,9 mm, +24 s).
            ruhe2, bericht2 = G9gcfigurbau.ruhelage(bilanz['stueck'], figur, roh, ruhe)
            bilanz2 = schreiben(ruhe2)
            angezogen2 = G9gcfigurbau.pruefen(bilanz2['stueck'], figur, roh)
            if (angezogen2['p99_mm'], angezogen2['max_mm']) < (angezogen['p99_mm'], angezogen['max_mm']):
                bilanz, bericht, angezogen = bilanz2, dict(bericht2, zweiter_durchgang=True), angezogen2
            else:
                bilanz = schreiben(ruhe)
                bericht['zweiter_durchgang'] = 'verworfen'
        bericht.update(stueck=bilanz['stueck'], name=anzeige, punkte=bilanz['punkte'], flaechen=bilanz['flaechen'],
                       haut_median_mm=bilanz['haut_median_mm'], kategorie=list(kategorie), angezogen=angezogen)
        if haar:
            bericht['kopf'] = getattr(self.lage, 'kopf_befund', None)
        if fuss is not None:
            # Die Datei NACH der `.duf` (Stückstand im Antwortvorrat), bei jedem Schuh — auch leer, sonst bliebe der Griff eines früheren Laufs stehen.
            G9stueckersatz.schreiben(bilanz['duf'], [], griff=fuss.griff() if absatz else None)
            bericht['fuss'] = fuss.bericht() if absatz else None
        if requisit:
            bericht['requisit'] = requisit
        elif not (haar or auge):
            # Abnahme (Stufe 7): Kantenverzerrung, frei hängender Anteil, Haltungstreue gegen das Original — samt Hinweisen.
            bericht['pruefung'] = self.pruefung().pruefen(bilanz['stueck'], punkte, self.lage.ins_netz(d['punkte']), d['dreiecke'],
                                                          fuss if absatz else None, rolle['name'])
        if auge:
            # Die Datei NACH der `.duf` (Stückstand im Antwortvorrat): der Browser blendet die Genesis-Augen aus, solange es sitzt.
            G9stueckersatz.schreiben(bilanz['duf'], ['augen'])
            bericht['ersetzt'] = ['augen']
        logger.info('Blender-Import %s: Stück %s → %s', self.ablage.kennung, rolle['name'], bilanz['stueck'])
        return bilanz['stueck'], bericht

    #: Schnitt der Deckkraftkarte beim Haar (Anteil 0…1): Haarkarten der .blend tragen einzelne Strähnen von 1–3 Texeln Breite.
    #: Mit Alpha-to-Coverage und Schnitt 0,02 verwischt der Browser sie zu flachen Bahnen; Blender rechnet „Hashed" mit
    #: vielen Abtastungen. Setzung am Vergleich mit Blender (cute girl, 08.10.2026): 0,18 zeigt einzelne Strähnen und
    #: bleibt dicht, 0,35 lichtet die Frisur aus — kein Messwert.
    HAAR_ALPHA_SCHWELLE = 0.18

    @classmethod
    def material(cls, kennung, quelle, ordner, haar=False):
        """Material für `G9dsonschreiber`: Farbe, Normalen, Rauheit, Alpha aus der .blend (Bilder werden kopiert).
        Die zweite, gekachelte Normalenkarte (`detailnormalen`, Gewebe der Kleider) kommt als PNG aus dem Export und trägt
        ihre Wiederholungen (`detail_kachel`). Ein DDS an der Grundnormale kann der Browser nicht lesen — es fällt weg."""
        def bild(kanal):
            pfad = quelle.get(kanal)
            if not pfad or str(pfad).lower().endswith('.dds'):
                return None
            return cls.browserbild(pfad, ordner / ('%s_%s.png' % (kennung, kanal)))

        alpha = bild('alpha')
        if alpha:
            alpha = cls.alphabild(alpha, ordner / (kennung + '_alpha.png'), quelle.get('alpha_ausgang') or 'Alpha')
        # Feste Farbe statt Bild (`Blendexport.festfarbe`: Haar mit Mix-Faktor 1,0): linear → sRGB, wie Daz' Diffusfarbe.
        fest = quelle.get('farbe_wert')
        farbe = tuple(round(cls.srgb(w), 4) for w in fest) if fest and not quelle.get('farbe') else (1.0, 1.0, 1.0)
        return {'name': kennung + '_Mat', 'farbe': farbe, 'bild': bild('farbe'),
                'normalen': bild('normalen'), 'rauheit_bild': bild('rauheit'), 'alpha_bild': alpha,
                'detailnormalen': bild('detailnormalen'), 'detail_kachel': quelle.get('detail_kachel'),
                'alpha_schwelle': cls.HAAR_ALPHA_SCHWELLE if haar and alpha else None,
                'shininess': None, 'opacity': None}

    #: Bildhelfer in `Blendimportbilder` (die Datei stand bei 297 Zeilen); hier als Namen des Stücks, damit Aufrufer und Tests
    #: (`mock.patch.object(Blendimportstuecke, 'alphabild', …)`) dieselben bleiben.
    browserbild = staticmethod(Blendimportbilder.browserbild)
    srgb = staticmethod(Blendimportbilder.srgb)
    alphabild = staticmethod(Blendimportbilder.alphabild)
    obj = staticmethod(Blendimportbilder.obj)
