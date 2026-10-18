# -*- coding: utf-8 -*-
"""Architekturmesh3daibild — eine einfache Grafik der KI von Mesh3D-AI für Hilfe → Architektur → Mesh3DAI (16.10.2026).

Edgar: „mach auch eine einfache Grafik zu der KI in der Form wie im Bild“ (Bild: Kästen „Input Layer“ rot, „Hidden Layer“ blau, „Output Layer“ grün, Kreise als Neuronen, Pfeile von jedem Kreis
einer Schicht zu jedem der nächsten). Abends (Edgar: „schreibe in jeder Schicht die Anzahl der Knoten (Neuronen) klar … oder habe ich nur 4 Neuronen?? oder 4 je Punkt, also 4*4096??“ →
„passe die Grafik an, vereinfacht, z. B. je Punkt“): die Grafik zeigt EINEN Punkt auf dem Weg durch das Netz — je Schicht eine Spalte mit der Zahl der Neuronen groß (= Zahlen, die ein Punkt
nach der Schicht trägt), darunter nur noch Gewichte und ein Stichwort; die Eingabe mit ihren sechs echten Kreisen (x, y, z, r, g, b), sonst drei Kreise, „⋮“, ein Kreis.
Seit dem späten Abend (Formkopf, `Architekturmesh3dainetz.formkopf`): unter den Kopf-Spalten eine zweite Reihe — aus „Ganze Figur“ die Formregler, einmal je Figur; ohne Formlauf entfällt sie.
Die Zahlen kommen aus `Architekturmesh3dainetz.STIMMEN`/`formkopf` (dieselbe Tabelle, die die Seite zeigt und gegen den Lauf prüft), Regler und Speicher aus `Architekturmesh3daigroesse` (gemessen).
Rechts steht, was NACH dem Netz geschieht (ohne Gewichte), grau.
"""

from django.utils.html import escape
from django.utils.safestring import mark_safe

from .architekturmesh3daibildkasten import Architekturmesh3daibildkasten
from .architekturmesh3dainetz import Architekturmesh3dainetz

__all__ = ['Architekturmesh3daibild']


def _de(n, stellen=0):
    text = '{:,.{s}f}'.format(float(n), s=stellen)
    return text.replace(',', ' ').replace('.', ',').replace(' ', '.')


class Architekturmesh3daibild:
    #: (Art, Titel, Zeile der Tabelle `STIMMEN`). Eine Spalte je Schicht, so wie EIN Punkt sie durchläuft.
    SPALTEN = (
        ('eingabe', 'Eingabe', 'Eingabe'),
        ('versteckt', 'Schicht 1', 'EdgeConv 1'),
        ('versteckt', 'Schicht 2', 'EdgeConv 2'),
        ('versteckt', 'Schicht 3', 'EdgeConv 3'),
        ('versteckt', 'Schicht 4', 'Punktweise'),
        ('figur', 'Ganze Figur', 'Ganze Figur'),
        ('versteckt', 'Schicht 5', 'Kopf 1'),
        ('versteckt', 'Schicht 6', 'Kopf 2'),
        ('ausgabe', 'Ausgabe', 'Stimmen'),
    )
    #: Die zweite Reihe unter den Spalten 6–8: (Spalte, Titel, Zeile von `formkopf`).
    #: Edgar, 17.10.2026 abends: „Was ist form1 und Form2 nacheinander??“ — die zwei verdeckten Schichten des Formkopfs (`Formnetz.form`: Linear 1024→512, LeakyReLU, 512→512, LeakyReLU, 512→Regler).
    FORMREIHE = ((6, 'Formschicht 1', 'Form 1'), (7, 'Formschicht 2', 'Form 2'), (8, 'Formregler', 'Formregler'))
    EINGABE_KREISE = ('x', 'y', 'z', 'r', 'g', 'b')
    FARBEN = {'eingabe': ('#f8cecc', '#b85450'), 'versteckt': ('#dae8fc', '#6c8ebf'), 'figur': ('#eef1f6', '#8a99b3'), 'ausgabe': ('#d5e8d4', '#82b366'), 'danach': ('#eeeeee', '#999999'),
              'form': ('#fff2cc', '#d6b656')}
    ZAHLFARBE = '#1f3f7a'
    BREITE = 1800
    SPALTE, ABSTAND, RADIUS = 140, 34, 17
    KASTEN_OBEN, KASTEN_UNTEN = 58, 560
    KREISE_OBEN, KREISE_HOEHE = 88, 222
    TEXT_OBEN = 340                    # Titel; darunter die Zahl groß, das Wort, dann die Stichworte im Abstand ZEILE
    ZEILE = 17
    FORM_OBEN, FORM_UNTEN = 600, 770   # zweite Reihe (Formkopf)

    @staticmethod
    def _tabelle(form=None):
        zeilen = Architekturmesh3dainetz.STIMMEN + (Architekturmesh3dainetz.formkopf(form) if form else ())
        return {z[1]: z for z in zeilen}

    @classmethod
    def punkte(cls):
        return cls._tabelle()['Eingabe'][6] // 6

    @classmethod
    def _x(cls, i):
        return 20 + i * (cls.SPALTE + cls.ABSTAND)

    @classmethod
    def _wort(cls, art):
        return {'eingabe': 'Zahlen je Punkt', 'figur': 'Zahlen, alle Punkte gleich', 'form': 'Neuronen je Figur'}.get(art, 'Neuronen je Punkt')

    @classmethod
    def _stichworte(cls, titel, zeile, regler):
        """[(Text, fett)] unter der Zahl — kurz, je Spalte höchstens acht Zeilen."""
        nachbarn = cls._tabelle()['Nachbargraph'][4]
        gewichte = ('Gewichte %s' % _de(zeile[5]), True)
        if titel == 'Eingabe':
            return [('Lage + Farbe', False), ('%d Nachbarn je Punkt' % nachbarn, False), ('keine Gewichte', False)]
        if titel in ('Schicht 1', 'Schicht 2', 'Schicht 3'):
            return [('mit %d Nachbarn' % nachbarn, False), gewichte]
        if titel == 'Schicht 4':
            return [('aus Schicht 1–3', False), gewichte]
        if titel == 'Ganze Figur':
            return [('Max + Mittel', False), ('über alle Punkte', False), ('keine Gewichte', False)]
        if titel == 'Schicht 5':
            return [('+ ganze Figur', False), gewichte]
        if titel == 'Schicht 6':
            return [gewichte]
        aus = [('= %d Ziele × 4' % (zeile[4] // 4), False), ('(Versatz x, y, z', False), ('+ Gewicht)', False), gewichte]
        # Edgar, 16.10.2026: „bei der Ausgabe schreibe die gesamte Anzahl der Parameter für die Genesis- und Kleider-Regler“ — gezählt, `Architekturmesh3daigroesse`.
        if regler:
            aus += [('noch nicht:', True), ('Kleider %s Regler' % _de(regler['kleider_regler']), False), ('Mimik', False)]
        return aus

    @classmethod
    def kopfzeilen(cls, form=None):
        n = _de(cls.punkte())
        zweite = 'Jede Schicht rechnet so für jeden der %s Punkte, mit denselben Gewichten. Kreise = Sinnbild, ⋮ = weitere.' % n
        if form:
            zweite += ' Gelb unten: der Formkopf — einmal je Figur, aus der ganzen Figur.'
        return 'Ein Punkt auf dem Weg durch das Netz — die große Zahl: so viele Zahlen (Neuronen) trägt der Punkt nach der Schicht.', zweite

    @classmethod
    def _fuss(cls, groesse, form=None):
        """Zwei Zeilen: Gewichte (mit Formkopf) → Datei → Grafikspeicher nach dem Laden, dann der Speicher beim Rechnen (gemessen am Netz OHNE Formkopf)."""
        stimmen = sum(int(z[5]) for z in Architekturmesh3dainetz.STIMMEN)
        formkopf = sum(int(z[5]) for z in Architekturmesh3dainetz.formkopf(form)) if form else 0
        erste = ['Summe %s Gewichte (lernbare Zahlen)' % _de(stimmen + formkopf)]
        if form:
            erste.append('davon Formkopf %s' % _de(formkopf))
        zweite = []
        if groesse:
            n = groesse['netz']
            v, t = groesse.get('vorhersage_4096'), groesse.get('training_4096')
            zweite.append('Gemessen am Netz ohne Formkopf (%s Gewichte): Datei netz.pt %s MB, GPU nach dem Laden %s MB reserviert' % (_de(n['parameter']), _de(n['datei_mb'], 1), _de(n['reserviert_geladen_mb'])))
            if v:
                zweite.append('eine Vorhersage %s MB, %s ms' % (_de(v['spitze_mb']), _de(v['ms'])))
            if t:
                zweite.append('ein Trainingsschritt (Batch %d) %s GB' % (t['batch'], _de(t['spitze_mb'] / 1000, 1)))
            zweite.append('%s, %s' % (n['gemessen'][:10], n['gpu'].replace('NVIDIA ', '')))
        return ' · '.join(erste), ' · '.join(zweite)

    @classmethod
    def _kreise(cls, art, cx):
        """[(cx, cy, Beschriftung)] und die y des „⋮“ (oder None)."""
        if art == 'eingabe':
            n = len(cls.EINGABE_KREISE)
            return [(cx, cls.KREISE_OBEN + cls.KREISE_HOEHE * (k + 0.5) / n, cls.EINGABE_KREISE[k]) for k in range(n)], None
        ys = [cls.KREISE_OBEN + cls.KREISE_HOEHE * (k + 0.5) / 5 for k in range(5)]
        return [(cx, ys[k], '') for k in (0, 1, 2, 4)], ys[3]

    @classmethod
    def _spalte(cls, teile, x, oben, unten, art, titel, zahl, stichworte, titel_y):
        """Kasten mit Titel, großer Zahl, Wort und Stichworten."""
        cx = x + cls.SPALTE / 2
        fuell, rand = cls.FARBEN[art]
        teile.append('<rect x="%d" y="%d" width="%d" height="%d" fill="%s" stroke="%s" stroke-dasharray="5 3"/>' % (x, oben, cls.SPALTE, unten - oben, fuell, rand))
        teile.append('<text x="%.0f" y="%d" text-anchor="middle" font-size="16" font-weight="600" fill="#222">%s</text>' % (cx, titel_y, escape(titel)))
        teile.append('<text x="%.0f" y="%d" text-anchor="middle" font-size="28" font-weight="700" fill="%s">%s</text>' % (cx, titel_y + 32, cls.ZAHLFARBE, _de(zahl)))
        teile.append('<text x="%.0f" y="%d" text-anchor="middle" font-size="13" font-weight="600" fill="%s">%s</text>' % (cx, titel_y + 51, cls.ZAHLFARBE, escape(cls._wort(art))))
        for k, (text, fett) in enumerate(stichworte):
            teile.append('<text x="%.0f" y="%d" text-anchor="middle" font-size="13"%s fill="#333">%s</text>' % (cx, titel_y + 74 + cls.ZEILE * k, ' font-weight="600"' if fett else '', escape(text)))

    @classmethod
    def _grau(cls, teile, x0, y_mitte, zeilen):
        breite = cls.BREITE - x0 - 20
        hoehe = 22 + 19 * len(zeilen)
        fuell, rand = cls.FARBEN['danach']
        teile.append('<rect x="%.0f" y="%.0f" width="%.0f" height="%d" rx="6" fill="%s" stroke="%s"/>' % (x0, y_mitte - hoehe / 2, breite, hoehe, fuell, rand))
        for j, (text, fett) in enumerate(zeilen):
            if text:
                teile.append('<text x="%.0f" y="%.0f" text-anchor="middle" font-size="%d"%s fill="#222">%s</text>'
                             % (x0 + breite / 2, y_mitte - hoehe / 2 + 26 + 19 * j, 15 if fett else 13, ' font-weight="600"' if fett else '', escape(text)))

    @classmethod
    def _pfeil(cls, teile, x1, y1, x2, y2, breite=1.5):
        teile.append('<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" stroke="#222" stroke-width="%.1f" marker-end="url(#m3a-pfeil)"/>' % (x1, y1, x2, y2, breite))

    @classmethod
    def svg(cls, regler=None, groesse=None, form=None, vorstufe=None, kette=None):
        """`form` = Zahl der Formregler des Bezugslaufs (None: Netz ohne Formkopf, keine zweite Reihe); `vorstufe` = `Architekturmesh3daivorstufe.kontext`, `kette` = `Architekturmesh3daikette.kontext`
        (beide None: kein Kasten unten links)."""
        t = cls._tabelle(form)
        hoehe = (Architekturmesh3daibildkasten.UNTEN if kette else cls.FORM_UNTEN) + 90 if form or vorstufe or kette else cls.KASTEN_UNTEN + 64
        teile = ['<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 %d %d" role="img" aria-label="Ein Punkt auf dem Weg durch die KI von Mesh3D-AI" class="m3a-bild">' % (cls.BREITE, hoehe),
                 '<defs><marker id="m3a-pfeil" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse"><path d="M0,0 L10,5 L0,10 z" fill="#222"/></marker></defs>',
                 '<rect x="0" y="0" width="%d" height="%d" rx="10" fill="#ffffff"/>' % (cls.BREITE, hoehe)]
        for k, text in enumerate(cls.kopfzeilen(form)):
            teile.append('<text x="20" y="%d" font-size="15"%s fill="#222">%s</text>' % (26 + 20 * k, ' font-weight="600"' if k == 0 else '', escape(text)))
        spalten = []
        for i, (art, titel, name) in enumerate(cls.SPALTEN):
            zeile = t[name]
            x = cls._x(i)
            cls._spalte(teile, x, cls.KASTEN_OBEN, cls.KASTEN_UNTEN, art, titel, zeile[4], cls._stichworte(titel, zeile, regler), cls.TEXT_OBEN)
            kreise, punkte_y = cls._kreise(art, x + cls.SPALTE / 2)
            spalten.append(kreise)
            if punkte_y is not None:
                teile.append('<text x="%.0f" y="%.0f" text-anchor="middle" font-size="26" font-weight="700" fill="#222">⋮</text>' % (x + cls.SPALTE / 2, punkte_y + 9))
        # Pfeile von jedem Kreis zu jedem der nächsten Spalte, darüber die Kreise.
        for a, b in zip(spalten, spalten[1:], strict=False):
            for xa, ya, _ in a:
                for xb, yb, _ in b:
                    teile.append('<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" stroke="#555" stroke-width="0.8" marker-end="url(#m3a-pfeil)"/>'
                                 % (xa + cls.RADIUS, ya, xb - cls.RADIUS - 2, yb))
        for spalte in spalten:
            for cx, cy, wort in spalte:
                teile.append('<circle cx="%.1f" cy="%.1f" r="%d" fill="#ffffff" stroke="#222" stroke-width="1.5"/>' % (cx, cy, cls.RADIUS))
                if wort:
                    teile.append('<text x="%.1f" y="%.1f" text-anchor="middle" font-size="14" fill="#222">%s</text>' % (cx, cy + 5, wort))
        # Nach dem Netz: Abstimmung und Anpassung (grau, ohne Gewichte).
        x0 = cls._x(len(cls.SPALTEN)) - cls.ABSTAND + 30
        y_mitte = cls.KREISE_OBEN + cls.KREISE_HOEHE / 2
        ab, an = t['Abstimmung'], t['Anpassung (kein Netz)']
        cls._grau(teile, x0, y_mitte, (('Nach dem Netz', True), ('ohne Gewichte', False), ('', False), ('Abstimmung über', False), ('alle Punkte → %d Ziele' % (ab[4] // 3), False), ('', False),
                                      ('Daz-Winkel anpassen', False), ('→ %d Gelenke' % (an[4] // 3), False)))
        cls._pfeil(teile, spalten[-1][0][0] + cls.RADIUS, y_mitte, x0 - 2, y_mitte)
        if form:
            cls._formreihe(teile, t, x0)
        if kette:
            Architekturmesh3daibildkasten.kette(cls, teile, kette)
        elif vorstufe:
            Architekturmesh3daibildkasten.rig(cls, teile, vorstufe)
        erste, zweite = cls._fuss(groesse, form)
        teile.append('<text x="20" y="%d" font-size="14" fill="#222">%s</text>' % (hoehe - 38, escape(erste)))
        if zweite:
            teile.append('<text x="20" y="%d" font-size="14" fill="#222">%s</text>' % (hoehe - 14, escape(zweite)))
        teile.append('</svg>')
        return mark_safe(''.join(teile))

    @classmethod
    def _formreihe(cls, teile, t, x0):
        """Zweite Reihe: aus „Ganze Figur“ (Spalte 5) nach unten und in den Formkopf, rechts was im Test daraus wird."""
        y = (cls.FORM_OBEN + cls.FORM_UNTEN) / 2
        stichworte = {'Formschicht 1': [('verdeckt, liest die 1.024', False), ('Zahlen der ganzen Figur', False)],
                      'Formschicht 2': [('verdeckt, rechnet weiter', False), ('(ohne sie: nur lineare', False), ('Summen möglich)', False)],
                      'Formregler': [('je Genesis-Form-Regler', False), ('eine Zahl', False)]}
        for spalte, titel, name in cls.FORMREIHE:
            zeile = t[name]
            cls._spalte(teile, cls._x(spalte), cls.FORM_OBEN, cls.FORM_UNTEN, 'form', titel, zeile[4],
                        stichworte[titel] + [('Gewichte %s' % _de(zeile[5]), True)], cls.FORM_OBEN + 26)
        cx5 = cls._x(5) + cls.SPALTE / 2
        teile.append('<polyline points="%.0f,%d %.0f,%.0f %.0f,%.0f" fill="none" stroke="#222" stroke-width="1.5" marker-end="url(#m3a-pfeil)"/>'
                     % (cx5, cls.KASTEN_UNTEN, cx5, y, cls._x(6) - 2, y))
        for a, b in ((6, 7), (7, 8)):
            cls._pfeil(teile, cls._x(a) + cls.SPALTE, y, cls._x(b) - 2, y)
        cls._grau(teile, x0, y, (('Im Test (ohne Gewichte)', True), ('Figur aus den Reglern', False), ('bauen (Genesis-Formung)', False), ('→ Skelett der Figur', False),
                                 ('→ Daz-Winkel an IHR', False), ('Skelett anpassen', False)))
        cls._pfeil(teile, cls._x(8) + cls.SPALTE, y, x0 - 2, y)
        for j, text in enumerate(('Formkopf = ein zweites kleines Netz am selben Rückgrat, einmal je Figur.',
                                  'Formschicht 1 und 2 sind seine verdeckten Schichten, nacheinander gerechnet;',
                                  'die letzte gibt je Genesis-Form-Regler eine Zahl aus.')):
            teile.append('<text x="%d" y="%d" font-size="13" fill="#555">%s</text>' % (cls._x(6), cls.FORM_UNTEN + 20 + 17 * j, escape(text)))
