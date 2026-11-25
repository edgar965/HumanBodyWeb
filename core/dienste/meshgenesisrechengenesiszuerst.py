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
        # 20.11.2026 (Edgar: „mach doch einen dritten Modus für die Kleider - "Eigen" neben Drapieren und Bibliothek und rechne das auch für jeden Job aus“): drittes Ergebnis, Weg e
        'eigen': ('eigen', 'Eigene Kleider: je Kleidungsstück ein eigenes Stück, an das Stück aus dem Netz gepasst (drittes Ergebnis neben Kleiderbibliothek und Drapieren, Genesis zuerst)',
                  ['-u', 'meshgenesis_eigen_lauf.py', '--nur', '{k}', '--geschlecht', '{g}']),
        # 22.11.2026 (Paket K6 von Edgar: „Passend in die Kette und in die Kostüm-Prüfung“): viertes Ergebnis, Weg p (`meshgenesis_passend_lauf.py`, bis dahin nur von Hand)
        'passend': ('passend', 'Kleider „Passend“: je Kleidungsstück das passendste Stück der Kleiderbibliothek aus mehreren Kandidaten, an das Netzstück gepasst (viertes Ergebnis, Genesis zuerst)',
                    ['-u', 'meshgenesis_passend_lauf.py', '--nur', '{k}', '--geschlecht', '{g}']),
        # 21.11.2026 (Edgar: „mach weiter mit dem Plan“, Konzept `2026-11-21_bibliothek-anpassen-konzept.md` Abschnitt 10): die gewählten Kleidungsregeln auf die Kleidungsstücke aller drei
        # Wege (Fetzen weg, glatter Rand, Rock an beiden Beinen), vor Prüfung und Stoff; Wahl: Einstellungen → Kleider, am Job `kleider_regeln` (`Kleidregelnaufloesung`)
        'kleidregeln': ('kleidregeln', 'Kleidungsregeln auf Kleiderbibliothek, Drapieren, Eigen und Passend (Löcher schließen, Fetzen weg, glatter Rand, Saum, Rock — wie gewählt, Genesis zuerst)',
                        ['-u', 'meshgenesis_kleidregeln_lauf.py', '--nur', '{k}', '--geschlecht', '{g}']),
        'pruefung': ('pruefung', 'Prüfung der Stücke der Kleiderbibliothek: Testfälle und Tanz', ['-u', 'meshgenesis_kostuem_lauf.py', '--nur', '{k}', '--stufe', '{kostuem_stufe}',
                                                                                                  '--nur-pruefen', '--weg', 'z']),
        # 22.11.2026 (Paket K2/K6 von Edgar: „volle Kostüm-Prüfung“ für Drapieren und Passend): dieselbe Prüfung mit der Kleidung des Wegs, Haar, Hut, Schuhe und Requisiten aus der
        # Kleiderbibliothek (wie die Seite), Tabelle `k/testfaelle_<weg>.json` (`Kostuempruefung.datei_name`); ohne Stücke des Wegs meldet der Schritt den Test als gescheitert und geht weiter
        'pruefung_f': ('pruefung_f', 'Prüfung der Stücke von Drapieren: Testfälle und Tanz', ['-u', 'meshgenesis_kostuem_lauf.py', '--nur', '{k}', '--stufe', '{kostuem_stufe}',
                                                                                              '--nur-pruefen', '--weg', 'f']),
        'pruefung_p': ('pruefung_p', 'Prüfung der Stücke von Passend: Testfälle und Tanz', ['-u', 'meshgenesis_kostuem_lauf.py', '--nur', '{k}', '--stufe', '{kostuem_stufe}',
                                                                                            '--nur-pruefen', '--weg', 'p']),
    }
    #: Schritte, die nach einem Schritt der alten Kette dazukommen (in dieser Reihenfolge). „stoff“ und „haar“ (Physik über die Animation) standen vom 19./20.11. bis 25.11.2026 am Ende der Kette;
    #: seitdem rechnet sie erst der MP4-Export (Edgar: „physik muss doch erst beim export in mp4 berechnet werden“, `Exportleistekettenlauf`) — die Seite zeigt bis dahin gehäutet bzw. ihre Pendel
    NACH = {'zeile1': ('proportionen',), 'kleider': ('garderobe', 'bausteine', 'drapieren', 'eigen', 'passend', 'kleidregeln'), 'pruefung': ('pruefung_f', 'pruefung_p')}
    #: Versuch 21.11.2026 (Edgar: „ja, teste Genesis zuerst mit Mesh-Reglern an edgar_fotos“): mit `genesis_zuerst_mesh_regler` in `einstellung.json` behält die Figur den freien
    #: Versatz der Einpassung als Mesh-Regler (Form wie das Netz, `abgleich.mittel_mm` 0 statt 15,1 an edgar_fotos), die Kleiderwege bleiben die von „Genesis zuerst“.
    #: `meshgenesis_zeile1figur.py` liest dieselbe Einstellung (ein Arbeitsprozess mit älterer Schrittliste rechnet so trotzdem das Gewählte).
    ZEILE1_MESH_REGLER = ('zeile1', 'Figur aus Zeile 1, Regler und Mesh-Regler (Genesis zuerst mit Form des Netzes)',
                          ['-u', 'meshgenesis_zeile1figur.py', '--nur', '{k}', '--geschlecht', '{g}'])

    @classmethod
    def einreihen(cls, schritte, mesh_regler=False):
        u"""Schritte der alten Kette → Schritte mit „Genesis zuerst“: gleichnamige ersetzt, `NACH` eingefügt; `mesh_regler`: „zeile1“ mit Mesh-Reglern (`ZEILE1_MESH_REGLER`)."""
        ersatz = dict(cls.SCHRITTE, zeile1=cls.ZEILE1_MESH_REGLER) if mesh_regler else cls.SCHRITTE
        aus = []
        for s in schritte:
            aus.append(ersatz.get(s[0], s))
            aus.extend(cls.SCHRITTE[n] for n in cls.NACH.get(s[0], ()))
        return tuple(aus)
