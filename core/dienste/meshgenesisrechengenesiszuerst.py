# -*- coding: utf-8 -*-
"""Meshgenesisrechengenesiszuerst — die Schritte der Kette „Genesis zuerst“ und wo sie in `Meshgenesisrechenlauf.SCHRITTE` stehen (aus `meshgenesisrechenlauf.py` abgeteilt 19.11.2026
abends, als dort der Schritt „stoff“ dazukam; die Datei stand bei 305 Zeilen).

„Genesis zuerst“ (12.11.2026, Edgar: „mach den Umbau“, Konzept `Docu/konzepte/2026-11-12_genesis-zuerst-konzept.md`, Abschnitt 9 und 10d Punkt 3): nur für einen Test mit `genesis_zuerst` in
`einstellung.json` (Häkchen am Foto-Genesis-Job, `Fotogenesisgenesisstart`). Die Figur nur aus Reglern (`--nur-regler`), danach die Prüfung „Proportionen wie im Foto“; der Kostüm-Weg schneidet
weiter, aber nur als Messung, das Ergebnis tragen Stücke der Garderobe (Weg z), und die Prüfung misst diese Stücke (`--weg z`). Die alte Kette bleibt die Vorgabe.

    Meshgenesisrechengenesiszuerst.einreihen(schritte)      # → Schritte des Tests mit „Genesis zuerst“
"""

__all__ = ['Meshgenesisrechengenesiszuerst']


class Meshgenesisrechengenesiszuerst:
    #: (Schlüssel, Klartext, Skript und Argumente — {k} Kennung, {g} Geschlecht, {…} aus den KI-Fassungen); ersetzt den gleichnamigen Schritt oder kommt nach `NACH`
    SCHRITTE = {
        'zeile1': ('zeile1', 'Figur aus Zeile 1, nur Regler (Genesis zuerst)', ['-u', 'meshgenesis_zeile1figur.py', '--nur', '{k}', '--geschlecht', '{g}', '--nur-regler']),
        'proportionen': ('proportionen', 'Prüfung „Proportionen wie im Foto“ (Genesis zuerst)', ['-u', 'meshgenesis_proportionen.py', '--nur', '{k}', '--geschlecht', '{g}']),
        # nur die Haut, ohne die Stücke von Weg g (12.11.2026, Edgar: „optimiere“; am Zauberer 67,6 s): die Kleiderliste zeigt hier nur Weg z
        'haut': ('haut', 'Haut aus der KI (Stufe 2: Farbe je Texel, ohne Kleider von Weg g)', ['-u', 'meshgenesis_stufe2_lauf.py', '--nur-einsatz', '{stufe2}', '--fassung', '{stufe2_fassung}',
                                                                                                '--test', '{k}', '--job', '', '--geschlecht', '{g}', '--hautki', '{hautki}', '--ohne-kleider']),
        'kleider': ('kleider', 'Kleider und Haar aus dem Mesh messen (Kostüm-Weg, nur Messung für Genesis zuerst)', ['-u', 'meshgenesis_kostuem_lauf.py', '--nur', '{k}', '--stufe', '{kostuem_stufe}',
                                                                                                                      '--ohne-pruefung']),
        'garderobe': ('garderobe', 'Kleider, Haar und Requisit aus der Kleiderbibliothek wählen und anpassen (Genesis zuerst)',
                      ['-u', 'meshgenesis_garderobe_lauf.py', '--nur', '{k}', '--geschlecht', '{g}']),
        # 18.11.2026 (Edgar: „kannst du den Code nicht mergen?“, `bausteine/stueckveredelung.py`): Stücke von Weg z mit Materialklassen aus dem Foto, Oberfläche und Glättung (Zeilen bs_*)
        # 19.11.2026 (Edgar: „Alles im generischen Code auch drin? Mach das“): dazu Stufe 2 — Hüllen je Klasse mit Goldkanten, Rock, Stiefel (`bausteine/generischkostuem.py`, Zeilen gk_*)
        'bausteine': ('bausteine', 'Kostüm aus Bausteinen: Materialklassen aus dem Foto, Hüllen mit Goldkanten, Rock, Stiefel (Genesis zuerst)',
                      ['-u', 'meshgenesis_kostuem_bausteine.py', '--nur', '{k}', '--geschlecht', '{g}', '--huellen']),
        # 19.11.2026 (Edgar: „Methode: Kleiderbibliothek (ehemals Garderobe) und Drapieren … am besten rechnest du 2 Ergebnisse“): zweites Ergebnis neben der Kleiderbibliothek,
        # die Vorgabe bleibt; die Foto-Genesis-Seite schaltet um (`Fotogenesiskleidermethode`). Gemessen 30 s je Stück (Median, 64 echte Stücke)
        'drapieren': ('drapieren', 'Kleider drapieren: Schnitt aus dem Stück, als Stoff genäht und drapiert (zweites Ergebnis neben der Kleiderbibliothek, Genesis zuerst)',
                      ['-u', 'meshgenesis_drapieren_lauf.py', '--nur', '{k}', '--geschlecht', '{g}']),
        'pruefung': ('pruefung', 'Prüfung der Stücke der Kleiderbibliothek: Testfälle und Tanz', ['-u', 'meshgenesis_kostuem_lauf.py', '--nur', '{k}', '--stufe', '{kostuem_stufe}',
                                                                                                  '--nur-pruefen', '--weg', 'z']),
        # 19.11.2026 abends (Edgar: „Ja“ auf „Soll der Stoff ein fester Job-Schritt nach Weg z werden?“): die Stücke von Weg z (auch die aus den Bausteinen) über die Animation der Seite als
        # Stoff (Stoffsolver mit Kernmotor); die Seite zeigt sie dann mit Falten statt als zweite Haut. Gemessen gk_anzug + gk_mieder (goldprinzessin_mesh_genesis_64): 5 + 9 s Simulation
        'stoff': ('stoff', 'Kleider der Kleiderbibliothek als Stoff über die Animation der Seite (Genesis zuerst)', ['-u', 'meshgenesis_kleiderstoff_lauf.py', '--nur', '{k}', '--geschlecht', '{g}']),
    }
    #: Schritte, die nach einem Schritt der alten Kette dazukommen (in dieser Reihenfolge). „stoff“ als letzter: ein Fehler dort hält keinen anderen Schritt auf, die Seite zeigt dann gehäutet
    NACH = {'zeile1': ('proportionen',), 'kleider': ('garderobe', 'bausteine', 'drapieren'), 'pruefung': ('stoff',)}

    @classmethod
    def einreihen(cls, schritte):
        u"""Schritte der alten Kette → Schritte mit „Genesis zuerst“: gleichnamige ersetzt, `NACH` eingefügt."""
        aus = []
        for s in schritte:
            aus.append(cls.SCHRITTE.get(s[0], s))
            aus.extend(cls.SCHRITTE[n] for n in cls.NACH.get(s[0], ()))
        return tuple(aus)
