# -*- coding: utf-8 -*-
"""Bildmodellbildtypen — die drei Wahlfelder je Bild und was die Rechnung daraus macht.

Edgar (19.09.2026): „ein paar Combo-Boxen, mit denen ich den Typ des Bildes
auswählen kann … Erste Combo Box: Hauptbild-Typ, zweite Nebenbild-Typ,
dritte nur Textur?"

    Hauptbild   Körper von vorn / Seite / hinten / dreiviertel, Kopf von
                vorn / Seite, Drehvideo → `kategorie` + `ansicht`. Körper-
                Hauptbilder gehen an SMPLest-X, Kopfbilder an PyMAF-X/FLAME,
                die Ansicht entscheidet die Geschlechtsschätzung (vorn/hinten).
    Nebenbild   ein Körperteil → `kategorie: neben` + `teil`. Hände liefern
                die Fingerlänge (`Bildmodellhaende`); jedes andere Teil geht
                mit Textur „Fotofarbe" durch den Schätzer und färbt NUR die
                SMPL-X-Punkte seines Teils (`Bildmodellfototextur`, `punkte`).
                Gruppenbild und „ohne Befund" bleiben außen vor.
    Nutzung     Form und Textur / nur Form / nur Textur / nicht verwenden →
                `nutzung`. „Nur Textur" nimmt das Bild aus Mischung, Maßen
                und Silhouette, aber der Schätzer läuft (die Fotofarbe braucht
                sein posiertes Netz); „nur Form" nimmt es aus Hautton und
                Fotofarbe.

`stellen(eintrag, rumpf)` schreibt die Wahl an den Eintrag, `fuer_form` und
`fuer_textur` fragen sie ab — an einer Stelle, damit Schätzung, Maße,
Silhouette und Textur dieselbe Antwort bekommen.
"""

__all__ = ['Bildmodellbildtypen']


class Bildmodellbildtypen:
    HAUPTKATEGORIEN = ('koerper', 'kopf', 'video')
    NEBENKATEGORIEN = ('neben', 'gruppe', 'leer')

    #: (wert, anzeige, kategorie, ansicht)
    HAUPT = (
        ('', '— kein Hauptbild —', None, None),
        ('koerper/vorne', 'Körper vorn', 'koerper', 'vorne'),
        ('koerper/seite', 'Körper Seite', 'koerper', 'seite'),
        ('koerper/hinten', 'Körper von hinten', 'koerper', 'hinten'),
        ('koerper/dreiviertel', 'Körper dreiviertel', 'koerper', 'dreiviertel'),
        ('kopf/vorne', 'Kopf vorn', 'kopf', 'vorne'),
        ('kopf/seite', 'Kopf Seite', 'kopf', 'seite'),
        ('video/drehung', 'Drehvideo', 'video', 'drehung'),
    )
    #: (wert, anzeige, kategorie, teil, Körperteile nach `G9koerperteile.TEILE`)
    NEBEN = (
        ('', '— kein Nebenbild —', None, None, ()),
        ('neben', 'Nebenbild', 'neben', None, ()),
        ('neben/haende', 'Hände', 'neben', 'haende', ('l_hand', 'r_hand')),
        ('neben/gesicht', 'Gesicht (Detail)', 'neben', 'gesicht', ('kopf',)),
        ('neben/oberkoerper', 'Oberkörper', 'neben', 'oberkoerper',
         ('hals', 'rumpf', 'l_schulter', 'r_schulter')),
        ('neben/ruecken', 'Rücken', 'neben', 'ruecken',
         ('rumpf', 'becken', 'l_schulter', 'r_schulter')),
        ('neben/becken', 'Hüfte/Gesäß', 'neben', 'becken', ('becken',)),
        ('neben/arme', 'Arme', 'neben', 'arme',
         ('l_oberarm', 'l_unterarm', 'l_hand', 'r_oberarm', 'r_unterarm', 'r_hand')),
        ('neben/beine', 'Beine', 'neben', 'beine',
         ('l_oberschenkel', 'l_unterschenkel', 'r_oberschenkel', 'r_unterschenkel')),
        ('neben/fuesse', 'Füße', 'neben', 'fuesse', ('l_fuss', 'r_fuss')),
        ('gruppe', 'Gruppenbild', 'gruppe', None, ()),
        ('leer', 'Ohne Befund', 'leer', None, ()),
    )
    #: (wert, anzeige, erklärung)
    NUTZUNG = (
        ('form_textur', 'Form und Textur', 'Schätzer, Mischung, Maße; Hautton und Fotofarbe'),
        ('form', 'Nur Form', 'Nicht für Hautton und Fotofarbe'),
        ('textur', 'Nur Textur', 'Der Schätzer läuft (posiertes Netz), Mischung und Maße lassen es aus'),
        ('aus', 'Nicht verwenden', 'Bleibt im Auftrag, zählt nirgends'),
    )
    VORGABE_NUTZUNG = 'form_textur'
    TEILE = {wert.split('/', 1)[1]: teile for wert, _, _, teil, teile in NEBEN if teil}

    # ------------------------------------------------------------ Katalog

    @classmethod
    def katalog(cls):
        """Für die Seite: die drei Listen."""
        return {
            'haupt': [{'wert': w, 'anzeige': a} for w, a, _, _ in cls.HAUPT],
            'neben': [{'wert': w, 'anzeige': a} for w, a, _, _, _ in cls.NEBEN],
            'nutzung': [{'wert': w, 'anzeige': a, 'erklaerung': e} for w, a, e in cls.NUTZUNG],
        }

    # ------------------------------------------------------------- Lesen

    @classmethod
    def haupt(cls, b):
        """Der Wert der ersten Box für diesen Eintrag ('' = kein Hauptbild)."""
        k = b.get('kategorie')
        if k not in cls.HAUPTKATEGORIEN:
            return ''
        ansicht = b.get('ansicht')
        werte = {w for w, _, kat, _ in cls.HAUPT if kat == k}
        wert = '%s/%s' % (k, ansicht)
        if wert in werte:
            return wert
        return sorted(werte)[0] if k != 'koerper' else 'koerper/vorne'

    @classmethod
    def neben(cls, b):
        """Der Wert der zweiten Box ('' = kein Nebenbild)."""
        k = b.get('kategorie') or 'neben'
        if k not in cls.NEBENKATEGORIEN:
            return ''
        if k != 'neben':
            return k
        teil = b.get('teil')
        return 'neben/%s' % teil if teil in cls.TEILE else 'neben'

    @classmethod
    def nutzung(cls, b):
        n = b.get('nutzung')
        return n if n in {w for w, _, _ in cls.NUTZUNG} else cls.VORGABE_NUTZUNG

    @classmethod
    def fuer_form(cls, b):
        """Zählt das Bild für Schätzung, Mischung, Maße und Silhouette?"""
        return (
            b.get('kategorie') in cls.HAUPTKATEGORIEN
            and float(b.get('gewicht') or 0) > 0
            and cls.nutzung(b) in ('form_textur', 'form')
        )

    @classmethod
    def fuer_textur(cls, b):
        """Darf das Bild Haut liefern (Hautton, Fotofarbe)? Die Tauglichkeit prüft `Bildmodelltextur`."""
        return cls.nutzung(b) in ('form_textur', 'textur')

    @classmethod
    def textur_teile(cls, b):
        """Die Körperteile, die ein Nebenbild färben darf — leer für Hauptbilder (alles)."""
        if b.get('kategorie') != 'neben':
            return ()
        return cls.TEILE.get(b.get('teil') or '', ())

    @classmethod
    def fuer_haende(cls, b):
        """Zählt das Bild für die Fingerlänge? Hauptbilder, Hände und Nebenbilder ohne Teil."""
        if cls.nutzung(b) == 'aus':
            return False
        if b.get('kategorie') in cls.HAUPTKATEGORIEN:
            return True
        return b.get('kategorie') == 'neben' and b.get('teil') in (None, '', 'haende')

    # ----------------------------------------------------------- Stellen

    @classmethod
    def stellen(cls, eintrag, rumpf):
        """Die Wahl aus dem Rumpf (`haupt`, `neben`, `nutzung`, `kategorie`, `gewicht`,
        `textur_an`) an den Eintrag schreiben; True, wenn Kategorie oder Gewicht
        von Hand gestellt wurden (`manuell`)."""
        manuell = False
        if 'haupt' in rumpf:
            manuell |= cls._haupt_stellen(eintrag, rumpf.get('haupt') or '')
        if 'neben' in rumpf:
            manuell |= cls._neben_stellen(eintrag, rumpf.get('neben') or '')
        if rumpf.get('kategorie') in cls.HAUPTKATEGORIEN + cls.NEBENKATEGORIEN:
            eintrag['kategorie'] = rumpf['kategorie']
            manuell = True
        if 'gewicht' in rumpf:
            try:
                eintrag['gewicht'] = max(0.0, min(1.0, float(rumpf['gewicht'])))
                manuell = True
            except TypeError, ValueError:
                pass
        if rumpf.get('nutzung') in {w for w, _, _ in cls.NUTZUNG}:
            eintrag['nutzung'] = rumpf['nutzung']
        if 'textur_an' in rumpf:
            eintrag['textur_an'] = bool(rumpf['textur_an'])
        if manuell:
            eintrag['manuell'] = True
        return manuell

    @classmethod
    def _haupt_stellen(cls, eintrag, wert):
        if wert == '':
            if eintrag.get('kategorie') in cls.HAUPTKATEGORIEN:
                eintrag['kategorie'] = 'neben'
                return True
            return False
        for w, _, kategorie, ansicht in cls.HAUPT:
            if w == wert:
                eintrag['kategorie'] = kategorie
                eintrag['ansicht'] = ansicht
                eintrag.pop('teil', None)
                if float(eintrag.get('gewicht') or 0) <= 0:
                    eintrag['gewicht'] = 1.0   # sonst zählt das neue Hauptbild nirgends
                return True
        return False

    @classmethod
    def _neben_stellen(cls, eintrag, wert):
        if wert == '':
            if eintrag.get('kategorie') in cls.NEBENKATEGORIEN:
                eintrag['kategorie'] = 'leer'
                eintrag.pop('teil', None)
                return True
            return False
        for w, _, kategorie, teil, _ in cls.NEBEN:
            if w == wert:
                eintrag['kategorie'] = kategorie
                if teil:
                    eintrag['teil'] = teil
                else:
                    eintrag.pop('teil', None)
                return True
        return False

    # ----------------------------------------------------------- Vorgaben

    @classmethod
    def vorgaben_pruefen(cls, roh, namen):
        """`{datei: {haupt, neben, nutzung}}` aus dem Upload-Feld `typen` (JSON) — nur für
        die eben abgelegten Dateien, nur bekannte Werte (19.09.2026: die Testfallbilder und
        „Bild für die Textur" kennen ihren Typ, bevor die Sichtung läuft)."""
        import json

        if not roh:
            return {}
        try:
            daten = json.loads(roh) if isinstance(roh, str) else roh
        except ValueError:
            return {}
        if not isinstance(daten, dict):
            return {}
        haupt = {w for w, _, _, _ in cls.HAUPT}
        neben = {w for w, _, _, _, _ in cls.NEBEN}
        nutzung = {w for w, _, _ in cls.NUTZUNG}
        aus = {}
        for name in namen:
            wahl = daten.get(name)
            if not isinstance(wahl, dict):
                continue
            sauber = {}
            if wahl.get('haupt') in haupt:
                sauber['haupt'] = wahl['haupt']
            if wahl.get('neben') in neben:
                sauber['neben'] = wahl['neben']
            if wahl.get('nutzung') in nutzung:
                sauber['nutzung'] = wahl['nutzung']
            if sauber:
                aus[name] = sauber
        return aus
