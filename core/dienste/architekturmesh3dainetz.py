# -*- coding: utf-8 -*-
"""Architekturmesh3dainetz — das Netz von Mesh3D-AI Schicht für Schicht, für Hilfe → Architektur → Mesh3DAI (16.10.2026).

Edgar: „Mach erstmal einen Plan des Netzes, ich bin Entwickler und möchte alles verstehen … eingabe, Netz, wieviele Neuronen, wieviele Schichten, welcher Netztyp".
Die Tabelle zeigt das Netz des Bezugslaufs: `HEUTE` (erstes Netz, `mesh3dai_ursula_netz.py`), mit Daz-Winkeln, `STIMMEN` (`mesh3dai_stimmen_netz.py`) oder `STIMMEN` + `formkopf`
(`mesh3dai_formnetz.py`, seit 16.10.2026 abends). Der frühere „Plan“ (ein Vektor, mehrere Köpfe) ist überholt; welche Köpfe gebaut und welche vorgeschlagen sind, steht in `Architekturmesh3daiplan.koepfe`.
Die Gewichte je Schicht werden hier aus Ein- und Ausgang GERECHNET (1×1-Faltung ohne Bias + BatchNorm = ein·aus + 2·aus; voll verbunden = ein·aus + aus, mit BatchNorm + 2·aus) und gegen
`parameter` in `lauf_ergebnis.json` des jüngsten Laufs geprüft — weicht die Summe ab, steht ein Befund auf der Seite (dann beschreibt die Tabelle ein anderes Netz als das, das gelaufen ist).
„Neuronen" heißt bei einem Punktnetz: Kanäle je Punkt — dieselben Gewichte gelten für jeden der 4.096 Punkte; „Werte je Probe" = Punkte × Kanäle (bzw. Kanten × Kanäle vor dem Maximum).
"""

import json

__all__ = ['Architekturmesh3dainetz']

PUNKTE = 4096
K = 16


def _faltung(ein, aus):
    """1×1-Faltung ohne Bias + BatchNorm (Gewicht und Verschiebung je Kanal)."""
    return ein * aus + 2 * aus


def _voll(ein, aus, norm=True):
    return ein * aus + aus + (2 * aus if norm else 0)


class Architekturmesh3dainetz:
    #: Das gelaufene Netz („DGCNN-lite"): (Nr, Schicht, Typ, Kanäle ein, Kanäle aus = Neuronen, Gewichte, Werte je Probe, Aktivierung, was sie tut).
    HEUTE = (
        ('', 'Eingabe', 'Punktwolke', 6, 6, 0, PUNKTE * 6, '—',
         '4.096 von 16.384 Punkten der Außenfläche (je Schritt neu gezogen): Lage x, y − 0,85 m, z und Farbe r, g, b (flache Teilfarbe). Die Normalen liegen in `eingabe.npz`, werden aber NICHT benutzt.'),
        ('', 'Nachbargraph', 'k-nächste Nachbarn', 3, K, 0, PUNKTE * K, '—',
         'Je Punkt die 16 nächsten Punkte nach LAGE, einmal aus der Eingabe (statischer Graph — im Original-DGCNN wird er in jeder Schicht im Merkmalsraum neu gebaut).'),
        ('1', 'EdgeConv 1', 'Kantenfaltung', 2 * 6, 64, _faltung(12, 64), PUNKTE * 64, 'BatchNorm, LeakyReLU 0,2, Maximum über 16 Nachbarn',
         'Je Kante (Nachbar − Mitte, Mitte) → 64 Merkmale, dann das Maximum über die Nachbarn: örtliche Form um jeden Punkt.'),
        ('2', 'EdgeConv 2', 'Kantenfaltung', 2 * 64, 64, _faltung(128, 64), PUNKTE * 64, 'wie 1', 'Dieselbe Rechnung auf den Merkmalen von Schicht 1 (gleicher Graph).'),
        ('3', 'EdgeConv 3', 'Kantenfaltung', 2 * 64, 128, _faltung(128, 128), PUNKTE * 128, 'wie 1', 'Dieselbe Rechnung auf den Merkmalen von Schicht 2.'),
        ('4', 'Punktweise', '1×1-Faltung', 64 + 64 + 128, 512, _faltung(256, 512), PUNKTE * 512, 'BatchNorm, LeakyReLU 0,2',
         'Schichten 1–3 nebeneinander (256 Kanäle) → 512 Merkmale je Punkt.'),
        ('', 'Bündeln', 'Maximum + Mittel über alle Punkte', 512, 1024, 0, 1024, '—', 'Aus 4.096 × 512 wird EIN Vektor mit 1.024 Zahlen für die ganze Figur.'),
        ('5', 'Voll verbunden 1', 'linear', 1024, 512, _voll(1024, 512), 512, 'BatchNorm, LeakyReLU 0,2, Dropout 0,2', ''),
        ('6', 'Voll verbunden 2', 'linear', 512, 256, _voll(512, 256), 256, 'BatchNorm, LeakyReLU 0,2', ''),
        ('7', 'Ausgabe', 'linear', 256, 414, _voll(256, 414, norm=False), 414, 'keine',
         '414 = 138 Rig-Punkte × 3. Ergebnis = mittlere Trainingspose + 0,1 × Ausgabe (die Ausgabe ist die Abweichung in Dezimetern; die mittlere Pose ist fest, kein Gewicht).'),
    )

    @classmethod
    def _zeilen(cls, liste):
        return [{'nr': nr, 'name': name, 'typ': typ, 'ein': ein, 'aus': aus, 'gewichte': gewichte, 'werte': werte, 'aktivierung': aktiv, 'text': text}
                for nr, name, typ, ein, aus, gewichte, werte, aktiv, text in liste]

    #: Lauf mit `--ausgabe kanaele` (16.10.2026): die letzte Schicht gibt die freien Daz-Winkel und die Wurzel aus, dahinter die Vorwärtskinematik (keine Gewichte).
    KANAELE_TEXT = ('Je freiem Daz-Kanal eine Zahl z → Winkel = min + (max − min) · sigmoid(z), dazu die Wurzel (Drehung als 6D, Lage 3). Feste Kanäle (ohne Spielraum oder im Training unbewegt, '
                    'etwa das ganze Gesicht) stehen auf ihrem Wert. Abschnitt 5.')
    KINEMATIK = ('', 'Vorwärtskinematik', 'Skelett von Ursula1', 0, 138 * 3, 0, 138 * 3, '—',
                 'D_b = D_eltern · O·E·Oᵀ, p_b = p_eltern + D_eltern · (c_b − c_eltern): aus den Winkeln die 138 Gelenke (und ihre Enden für den Verlust). Knochenlängen = Ursula1, keine Gewichte.')

    #: Das Stimmen-Netz (16.10.2026 nachmittags, `mesh3dai_stimmen_netz.py`, `kopf = stimmen` im Lauf): dieselben Kantenfaltungen, aber KEIN einzelner Vektor für die ganze Figur als Ausgang —
    #: jeder Punkt sagt für jedes Ziel (138 Gelenke + 138 Enden) einen Versatz und ein Gewicht voraus; GroupNorm statt BatchNorm (gleich viele Gewichte), kein Dropout.
    STIMMEN = (
        ('', 'Eingabe', 'Punktwolke', 6, 6, 0, PUNKTE * 6, '—', '4.096 Punkte der Außenfläche: Lage x, y − 0,85 m, z und Farbe r, g, b.'),
        ('', 'Nachbargraph', 'k-nächste Nachbarn', 3, K, 0, PUNKTE * K, '—', 'Je Punkt die 16 nächsten Punkte nach Lage (einmal aus der Eingabe).'),
        ('1', 'EdgeConv 1', 'Kantenfaltung', 12, 64, _faltung(12, 64), PUNKTE * 64, 'GroupNorm, LeakyReLU 0,2, Maximum über 16 Nachbarn',
         'Je Kante (Nachbar − Mitte, Mitte) → 64 Merkmale, dann das Maximum über die Nachbarn: örtliche Form um jeden Punkt.'),
        ('2', 'EdgeConv 2', 'Kantenfaltung', 128, 64, _faltung(128, 64), PUNKTE * 64, 'wie 1', 'Dieselbe Rechnung auf den Merkmalen von Schicht 1.'),
        ('3', 'EdgeConv 3', 'Kantenfaltung', 128, 128, _faltung(128, 128), PUNKTE * 128, 'wie 1', 'Dieselbe Rechnung auf den Merkmalen von Schicht 2.'),
        ('4', 'Punktweise', '1×1-Faltung', 256, 512, _faltung(256, 512), PUNKTE * 512, 'GroupNorm, LeakyReLU 0,2', 'Schichten 1–3 nebeneinander → 512 Merkmale je Punkt.'),
        ('', 'Ganze Figur', 'Maximum + Mittel über alle Punkte', 512, 1024, 0, 1024, '—', 'Ein Vektor für die ganze Figur — er wird JEDEM Punkt wieder angehängt (wo in der Figur liege ich?).'),
        ('5', 'Kopf 1', '1×1-Faltung je Punkt', 256 + 1024, 512, _faltung(1280, 512), PUNKTE * 512, 'GroupNorm, LeakyReLU 0,2', 'Je Punkt: eigene Merkmale (Schichten 1–3) + ganze Figur.'),
        ('6', 'Kopf 2', '1×1-Faltung je Punkt', 512, 256, _faltung(512, 256), PUNKTE * 256, 'GroupNorm, LeakyReLU 0,2', ''),
        ('7', 'Stimmen', '1×1-Faltung je Punkt', 256, 4 * 276, _voll(256, 4 * 276, norm=False), PUNKTE * 4 * 276, 'keine',
         'Je Punkt und Ziel (138 Gelenke + 138 Enden): ein Versatz (3 Zahlen, in Dezimetern) und ein Gewicht (1 Zahl).'),
        ('', 'Abstimmung', 'Softmax über die Punkte', 4 * 276, 276 * 3, 0, 276 * 3, '—', 'Ziel = Σ softmax(Gewicht) · (Punkt + Versatz): gewichtetes Mittel der Stimmen. Keine Gewichte.'),
        ('', 'Anpassung (kein Netz)', 'Daz-Winkel an die Ziele', 276 * 3, 138 * 3, 0, 138 * 3, '—',
         'Nach dem Netz: Daz-Winkel in den Grenzen von Genesis 9 an die gestimmten Ziele angepasst (Adam, erst die Wurzel, dann alles) → 138 Gelenke + Drehung je Knochen.'),
    )

    @staticmethod
    def formkopf(regler):
        """Der Formkopf (16.10.2026 abends, `ProjektTemp/_wegwerf/mesh3dai_formnetz.py`, `Formnetz`): aus dem Merkmal der ganzen Figur 1.024 → 512 → 512 → Regler, LeakyReLU 0,2, keine Norm."""
        return (
            ('8', 'Form 1', 'linear, aus „Ganze Figur“', 1024, 512, _voll(1024, 512, norm=False), 512, 'LeakyReLU 0,2',
             'Zweiter Kopf: liest die Form aus den 1.024 Zahlen der ganzen Figur — einmal je Figur, nicht je Punkt.'),
            ('9', 'Form 2', 'linear', 512, 512, _voll(512, 512, norm=False), 512, 'LeakyReLU 0,2', ''),
            ('10', 'Formregler', 'linear', 512, regler, _voll(512, regler, norm=False), regler, 'keine',
             'Je Genesis-Form-Regler eine Zahl (Abschnitt 3). Verlust: Δ Regler × Wirkung → mittlere Verschiebung der Körperpunkte.'),
        )

    @classmethod
    def _heute_liste(cls, lauf_ergebnis):
        """Die Schichten des gelaufenen Netzes: bis zum 16.10.2026 morgens 414 freie Punktzahlen, seit dem Lauf `…_kanaele_e480` Daz-Winkel + Vorwärtskinematik (`ausgabe` in `lauf_ergebnis.json`),
        seit dem Nachmittag Stimmen je Punkt (`kopf = stimmen`), seit dem Abend dazu der Formkopf (`formkopf` = Zahl der Regler)."""
        e = lauf_ergebnis or {}
        if e.get('kopf') == 'stimmen' and e.get('formkopf'):
            return cls.STIMMEN + cls.formkopf(int(e['formkopf']))
        if e.get('kopf') == 'stimmen':
            return cls.STIMMEN
        if e.get('ausgabe') != 'kanaele' or not e.get('ausgabe_zahlen'):
            return cls.HEUTE
        n = int(e['ausgabe_zahlen'])
        letzte = ('7', 'Ausgabe', 'linear', 256, n, _voll(256, n, norm=False), n, 'keine (dann sigmoid in die Grenzen)', cls.KANAELE_TEXT)
        return cls.HEUTE[:-1] + (letzte, cls.KINEMATIK)

    @classmethod
    def heute(cls, lauf_ergebnis):
        """Tabelle, Summen und die Prüfung gegen den Lauf (`lauf_ergebnis`: dict aus `lauf_ergebnis.json` oder None)."""
        zeilen = cls._zeilen(cls._heute_liste(lauf_ergebnis))
        gewichte = sum(z['gewichte'] for z in zeilen)
        schichten = [z for z in zeilen if z['nr']]
        lauf = (lauf_ergebnis or {}).get('parameter')
        befund = None
        if lauf is None:
            befund = 'Kein Lauf mit `parameter` gefunden — die Summe ist nicht gegen ein gelaufenes Netz geprüft.'
        elif int(lauf) != gewichte:
            befund = 'Die Tabelle ergibt %d Gewichte, der Lauf meldet %d — die Tabelle beschreibt nicht das gelaufene Netz.' % (gewichte, int(lauf))
        kanaele = (lauf_ergebnis or {}).get('ausgabe') == 'kanaele'
        stimmen = (lauf_ergebnis or {}).get('kopf') == 'stimmen'
        form = int((lauf_ergebnis or {}).get('formkopf') or 0)
        if stimmen and form:
            text = 'Ausgabe: je Punkt Versatz + Gewicht für 276 Ziele → Abstimmung → Anpassung der Daz-Winkel → 138 Gelenke; dazu %d Formregler für die ganze Figur' % form
        elif stimmen:
            text = 'Ausgabe: je Punkt Versatz + Gewicht für 276 Ziele → Abstimmung → Anpassung der Daz-Winkel → 138 Gelenke'
        elif kanaele:
            text = 'Ausgabe: %s Zahlen (Daz-Winkel in ihren Grenzen + Wurzel) → Vorwärtskinematik → 138 Gelenke' % (lauf_ergebnis or {}).get('ausgabe_zahlen')
        else:
            text = 'Ausgabe: 138 Rig-Punkte × 3 in Metern, kein Regler'
        formnamen = {z[1] for z in cls.formkopf(1)}
        return {'zeilen': zeilen, 'gewichte': gewichte, 'lauf_gewichte': lauf, 'befund': befund, 'schichten': len(schichten),
                'neuronen': sum(z['aus'] for z in schichten), 'kanaele': kanaele, 'stimmen': stimmen, 'form': form, 'ausgabe_text': text,
                'neuronen_punkt': sum(z['aus'] for z in schichten if z['name'] not in formnamen),
                'neuronen_form': sum(z['aus'] for z in schichten if z['name'] in formnamen),
                'gewichte_form': sum(z['gewichte'] for z in zeilen if z['name'] in formnamen)}

    @staticmethod
    def lauf_lesen(ordner):
        """`lauf_ergebnis.json` des Laufordners oder None."""
        try:
            return json.loads((ordner / 'lauf_ergebnis.json').read_text(encoding='utf-8'))
        except (OSError, ValueError, TypeError, AttributeError):
            return None
