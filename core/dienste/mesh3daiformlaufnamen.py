# -*- coding: utf-8 -*-
"""Mesh3daiformlaufnamen — deutsche Namen der Schlüssel, die ein Trainingslauf in `lauf_ergebnis.json` und `lauf.log` schreibt (Seite /mesh-3D-AI/formtraining/<lauf>/, 18.10.2026).

Die Schlüssel gehören den Trainingsskripten (`ProjektTemp/_wegwerf/mesh3dai_vorstufe_form2.py`, `…_form.py`, `…_stimmen_alle.py`); ein neuer Schlüssel erscheint auf der Seite unter seinem
Rohnamen, bis er hier einen Namen bekommt — nichts fällt weg. „Kleiner ist besser“ gilt für Fehler der Vorhersage; die Bezugsgrößen (mittlere Form, Grundfigur) sind keine Leistung des Laufs
und werden im Vergleich nicht gefärbt.
"""

__all__ = ['Mesh3daiformlaufnamen']


class Mesh3daiformlaufnamen:
    NAMEN = {
        # Verlauf (je Zwischenmessung)
        'training_mm': 'Training: Gelenke (Verlust)', 'form_verlust': 'Training: Formverlust', 'training_eval_mm': 'Training: Gelenke (Auswertung)',
        'training_form_mm': 'Training: Form', 'pruefung_mm': 'Prüfung: Gelenke', 'pruefung_form_mm': 'Prüfung: Form',
        'training_ziel_mm': 'Training: Ziel (Verlust)', 'training_kopf_mm': 'Training: Kopf (Verlust)', 'training_gelenke_mm': 'Training: Gelenke',
        'training_kopfform_mm': 'Training: Kopf-Form', 'pruefung_gelenke_mm': 'Prüfung: Gelenke', 'pruefung_kopfform_mm': 'Prüfung: Kopf-Form',
        # Ergebnis je Gruppe / je Figur
        'figuren': 'Figuren', 'proben': 'Proben', 'gelenke_mm': 'Gelenke (mm)', 'form_mm': 'Form (mm)', 'form_gemittelt_mm': 'Form, über die Posen gemittelt (mm)',
        'mittlere_form_mm': 'Bezug: mittlere Form (mm)', 'grundfigur_mm': 'Bezug: Grundfigur (mm)', 'streuung_mm': 'Streuung über die Posen (mm)',
        'kopf_form_mm': 'Kopf-Form (mm)', 'kopf_form_mittlere_form_mm': 'Bezug: Kopf-Form der mittleren Form (mm)',
        'nase_mm': 'Nase (mm)', 'nase_mittlere_form_mm': 'Bezug: Nase der mittleren Form (mm)', 'mund_mm': 'Mund (mm)', 'mund_mittlere_form_mm': 'Bezug: Mund der mittleren Form (mm)',
        'augen_mm': 'Augen (mm)', 'augen_mittlere_form_mm': 'Bezug: Augen der mittleren Form (mm)', 'ohren_mm': 'Ohren (mm)', 'ohren_mittlere_form_mm': 'Bezug: Ohren der mittleren Form (mm)',
        'alter_fehler_jahre': 'Alter (Jahre daneben)', 'alter_mittel_fehler_jahre': 'Bezug: Alter des Mittels (Jahre daneben)',
        'mm': 'Gelenke (mm)', 'median_mm': 'Gelenke, Median (mm)', 'rig_verfaelscht_mm': 'Rig verfälscht (mm)',
        # Einstellungen
        'name': 'Name', 'kopf': 'Kopf des Netzes', 'netz': 'Netz', 'formmass': 'Formmaß (Fassung)', 'eingang': 'Eingang (Wolkenfassung)', 'formkopf': 'Formregler im Kopf',
        'formregler_datei': 'Formregler-Datei', 'daten': 'Bezugsjob', 'training_daten': 'Jobs im Training', 'formvarianten': 'Formvarianten', 'epochen': 'Epochen',
        'dauer_s': 'Trainingszeit (s)', 'parameter': 'Gewichte', 'punkte_je_probe': 'Punkte je Probe', 'kopf_knochen': 'Kopfknochen', 'kopf_punkte': 'Kopfpunkte',
        'drehung_grad': 'Zufallsdrehung (°)', 'aufmerk': 'Gewicht Aufmerksamkeit', 'farbe': 'Farbe', 'form_gewicht': 'Gewicht Form', 'kopf_gewicht': 'Gewicht Kopf',
        'haut_anteil': 'Anteil Hautvarianten', 'alter_gewicht': 'Gewicht Alter', 'saat': 'Saat', 'wolken': 'Wolken k', 'wolken_mit_hautfeldern': 'Wolken mit Hautfeldern',
        'start': 'Start aus Lauf', 'k_training': 'Wolken je Probe (Training)', 'stoerung_pruefung_mm': 'Störung der Prüfung (mm)',
        'pruefung_grund_teilfarbe_mm': 'Prüfung mit Teilfarbe (mm)', 'ausgelassen_pruefung': 'Ausgelassene Prüfwolken', 'haeute': 'Hautsätze',
        'proben_alle': 'Proben (Wolken)', 'parameter_kopf': 'Gewichte des Kopfs',
    }
    #: Schlüssel, die eine Bezugsgröße sind (keine Leistung des Laufs)
    BEZUG = ('mittlere', 'grundfigur', 'mittel_fehler')
    #: Gruppen von Figuren im Ergebnis je Figur
    GRUPPEN = {'training': 'Training', 'pruefung': 'Prüfung'}
    #: Körperteile der Vorstufen-Läufe (`je_figur` → `je_gruppe_mm`)
    TEILE = {'arm': 'Arm', 'bein': 'Bein', 'finger': 'Finger', 'fuss': 'Fuß', 'gesicht': 'Gesicht', 'hand': 'Hand', 'kopf': 'Kopf', 'rumpf': 'Rumpf', 'zehen': 'Zehen'}

    @classmethod
    def name(cls, schluessel):
        if '.' in schluessel:
            oben, teil = schluessel.split('.', 1)
            return '%s (mm)' % cls.TEILE.get(teil, teil) if oben.endswith('_mm') else '%s: %s' % (cls.name(oben), teil)
        return cls.NAMEN.get(schluessel, schluessel)

    @staticmethod
    def flach(werte):
        """Zahlen eines Ergebnisses, eine Ebene tiefer verschachtelte als `oben.unten` — `je_gruppe_mm: {arm: 8,3}` → `je_gruppe_mm.arm`."""
        aus = {}
        for k, v in (werte or {}).items():
            if isinstance(v, dict):
                aus.update({'%s.%s' % (k, u): w for u, w in v.items() if isinstance(w, (int, float)) and not isinstance(w, bool)})
            elif isinstance(v, (int, float)) and not isinstance(v, bool):
                aus[k] = v
        return aus

    @classmethod
    def bezug(cls, schluessel):
        return any(b in schluessel for b in cls.BEZUG)

    @classmethod
    def fehler(cls, schluessel):
        """Ein Fehlermaß der Vorhersage: kleiner ist besser (mm oder Jahre, keine Bezugsgröße, kein Verlust des Trainingsschritts)."""
        oben = schluessel.split('.', 1)[0]
        return (oben == 'mm' or oben.endswith(('_mm', '_jahre'))) and not cls.bezug(schluessel)
