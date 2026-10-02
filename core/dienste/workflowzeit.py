# -*- coding: utf-8 -*-
"""Workflowzeit — eine gemessene Dauer im Workflow-Reiter der Seite Hilfe → Architektur → 2D3D (02.10.2026).

Edgar: „ich brauche grafische Klassen mit Entscheidungsbäumen und Infos, was jeder Schritt kostet an Zeit". Jede Zahl
der Seite ist eine `Workflowzeit`: von/bis in Sekunden (ein Wert oder eine Spanne über mehrere Aufträge oder Runden) und
die Quelle, aus der sie stammt. Ohne Wert (`von=None`) steht dort „nicht gemessen" — keine geschätzte Zahl, die wie eine
Messung aussähe. Die Stufe (`klasse`) färbt die Marke: unter 1 s, 1–10 s, 10–60 s, 1–5 min, über 5 min.
"""

__all__ = ['Workflowzeit']


class Workflowzeit:
    #: (obere Grenze in s, CSS-Klasse) — gefärbt wird nach dem GRÖSSTEN Wert der Spanne.
    STUFEN = ((1.0, 'z0'), (10.0, 'z1'), (60.0, 'z2'), (300.0, 'z3'))
    GROESSTE, UNBEKANNT = 'z4', 'zx'
    #: Ab so vielen Sekunden steht die Dauer auch in Minuten daneben.
    MINUTEN_AB = 120.0

    def __init__(self, von=None, bis=None, quelle='', hinweis='', unter=False):
        """`von`/`bis`: Sekunden (`bis` leer = ein einzelner Wert), `quelle`: woher die Messung stammt, `hinweis`: was
        sonst dazugehört (Bedingung, Einschränkung), `unter`: die Quelle sagt nur „weniger als `von`"."""
        self.von = None if von is None else float(von)
        self.bis = self.von if bis is None else float(bis)
        self.quelle = quelle
        self.hinweis = hinweis
        self.unter = bool(unter)

    @property
    def gemessen(self):
        return self.von is not None

    @property
    def klasse(self):
        if not self.gemessen:
            return self.UNBEKANNT
        for grenze, name in self.STUFEN:
            if self.bis < grenze:
                return name
        return self.GROESSTE

    @property
    def wert(self):
        """Der Wert für Balken und Summen: das Ende der Spanne (0 ohne Messung)."""
        return self.bis if self.gemessen else 0.0

    @staticmethod
    def zahl(sekunden):
        """`563.1` → „563", `5.2` → „5,2", `0.04` → „0,04" — deutsches Komma, so viele Stellen wie nötig."""
        s = float(sekunden)
        if s >= 100:
            return '%d' % round(s)
        text = ('%.2f' % s) if 0 < s < 0.1 else ('%.1f' % s)
        return text.replace('.', ',')

    @property
    def text(self):
        if not self.gemessen:
            return 'nicht gemessen'
        kern = (
            self.zahl(self.von)
            if self.von == self.bis
            else '%s–%s' % (self.zahl(self.von), self.zahl(self.bis))
        )
        text = ('< ' if self.unter else '') + kern + ' s'
        if self.bis >= self.MINUTEN_AB:
            minuten = ('%.1f' % (self.bis / 60.0)).replace('.', ',')
            text += ' (%s min)' % minuten if self.von == self.bis else ' (bis %s min)' % minuten
        return text
