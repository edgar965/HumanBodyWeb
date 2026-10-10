# -*- coding: utf-8 -*-
"""Blendimportkoerperpruefung — deckt der Körper der .blend die ganze Figur? (Wächter nach „export", 10.10.2026)

Edgar (10.10.2026), nach Rosemary Winters: „mach: ein Wächter nach dem Export (5 s), der einen Körper meldet, der nur einen Teil der Figurhöhe
deckt." Der Import von Rosemary rechnete Stunden (Mesh to 3D 20 Min., Stücke 11 Min., Abstandsschritt 22,5 Min., Backen) und lieferte eine Figur,
die nicht zum Körper passte (Abstand median 81 mm), weil das Körper-Netz `body` nur von Kopf bis Mitte Oberschenkel reichte (z 1,353…2,941 m); die
Beine gab es nur als Strumpf-Netz `sock` (z −0,225…1,506). „Mesh to 3D" passt eine GANZE Genesis-Figur an; einem Torso gibt es keine passende.

Figurhöhe = Spanne über alle Netze der Rollen Körper, Kleid und Auge (das Haar zählt nicht: ein Dutt oder eine Mähne verlängert die Figur nicht).
Anteil = Höhe des Körper-Netzes ÷ Figurhöhe. **Gemessen an allen gespeicherten Inventaren** (`ProjektTemp/_wegwerf/asian/koerper_anteil.py`): cute girl 100 %,
Asian Female 99 %, Fallout ranger 93 % (Körper ohne Füße, Helm und Waffe zählen mit), Asian (Character Creator) 99 % — Rosemary 48 %. Die Schwelle liegt
bei 70 %: weit genug von 93 % für Hut, Stiefel und Waffe, weit genug von 48 %, dass ein abgeschnittener Körper nie durchrutscht.

Wer absichtlich einen Teilkörper importieren will (eine Büste), stellt „Unvollständiger Körper" auf „Trotzdem importieren" (`unvollstaendig`).
"""

__all__ = ['Blendimportkoerperpruefung']


class Blendimportkoerperpruefung:
    #: Kleinster Anteil, den der Körper an der Figurhöhe haben darf.
    MIN_ANTEIL = 0.70
    #: Netze mit diesen Rollen bilden die Figur (Haar, Mund, Augenzubehör nicht).
    FIGUR = ('koerper', 'kleid', 'auge')

    @classmethod
    def messen(cls, inventar, rollen):
        """`{koerper, koerper_z, figur_z, deckung_z, hoehe_koerper_m, hoehe_figur_m, anteil, tiefstes, hoechstes}` — Höhen in Metern des Inventars
        (Blender-Z). `anteil` = Länge der Deckung (Körper ∪ Kleidung, die unter den Körper reicht) ÷ Figurhöhe."""
        netze = {n['name']: n for n in (inventar or {}).get('netze') or []}
        koerper = next((netze[r['name']] for r in rollen if r['rolle'] == 'koerper' and r['name'] in netze), None)
        figur = [netze[r['name']] for r in rollen if r['rolle'] in cls.FIGUR and r['name'] in netze]
        if koerper is None or not figur:
            return None
        tiefstes = min(figur, key=lambda n: float(n['min'][2]))
        hoechstes = max(figur, key=lambda n: float(n['max'][2]))
        unten, oben = float(tiefstes['min'][2]), float(hoechstes['max'][2])
        h_koerper = float(koerper['max'][2]) - float(koerper['min'][2])
        h_figur = oben - unten
        # Strümpfe, Hosen, Röcke über den Beinen: der Körper endet darin, die Kleidung deckt die Beine (Rosemary Winters, 10.10.2026: „die Dame ist
        # völlig korrekt" — der Strumpf-Netz `sock` reicht bis zum Absatz, die Haut darunter ist nicht da, und das Bild zeigt eine ganze Figur).
        kleider = [netze[r['name']] for r in rollen if r['rolle'] == 'kleid' and r['name'] in netze]
        spannen = [(float(koerper['min'][2]), float(koerper['max'][2]))] + [(float(k['min'][2]), float(k['max'][2])) for k in kleider]
        deckung = cls._vereinigt(spannen)
        deckung_z = (min(a for a, _ in spannen), max(b for _, b in spannen))
        return {'koerper': koerper['name'], 'koerper_z': [round(float(koerper['min'][2]), 3), round(float(koerper['max'][2]), 3)],
                'figur_z': [round(unten, 3), round(oben, 3)], 'deckung_z': [round(deckung_z[0], 3), round(deckung_z[1], 3)],
                'hoehe_koerper_m': round(h_koerper, 3), 'hoehe_figur_m': round(h_figur, 3),
                'anteil': round(deckung / h_figur, 3) if h_figur > 0 else 1.0, 'tiefstes': tiefstes['name'], 'hoechstes': hoechstes['name']}

    @staticmethod
    def _vereinigt(spannen):
        """Länge der Vereinigung von `(unten, oben)`-Spannen: überlappende Stücke zählen einmal."""
        gesamt, lauf = 0.0, None
        for a, b in sorted(spannen):
            if lauf is None or a > lauf[1]:
                if lauf is not None:
                    gesamt += lauf[1] - lauf[0]
                lauf = [a, b]
            else:
                lauf[1] = max(lauf[1], b)
        if lauf is not None:
            gesamt += lauf[1] - lauf[0]
        return gesamt

    @classmethod
    def pruefen(cls, inventar, rollen, trotzdem=False):
        """Das Messergebnis für den Bericht; `ValueError` mit dem Grund, wenn der Körper zu wenig der Figur deckt und `trotzdem` fehlt."""
        mass = cls.messen(inventar, rollen)
        if mass is None or mass['anteil'] >= cls.MIN_ANTEIL:
            return mass
        mass['unvollstaendig'] = True
        if trotzdem:
            mass['trotzdem'] = True
            return mass
        raise ValueError(cls.text(mass))

    @classmethod
    def text(cls, mass):
        """Der Befund in Klartext: wie viel, wo es fehlt, welches Netz darüber hinausreicht, und wie man es übergeht."""
        k_unten, k_oben = mass['deckung_z']
        f_unten, f_oben = mass['figur_z']
        fehlt = []
        if k_unten - f_unten > 0.1 * mass['hoehe_figur_m']:
            fehlt.append('unten %.2f m (bis „%s", z %.2f m)' % (k_unten - f_unten, mass['tiefstes'], f_unten))
        if f_oben - k_oben > 0.1 * mass['hoehe_figur_m']:
            fehlt.append('oben %.2f m (bis „%s", z %.2f m)' % (f_oben - k_oben, mass['hoechstes'], f_oben))
        return ('Der Körper „%s" ist unvollständig: Körper und Kleidung reichen von z %.2f bis %.2f m und decken nur %d %% der Figurhöhe (%.2f m)%s. '
                '„Mesh to 3D" passt eine ganze Figur an; an diesem Körper würde sie nicht passen, und der Import rechnete Stunden. '
                'Der fehlende Teil des Körpers liegt nicht in der .blend. Soll sie trotzdem importiert werden: neuen Import starten mit der '
                'Einstellung „Unvollständiger Körper" auf „Trotzdem importieren".'
                % (mass['koerper'], k_unten, k_oben, round(mass['anteil'] * 100), mass['hoehe_figur_m'],
                   '; es fehlt ' + ', '.join(fehlt) if fehlt else ''))
