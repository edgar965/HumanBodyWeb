# -*- coding: utf-8 -*-
"""Standvorabkleider — die Kleider und das Haar des Standmodells, solange es noch keine Iteration gibt: die Stücke des Schritts „Kleiderstücke" und die gewählte Frisur (04./05.10.2026).

Das Standmodell (`Engine2d3dKleiderstandmodell`, die GLB der Bühne) nahm Kleider und Haar bisher nur aus dem Modell der letzten Runde (`kreislauf.modell`) — vor Runde 1 trug es keine, und der
Schalter „Kleider" der Bühne hatte nichts zu schalten (Edgar, 04.10.2026: „die Kleider sind im 3D View noch nicht wegklickbar"). Nach dem Schritt „Kleiderstücke" (`Fotostuecke`, gemerkt in
`job.ergebnis['fotostuecke']`) gibt es die Stücke; diese Klasse macht daraus das Modell, das Runde 1 ohnehin anzöge: `Kleiderwahl.soll` nimmt die Stücke in der Reihenfolge `FOTO_REIHE`.

Das Oberteil (04.10.2026, Edgar zum dritten Mal: „T-shirt verfranst am Anfang und am Ende, zu weit abstehend vom Körper, kein Saum. Nimmst du ein Genesis T-Shirt oder GC? die sind doch viel besser"):
Die Option `koerper.oberteil` wählt, ob das Fotostück oder das Genesis-Hemd der Bibliothek (`Kleiderwahl.OBERTEIL`, mit Saum, Ausschnitt und Ärmelabschlüssen) getragen wird — Vorgabe Bibliothek;
das Hemd bekommt die mittlere Farbe des Fotostücks (die Farbe des Hemds im Foto, `hemdfarbe`). Hose und Socken bleiben Fotostücke.

Das Haar (05.10.2026, Edgar: „Haar textur noch auf dem Kopf", „die Haare sind bei Sapiens noch keine Objekte"): Der Schritt „Frisur" der Körper-Kette hat die beste Frisur der Garderobe gewählt
(`ergebnis.frisur.wahl`: Kennung, Regler, Farbe) — mit Option `figur.kopfhaut = haut` trägt die Kopfhaut keine Haarfarbe mehr, und das Haar kommt als Objekt: Runde 1 beginnt mit genau dieser Frisur
(`Begutachtungsrunde._start`), die Bühne zeigt sie jetzt schon davor („Haare" schaltet sie). Gefärbt wird wie in Runde 1: erst umfärben (Grau), dann tönen — mit der Haarfarbe der Fotos
(`haarfarbe`, Sapiens-Klasse Haar), sonst der der Netzflächen (04.10.2026: Edgar „Haar textur und Größe total daneben, Haar ist grau bis weiss" — ohne Umfärben sah man nur die orange Strähnengruppe).
Die Regler der Wahl (Mavick: `ExpandAll −0,25`) gelten jetzt auch hier; die Strähnengruppen werden an die Helligkeit angeglichen (`GLEICH`, „Haar seitlich braun": das Unterhaar der Mavick-Frisur
stand schwarz), und die Frisur wird an die Hülle des Fotohaars geklemmt (`Haarklemme`, beim Bau der Teile).

Zwei Fallen, beide gemessen am Auftrag 2026.10.04.11.11.44:
  * `ModellMitKleidern().kleid_nur(*stuecke)` lässt das Standardhemd `g9_base_shirt` stehen (sein Regler fehlt, die Bibliothek zählt es dann als 1) — es wird ausdrücklich abgelegt (außer es IST das Hemd);
  * ein frisches Modell trägt auch das Standardhaar (`kin_hair`, 421.846 Flächen) — `haar_nur` ersetzt es durch die gewählte Frisur; ohne gewählte Frisur wird es mit `haar_keins` abgelegt.

Gilt nur ohne `kreislauf.modell`: mit Iterationen bestimmt deren Modell die Kleider und das Haar wie bisher. Das Standmodell nimmt aus dem Vorab-Modell die Arten `ARTEN` (`Kleidung`, `Haar`).
"""

import json

__all__ = ['Standvorabkleider']


class Standvorabkleider:
    #: Die Arten der Teile, die das Standmodell vor den Iterationen aus dem Vorab-Modell nimmt (`Kleidermodellbau.teile`: `art`).
    ARTEN = ('kleidung', 'haar')
    #: Wie weit die Helligkeit der Strähnengruppen angeglichen wird (`haar_gruppen_angleichen`, 0 = Staffelung der Daz-Frisur, 1 = gleich). Anhaltswert: das Foto zeigt das Haar oben etwa
    #: doppelt so hell wie an den Seiten (am Bild gesehen, nicht gemessen); bei 0,6 liegt das Unterhaar der Mavick-Frisur bei rund 0,43 statt 0,19 (Grau 0,75 oben).
    GLEICH = 0.6

    @staticmethod
    def _fotostuecke(job):
        return ((job.ergebnis or {}).get('fotostuecke') or {}).get('stuecke') or {}

    @classmethod
    def stuecke(cls, job):
        """Garderobenkennungen der Stücke in der Reihenfolge von `Kleiderwahl.FOTO_REIHE` (das Oberteil nach der Option `koerper.oberteil`) — leer ohne Stücke."""
        from iterationen2d3d.kleiderwahl import Kleiderwahl

        from .engine2d3dkleiderkoerperoptionen import Engine2d3dKleiderkoerperoptionen
        gebaut = Kleiderwahl.mit_oberteil(cls._fotostuecke(job), Engine2d3dKleiderkoerperoptionen.oberteil(job))
        return [gebaut[name] for name in Kleiderwahl.FOTO_REIHE if gebaut.get(name)]

    #: Gemerkt je Auftrag und Stand der Fotostücke: die Erkennung liest die Fotos, `fingerabdruck` wird bei jeder Zustandsabfrage der Bühne gebildet.
    _UHREN = {}

    @classmethod
    def uhren(cls, job):
        """Garderobenkennungen der Uhren, die die Fotos zeigen (`Uhrerkennung` über `Begutachtungswerkzeug.zubehoer`, das Stück `eigen_uhr_<l|r>` wird bei Bedarf gebaut) — leer ohne Uhr oder bei Fehler.
        Edgar 05.10.2026 („hast du kein Daz-Objekt für Uhr?"): das Startrezept von Sapiens 2 trug keine Uhr, obwohl das Stück in der Garderobe liegt und Randy (2026.10.03.13.00.02) es trägt — nur die
        automatische Runde hängte das Zubehör an (`Kleiderwahl.soll`), das Vorab-Modell nicht."""
        import logging

        from iterationen2d3d.kleiderwahl import Kleiderwahl
        schluessel = (getattr(job, 'kennung', None), json.dumps(((job.ergebnis or {}).get('fotostuecke') or {}).get('stand'), sort_keys=True, default=str))  # `stand` ist eine Liste: nicht hashbar
        if schluessel not in cls._UHREN:
            try:
                from ..daten.engine2d3dkleiderablage import Engine2d3dKleiderablage
                from .begutachtungswerkzeug import Begutachtungswerkzeug
                from .iterationsreferenz import Iterationsreferenz
                referenzen, _ausgelassen = Iterationsreferenz.laden(job)
                zubehoer = Begutachtungswerkzeug(job, Engine2d3dKleiderablage(job.kennung)).zubehoer(referenzen)
            except Exception as fehler:  # noqa: BLE001 — Zubehör ist Beiwerk: ohne Uhr weiter (nicht gemerkt, nächster Aufruf probiert es wieder)
                logging.getLogger('core').warning('Standvorab %s: Uhr nicht erkannt (%s)', getattr(job, 'kennung', '?'), fehler)
                return []
            cls._UHREN[schluessel] = [Kleiderwahl.UHR % seite for seite in zubehoer.get('uhr') or []]
        return cls._UHREN[schluessel]

    @classmethod
    def hemdfarbe(cls, job):
        """Die Farbe des Hemds im Foto (RGB 0–1): Mittel der Textur des Fotostücks `oberteil` — None ohne dieses Stück oder ohne Bild."""
        import numpy as np
        from Genesis9.garderobe import G9garderobe
        from Genesis9.material import G9material
        from PIL import Image

        kennung = cls._fotostuecke(job).get('oberteil')
        if not kennung:
            return None
        try:
            for b in (G9garderobe.bilder(kennung) or {}).values():
                pfad = G9material.datei(b['albedo']) if b.get('albedo') else None
                if pfad is None:
                    continue
                with Image.open(pfad) as bild:
                    a = np.asarray(bild.convert('RGBA'), dtype=np.float64)
                sicht = a[..., 3] > 10
                if sicht.any():
                    return [round(float(c) / 255.0, 4) for c in a[sicht][:, :3].mean(axis=0)]
        except (OSError, ValueError, KeyError) as fehler:
            import logging
            logging.getLogger('core').warning('Standvorab %s: Hemdfarbe nicht gelesen (%s)', getattr(job, 'kennung', '?'), fehler)
        return None

    @staticmethod
    def frisur(job):
        """`(kennung, farbe)` der Frisur, die der Schritt „Frisur" gewählt hat — sonst die erste Kandidatin; None, wenn keine gemessen ist."""
        fr = (job.ergebnis or {}).get('frisur') or {}
        wahl = fr.get('wahl') or {}
        erste = (fr.get('kandidaten') or [{}])[0]
        kennung = wahl.get('kennung') or erste.get('kennung')
        return (kennung, wahl.get('farbe')) if kennung else None

    @staticmethod
    def frisurregler(job):
        """Die Formregler der gewählten Frisur (`ergebnis.frisur.wahl.regler`, Mavick: `ExpandAll −0,25`) — leer, wenn die Wahl keine hat."""
        wahl = ((job.ergebnis or {}).get('frisur') or {}).get('wahl') or {}
        return {str(k): float(v) for k, v in (wahl.get('regler') or {}).items()}

    @staticmethod
    def haarfarbe(job):
        """Die Haarfarbe der FOTOS (RGB 0–1) aus dem Schritt „Segmentierung" (`kennzahlen.haarfarbe`, Median der Pixel der Sapiens-Klasse Haar) — None ohne diesen Schritt oder ohne Haar im Foto."""
        from ..daten.engine2d3dkleiderablage import Engine2d3dKleiderablage
        try:
            daten = json.loads(Engine2d3dKleiderablage(job.kennung).segmentierung('segmentierung.json').read_text(encoding='utf-8'))
        except (OSError, ValueError):
            return None
        rgb = ((daten.get('kennzahlen') or {}).get('haarfarbe') or {}).get('rgb')
        return [float(c) / 255.0 for c in rgb[:3]] if rgb else None

    @classmethod
    def kappenfarbe(cls, job):
        """Die Farbe der Haarkappe (`Haarkappe`, RGB 0–1): die Haarfarbe der Fotos, sonst die der Haarflächen des Netzes (`frisur.wahl.farbe`); unbunt wird grau wie in den Runden — None ohne beide."""
        from iterationen2d3d.farbangleich import Farbangleich
        from iterationen2d3d.iterationhaare import IterationHaare
        wahl = ((job.ergebnis or {}).get('frisur') or {}).get('wahl') or {}
        rgb = cls.haarfarbe(job) or (Farbangleich.rgb_aus(wahl['farbe']) if wahl.get('farbe') else None)
        return IterationHaare._neutral(rgb) if rgb else None  # noqa: SLF001 — dieselbe Regel „unbunt wird grau" wie Runde 1

    @classmethod
    def _haar_faerben(cls, modell, kennung, frisur_farbe, foto, hell=1.0):
        """Wie Runde 1 (`IterationHaare.farbe`): erst die Daz-Grundtöne der Strähnengruppen durch Grau ersetzen (`haar_umfaerben`), dann tönen — `haar_farbe` allein tönt Grundton × Farbe, die Gruppen
        blieben braun, orange und fast schwarz (Auftrag 2026.10.04.11.11.44: von der Frisur sah man nur die orange Gruppe, der Rest verschwand im dunklen Hintergrund). Farbe: die der Fotos, sonst die
        Haarflächen des Netzes (`frisur_farbe`, #rrggbb). Danach die Gruppen angleichen (`GLEICH`). `hell`: wie hell die Karten im Render erscheinen (`Haarumbau.KARTEN_HELL`) — die Tönung wird durch
        diesen Anteil geteilt, damit der Render die Fotofarbe trifft; 1,0 für die Bühne (GLB, ohne Eigenschatten der Karten)."""
        from iterationen2d3d.farbangleich import Farbangleich
        from iterationen2d3d.iterationhaare import IterationHaare
        rgb = foto or (Farbangleich.rgb_aus(frisur_farbe) if frisur_farbe else None)
        if rgb:
            modell.haar_umfaerben(kennung)
            modell.haar_gruppen_angleichen(kennung, cls.GLEICH)
            neutral = IterationHaare._neutral(rgb)  # noqa: SLF001 — dieselbe Regel „unbunt wird grau" wie Runde 1
            modell.haar_farbe(Farbangleich.start_grau([c / hell for c in neutral]))

    @classmethod
    def _hemd_faerben(cls, modell, kennung, rgb):
        """Das Genesis-Hemd in der Farbe des Fotos (wie Runde 1, `IterationKleider.farbe`): die Daz-Farbe durch Grau ersetzen, dann auf die Fotofarbe tönen."""
        from iterationen2d3d.farbangleich import Farbangleich
        if rgb:
            modell.kleid_umfaerben(kennung)
            modell.kleid_farbe_je_stueck(kennung, Farbangleich.start_grau(rgb))

    @classmethod
    def modell(cls, job, ohne_haar=False, modell=None, hell=1.0):
        """`ModellMitKleidern.als_dict()` mit genau diesen Stücken und der gewählten Frisur — None ohne Stücke. `ohne_haar`: kein Haar im Modell (das Standmodell trägt dann die Haarkappe, `Haarkappe`).
        `modell`: ein anderes Modell, an dem die Aufrufe laufen (`Rezeptaufzeichnung` — dieselben Aufrufe als Text, `rezept`). `hell`: siehe `_haar_faerben`."""
        liste = cls.stuecke(job)
        if not liste:
            return None
        from Genesis9.modellmitkleidern import ModellMitKleidern
        from iterationen2d3d.kleiderwahl import Kleiderwahl
        modell = (modell if modell is not None else ModellMitKleidern()).kleid_nur(*liste, *cls.uhren(job))
        if Kleiderwahl.OBERTEIL in liste:
            cls._hemd_faerben(modell, Kleiderwahl.OBERTEIL, cls.hemdfarbe(job))
        else:
            modell.kleid_aus(Kleiderwahl.OBERTEIL)
        frisur = None if ohne_haar else cls.frisur(job)
        if frisur:
            modell.haar_nur(frisur[0])
            for kanal, wert in cls.frisurregler(job).items():
                modell.haar_morph(frisur[0], kanal, wert)
            cls._haar_faerben(modell, frisur[0], frisur[1], cls.haarfarbe(job), hell)
        else:
            modell.haar_keins()                         # ohne Wahl kein Standardhaar (`kin_hair`)
        return modell.als_dict()

    @staticmethod
    def haltungszeilen(job):
        """Die Haltung der Fotos als Rezeptzeilen (`m.haltung(…)`, `m.haltung_gelenk(…)` für Ellbogen und Beine) — dieselben Regeln wie die automatische Runde (`IterationModell.haltung`) aus den Posenlandmarken
        der Fotos (`Haltungsfotos`, `kreislauf.haltung_foto`; ohne Runde wird sie hier geschätzt und nicht abgelegt). Leer ohne Fotolandmarken: dann bleibt die A-Pose.
        Gemessen an Sapiens 2 (Runde 1, 05.10.2026): ohne diese Zeilen stand die Figur mit gespreizten Armen vor Fotos mit hängenden Armen, und die Fotohaut der Arme deckte 0,4 % der Kachel (die Projektion
        trifft dort Hintergrund)."""
        import logging

        from Genesis9.modellmitkleidern import ModellMitKleidern
        from iterationen2d3d.iterationmodell import IterationModell
        foto = ((job.ergebnis or {}).get('kreislauf') or {}).get('haltung_foto')
        if not foto:
            try:
                from ..daten.engine2d3dkleiderablage import Engine2d3dKleiderablage
                from .haltungsfotos import Haltungsfotos
                from .iterationsreferenz import Iterationsreferenz
                referenzen, _ausgelassen = Iterationsreferenz.laden(job)
                foto = Haltungsfotos(job, Engine2d3dKleiderablage(job.kennung)).fuer_lauf({}, referenzen)
            except Exception as fehler:  # noqa: BLE001 — ohne Haltung der Fotos bleibt die A-Pose (Hinweis im Log)
                logging.getLogger('core').warning('Startrezept %s: Haltung der Fotos nicht geschätzt (%s)', getattr(job, 'kennung', '?'), fehler)
                return []
        return IterationModell(ModellMitKleidern(), {'haltung_foto': foto}).haltung() if foto else []

    @classmethod
    def rezept(cls, job):
        """Die Haltung der Fotos (`haltungszeilen`) und dieselben Aufrufe wie `modell`, als Zeilen eines Rezepts (`m.kleid_nur(…)`, `m.haar_nur(…)`, Farben) — die Figur, die der Stand vor den Iterationen
        zeigt (Haarkappe ausgenommen: im Rezept ist es die gewählte Frisur, getönt für den Render, `Haarumbau.KARTEN_HELL`). Leer ohne Fotostücke. Die Ausgangslage der Nachbesserung (`Edgar.Rezeptkatalog`)."""
        from Genesis9.modellmitkleidern import ModellMitKleidern

        from .haarumbau import Haarumbau
        from .rezeptaufzeichnung import Rezeptaufzeichnung
        aufzeichnung = Rezeptaufzeichnung(ModellMitKleidern())
        if cls.modell(job, modell=aufzeichnung, hell=Haarumbau.KARTEN_HELL) is None:
            return []
        return cls.haltungszeilen(job) + aufzeichnung.zeilen

    @classmethod
    def fingerabdruck(cls, job):
        """Gehört in die Fassung des Standmodells: die Stücke, die Frisur und der Stand ihres Baus (Netz, Maske, Figur) — None ohne Stücke. Ein neu gebautes Stück unter demselben Namen
        ändert den Stand, die Bühne lädt dann die neue Datei (`artefakte-benennen`)."""
        liste = cls.stuecke(job)
        if not liste:
            return None
        # Die Hemdfarbe ist das Mittel der Textur des Fotostücks: ändert sie sich, ändert sich `stand` — sie selbst wird nicht gerechnet (die Fassung wird bei jeder Zustandsabfrage gebildet).
        from ..daten.engine2d3dkleiderablage import Engine2d3dKleiderablage
        from .haarkappe import Haarkappe
        from .herrenhaar import Herrenhaar
        from .iterationsoptionen import Iterationsoptionen
        ablage = Engine2d3dKleiderablage(job.kennung)
        return [liste, cls.uhren(job), cls._fotostuecke(job).get('oberteil'), ((job.ergebnis or {}).get('fotostuecke') or {}).get('stand'), cls.frisur(job), cls.frisurregler(job), cls.haarfarbe(job),
                cls.GLEICH, Haarkappe.fingerabdruck(ablage), Iterationsoptionen.haarumbau(job), Herrenhaar.fingerabdruck(ablage)]
