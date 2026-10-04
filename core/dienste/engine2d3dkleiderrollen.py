# -*- coding: utf-8 -*-
"""Engine2d3dKleiderrollen — welche Fotos wohin gehen: Netz-Pipeline oder nur Iterationen (03.10.2026).

Edgar (03.10.2026, Job „Randy": 8 Ansichten, vier davon auf „aus"): „Diagonalbilder sind für TRELLIS nicht nützlich — mach einen
Bereich, welche Bilder du für die TRELLIS-Pipeline benutzt, und darunter welche zusätzlichen du für die Iterationen nutzt."

Ein Foto hat genau eine Rolle (`Meshoptionen.ROLLEN`), dazu kommt hier „Nur Iterationen":

    Netz-Pipeline     alle Rollen außer „aus" und „Nur Iterationen" — sie gehen in den Schritt „netz" (Form- und Texturmodell)
                      UND in die Iterationen (Blickwinkel, Note, Fotoprojektion)
    Nur Iterationen   das Foto kommt NICHT in den Schritt „netz" (die Formmodelle nehmen höchstens die vier senkrechten Ansichten,
                      `Meshoptionen`: Hunyuan3D-2mv „bis zu vier Fotos (vorne/hinten/links/rechts)"), zählt aber in den Iterationen
                      (`Iterationsreferenz.laden` lässt nur „aus" und Gewicht 0 weg)
    aus               nirgends

Den Blickwinkel eines „Nur Iterationen"-Fotos (Grad ab vorn, positiv zur linken Seite der Figur) gibt `winkel` am Foto
(`Iterationsreferenz.winkel_von`, erste Quelle); ohne ihn schätzt ihn die Pose (`Blickwinkelschaetzung`).
"""

from .meshoptionen import Meshoptionen

__all__ = ['Engine2d3dKleiderrollen']


class Engine2d3dKleiderrollen:
    NUR_ITERATIONEN = 'iterationen'
    AUS = 'aus'
    TEXT = 'Nur Iterationen (nicht fürs Netz)'

    @classmethod
    def liste(cls):
        """Die Rollen der Bildauswahl: die der Mesh-Seite, „Nur Iterationen" vor „Nicht verwenden"."""
        rollen = list(Meshoptionen.ROLLEN)
        stelle = next((i for i, (wert, _text) in enumerate(rollen) if wert == cls.AUS), len(rollen))
        rollen.insert(stelle, (cls.NUR_ITERATIONEN, cls.TEXT))
        return rollen

    @classmethod
    def katalog(cls):
        return [{'wert': w, 'text': t} for w, t in cls.liste()]

    @classmethod
    def pruefen(cls, rolle):
        """Eine gültige Rolle, sonst „auto" (wie `Meshoptionen.rolle_pruefen`, aber mit „Nur Iterationen")."""
        return rolle if rolle in dict(cls.liste()) else 'auto'

    @classmethod
    def fuer_netz(cls, eintrag):
        """True, wenn das Foto in den Schritt „netz" geht."""
        return eintrag.get('rolle') not in (cls.AUS, cls.NUR_ITERATIONEN)

    @classmethod
    def nur_iterationen(cls, bilder):
        """Die Dateinamen der Fotos, die der Schritt „netz" nicht bekommt."""
        return {b.get('datei') for b in bilder or [] if isinstance(b, dict) and b.get('rolle') == cls.NUR_ITERATIONEN}

    @staticmethod
    def farbe_pruefen(wert):
        """`farbe` am Foto: False = das Foto zählt nur für die FORM (Umriss, Note), nicht für Farbe und Textur (Fotoprojektion).
        Gemessen 03.10.2026 (Randy, Runde 40 gegen 41): Mit den vier Schrägfotos in der Projektion wurde der Rückendruck des
        Hemds doppelt und verwaschen — die Schrägansichten passen nicht deckungsgleich aufs Modell. None/unklar = Vorgabe (an)."""
        if isinstance(wert, bool):
            return wert
        return {'0': False, 'false': False, 'aus': False, '1': True, 'true': True, 'an': True}.get(str(wert).strip().lower())

    @staticmethod
    def winkel_pruefen(wert):
        """Grad in (−180, 180] oder None (kein Winkel von Hand — dann schätzt ihn die Pose); Unsinn ergibt None."""
        if wert is None or isinstance(wert, bool) or wert == '':
            return None
        try:
            grad = float(wert)
        except (TypeError, ValueError):
            return None
        if grad != grad or abs(grad) == float('inf'):          # NaN, unendlich
            return None
        grad = (grad + 180.0) % 360.0 - 180.0
        return 180.0 if grad == -180.0 else round(grad, 1)
