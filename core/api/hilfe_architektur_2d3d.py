# -*- coding: utf-8 -*-
"""Hilfe -> Architektur -> 2D3D: wie die Iterationen von „2D3D Kleider" gebaut sind.

Edgar (02.10.2026): „in welchem Schritt schaut die KI auf das Ergebnis und baut den Code für die nächste Runde?
Schreibe alles über die Implementierung der 2D3D Iterationen in eine neue Seite Hilfe - Architektur 2D3D". Die
Zeilen (Schritte, Klassen, Messungen) kommen aus `core.dienste.architektur2d3d`; jede Klasse wird mit dem ersten Satz
ihres Docstrings und ihrer Zeilenzahl aus dem Code gelesen, damit die Seite nicht hinter dem Code zurückbleibt.
"""

from ..dienste.architektur2d3d import Architektur2d3d
from ..dienste.architektur2d3dmodellvergleich import Architektur2d3dmodellvergleich
from ..dienste.kopfpipelinevergleich import Kopfpipelinevergleich
from .hilfeseite import Hilfeseite


class HilfeArchitektur2d3d(Hilfeseite):
    template_name = 'hilfe/architektur_2d3d.html'
    AKTIV = 'hilfe_architektur_2d3d'

    def kontext(self):
        """Architektur plus der Foto-zu-3D-Kopf-Teil (früher /hilfe/2d-3d/, 06.10.2026); eigene Namen, damit `messung` nicht kollidiert."""
        ergebnis = Architektur2d3d.kontext()
        ergebnis.update({
            'kopf_messung': Kopfpipelinevergleich.MESSUNG,
            'kopf_gemessen': Kopfpipelinevergleich.gemessen(),
            'kopf_extern': Kopfpipelinevergleich.extern(),
        })
        # Vergleichstabelle TRELLIS/Hunyuan3D/Pixal3D gegen Meshy & Co. (Edgar, 08.10.2026: „Mach [...] eine
        # Tabelle im djangoBase Stil mit allen Modellen [...] auflösung, geschwindigkeit, qualität, größe [...]").
        ergebnis.update(Architektur2d3dmodellvergleich.kontext())
        return ergebnis
