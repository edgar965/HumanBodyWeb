# -*- coding: utf-8 -*-
"""Engine2d3dKleidernurtrellis — „2D3D Kleider" formt sein Netz NUR mit TRELLIS.2, kein Hunyuan3D (02.10.2026).

Edgar (02.10.2026): „ich brauche NUR trellis in dem Workflow, kein Hunyan". Der Katalog der Gruppe `netz` ist der der Seite
„Mesh" (`Meshoptionen`) und kennt vier Formmodelle, dazu einen Wert, den es nur mit Hunyuan3D gibt: Textur „malerei"
(Hunyuan malt auf die TRELLIS-Form). Hier werden sie für diesen Bereich gestrichen:

    formmodell   immer `trellis2` — das Feld steht nicht im Formular (`Engine2d3dKleideroptionen.SICHTBAR`)
    textur       fotos_ki · fotos · ki · keine

und die Beschriftungen nennen Hunyuan3D nicht mehr. Ein gespeicherter Auftrag mit einem anderen Wert fällt beim Lesen auf die
Vorgabe des Katalogs zurück (`pruefen`), ohne dass die Datenbank angefasst wird. Die Seite „Mesh" bleibt unverändert. Die
Auflösung (Octree 768 „sehr hoch" gibt es nur bei Hunyuan3D) steht in der Gruppe `mesh` mit den drei TRELLIS-Stufen
(`Engine2d3dKleidermeshoptionen`).
"""

from .meshoptionen import Meshoptionen

__all__ = ['Engine2d3dKleidernurtrellis']


class Engine2d3dKleidernurtrellis:
    ERLAUBT = {
        'formmodell': ('trellis2',),
        'textur': ('fotos_ki', 'fotos', 'ki', 'keine'),
    }
    TEXTE = {
        'textur': {
            'fotos_ki': 'Fotos aufprojiziert, Lücken aus der Textur von TRELLIS.2',
            'fotos': 'Nur Fotos (Lücken aufgefüllt)',
            'ki': 'Nur die Textur von TRELLIS.2 (PBR)',
            'keine': 'Keine (grau)',
        },
    }
    HINWEISE = {
        'textur': 'Gemessen am 30.09.2026: „fotos_ki" legte bei „schnell" Fotoränder auf Arme und Beine, „ki" war '
                  'sauber.',
    }

    @classmethod
    def katalogfeld(cls, feld):
        """Das Feld, wie es dieser Bereich zeigt: nur die erlaubten Werte, ohne Hunyuan in den Texten."""
        schluessel = feld['schluessel']
        if schluessel not in cls.ERLAUBT:
            return feld
        texte = cls.TEXTE.get(schluessel, {})
        werte = [dict(w, text=texte.get(w['wert'], w['text'])) for w in feld.get('werte', [])
                 if w['wert'] in cls.ERLAUBT[schluessel]]
        aus = dict(feld, werte=werte)
        if schluessel in cls.HINWEISE:
            aus['hinweis'] = cls.HINWEISE[schluessel]
        return aus

    @classmethod
    def pruefen(cls, werte):
        """Die geprüften Werte der Gruppe `netz` — ein nicht erlaubter Wert wird zur Vorgabe des Katalogs."""
        vorgaben = Meshoptionen.vorgaben()
        aus = dict(werte)
        for schluessel, erlaubt in cls.ERLAUBT.items():
            if aus.get(schluessel) not in erlaubt:
                aus[schluessel] = vorgaben[schluessel]
        return aus
