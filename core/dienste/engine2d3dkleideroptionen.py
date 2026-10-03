# -*- coding: utf-8 -*-
"""Engine2d3dKleideroptionen — was der Bereich „2D3D Kleider" (`engine2d3dkleider`) einstellen lässt, mit Vorgaben (30.09.2026).

Sechs Gruppen, je mit ihrem eigenen Katalog geprüft (gleichnamige Felder meinen in den Katalogen
Verschiedenes):

    figur        Grundfigur und „Als Modell speichern" (`Meshfiguroptionen` — nur diese zwei Felder)
    netz         Netz aus den Fotos, NUR mit TRELLIS.2: Textur, Freistellen, Licht (`Meshoptionen`, Reiter „Mesh";
                 Hunyuan3D gestrichen, `Engine2d3dKleidernurtrellis`)
    mesh         das Interface von TRELLIS.2 wie im Hugging-Face-Space: Resolution, Seed, Decimation Target, Texture Size
                 und die Sampler der drei Stufen (`Engine2d3dKleidermeshoptionen`, 02.10.2026)
    koerper      woher die Figur kommt: übernehmen aus „Mesh to 3D" oder rechnen (`Engine2d3dKleiderkoerperoptionen`)
    iterationen  Iterationen: Begutachtung oder automatisch, Runden, Kandidaten, Prüf-KI (`Iterationsoptionen`)
    film         BVH, Bilder, Größe (`Engine2d3dKleiderfilmoptionen`)

`figur.modell` hat hier die Vorgabe „aus" (in „Mesh to 3D" „an"): Jeder Lauf würde sonst ein Genesis-Modell
in die Modellbibliothek schreiben (`HumanBody/data/models`). Gespeichert wird über den Knopf „Modell
speichern".
"""

from .engine2d3dkleiderfilmoptionen import Engine2d3dKleiderfilmoptionen
from .engine2d3dkleiderkoerperoptionen import Engine2d3dKleiderkoerperoptionen
from .engine2d3dkleidermeshoptionen import Engine2d3dKleidermeshoptionen
from .engine2d3dkleidernurtrellis import Engine2d3dKleidernurtrellis
from .iterationsoptionen import Iterationsoptionen
from .meshfiguroptionen import Meshfiguroptionen
from .meshoptionen import Meshoptionen

__all__ = ['Engine2d3dKleideroptionen']


class Engine2d3dKleideroptionen:
    GRUPPEN = ('figur', 'netz', 'mesh', 'koerper', 'iterationen', 'film')
    #: Felder, die im Formular erscheinen (None = alle des Katalogs).
    SICHTBAR = {
        'figur': ('basis', 'modell'),
        # `textur` seit 30.09.2026 sichtbar: „fotos_ki" legte bei „schnell" Fotoränder auf Arme und Beine, „ki" (die
        # PBR-Textur von TRELLIS.2, wie im Mesh-Auftrag 2026.09.29.00.09.00) war sauber — Edgar: „bessere Textur".
        # `formmodell` nicht mehr (02.10.2026): hier gibt es nur TRELLIS.2 (`Engine2d3dKleidernurtrellis`). `aufloesung`,
        # `flaechen` und `texturgroesse` auch nicht: Sie stehen seit 02.10.2026 im Abschnitt „Mesh" (Gruppe `mesh`, wie
        # im Hugging-Face-Space) — `UEBERNAHME` holt den gespeicherten Wert von hier.
        'netz': ('textur', 'freistellen', 'licht'),
        'mesh': None,
        'koerper': None,
        'iterationen': None,
        'film': None,
    }
    #: Felder, die bis 02.10.2026 in der Gruppe `netz` standen und jetzt zur Gruppe `mesh` gehören: Ein Auftrag, dessen
    #: Gruppe `mesh` sie noch nicht trägt, behält den Wert, den er unter `netz` gespeichert hat.
    UEBERNAHME = ('aufloesung', 'flaechen', 'texturgroesse')
    #: Vorgaben, die hier von der Vorlage abweichen. (`flaechen` 100.000 steht jetzt in `Engine2d3dKleidermeshoptionen`.)
    ABWEICHUNGEN = {'figur': {'modell': 'aus'}, 'netz': {}, 'mesh': {}, 'koerper': {}, 'iterationen': {}, 'film': {}}
    PRUEFER = (
        ('figur', Meshfiguroptionen),
        ('netz', Meshoptionen),
        ('mesh', Engine2d3dKleidermeshoptionen),
        ('koerper', Engine2d3dKleiderkoerperoptionen),
        ('iterationen', Iterationsoptionen),
        ('film', Engine2d3dKleiderfilmoptionen),
    )

    @classmethod
    def katalog(cls):
        """`{figur: {optionen}, netz: …, mesh: …, koerper: …, iterationen: …, film: …, rollen}` für das Formular."""
        aus = {}
        for gruppe, pruefer in cls.PRUEFER:
            felder = []
            katalog = pruefer.katalog()
            for feld in katalog['optionen']:
                sichtbar = cls.SICHTBAR[gruppe]
                if sichtbar is not None and feld['schluessel'] not in sichtbar:
                    continue
                if gruppe == 'netz':
                    feld = Engine2d3dKleidernurtrellis.katalogfeld(feld)
                felder.append(
                    dict(feld, vorgabe=cls.ABWEICHUNGEN[gruppe].get(feld['schluessel'], feld['vorgabe']))
                )
            aus[gruppe] = {'optionen': felder}
            if katalog.get('fein_titel'):  # Überschrift des zugeklappten Bereichs (`Meshoptionenformular`)
                aus[gruppe]['fein_titel'] = katalog['fein_titel']
            if katalog.get('gilt_nach'):  # Feld, nach dem das Formular Felder mit `gilt` ein- und ausblendet
                aus[gruppe]['gilt_nach'] = katalog['gilt_nach']
        # Die Rollen der Bildauswahl (vorne/links/rechts/hinten geben den Blickwinkel der Iterationen).
        aus['rollen'] = [{'wert': w, 'text': t} for w, t in Meshoptionen.ROLLEN]
        return aus

    @classmethod
    def pruefen(cls, roh):
        """Jede Gruppe gegen ihren Katalog — bekannte Schlüssel, gültige Werte, sonst Vorgabe."""
        roh = roh if isinstance(roh, dict) else {}
        aus = {}
        for gruppe, pruefer in cls.PRUEFER:
            gruppenwerte = roh.get(gruppe)
            frueher = {}
            if gruppe == 'mesh' and isinstance(roh.get('netz'), dict):
                frueher = {k: roh['netz'][k] for k in cls.UEBERNAHME if k in roh['netz']}
            werte = {**cls.ABWEICHUNGEN[gruppe], **frueher, **(gruppenwerte if isinstance(gruppenwerte, dict) else {})}
            aus[gruppe] = pruefer.pruefen(werte)
        aus['netz'] = Engine2d3dKleidernurtrellis.pruefen(aus['netz'])
        return aus

    @classmethod
    def mischen(cls, alt, neu):
        """`neu` über `alt` legen, Gruppe für Gruppe (eine Seite schickt nur, was sie kennt) — geprüft."""
        alt, neu = (alt if isinstance(alt, dict) else {}), (neu if isinstance(neu, dict) else {})
        return cls.pruefen(
            {
                g: {
                    **(alt.get(g) if isinstance(alt.get(g), dict) else {}),
                    **(neu.get(g) if isinstance(neu.get(g), dict) else {}),
                }
                for g in cls.GRUPPEN
            }
        )

    @classmethod
    def figur(cls, optionen):
        """Die Optionen der Figur — dieselbe Form wie `Meshfiguroptionen.pruefen`."""
        return cls.pruefen(optionen)['figur']

    @classmethod
    def netz(cls, optionen):
        return cls.pruefen(optionen)['netz']

    @classmethod
    def mesh(cls, optionen):
        """Die Regler von TRELLIS.2 (Seed, Stage 1–3) — der Runner liest sie über `Engine2d3dKleidernetz.beschreibung`."""
        return cls.pruefen(optionen)['mesh']

    @classmethod
    def koerper(cls, optionen):
        return cls.pruefen(optionen)['koerper']

    @classmethod
    def iterationen(cls, optionen):
        return cls.pruefen(optionen)['iterationen']

    @classmethod
    def film(cls, optionen):
        """Die Optionen des Films (BVH, Bilder, Größe)."""
        return cls.pruefen(optionen)['film']
