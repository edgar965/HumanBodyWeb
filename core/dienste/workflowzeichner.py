# -*- coding: utf-8 -*-
"""Workflowzeichner — macht aus einem `Workflowbaum` HTML: waagerechter Entscheidungsbaum aus Kästen, Kanten und Zeit-Marken
(Hilfe → Architektur → 2D3D, 02.10.2026).

Kein SVG und keine Bibliothek: Kästen sind `div`s mit festem Breitenanteil, Kanten entstehen im Stilblatt aus Rändern
(`hilfe_architektur_2d3d_workflow.css`). Der Text bricht dadurch von selbst um — bei SVG hätte jede Zeilenlänge geschätzt werden
müssen. Alles Gezeigte wird maskiert; die Klassennamen werden zu Verweisen auf die Klassenkarten (`#k-<Name>`), wenn es die Karte
gibt (`bekannt`), sonst bleiben sie schlichter Text. Die Zeit-Marke trägt die Nummer ihrer Quelle (`Workflowquellen`).
"""

from django.utils.html import escape
from django.utils.safestring import mark_safe

from .workflowknoten import Workflowknoten

__all__ = ['Workflowzeichner']


class Workflowzeichner:
    ICONS = {
        Workflowknoten.FRAGE: 'bi-signpost-split',
        Workflowknoten.TAT: 'bi-gear',
        Workflowknoten.ENDE: 'bi-flag',
        Workflowknoten.OFFEN: 'bi-dash-circle',
    }

    def __init__(self, quellen, bekannt):
        """`quellen`: `Workflowquellen`, `bekannt`: Namen der Klassen, zu denen es eine Karte gibt."""
        self.quellen = quellen
        self.bekannt = set(bekannt)

    # ------------------------------------------------------------------ kleine Teile

    def klasse(self, name):
        """Der Klassenname als Verweis auf seine Karte (oder schlichter Text, wenn es keine gibt) — als HTML markiert."""
        if name in self.bekannt:
            return mark_safe('<a class="wf-klasse" href="#k-%s">%s</a>' % (escape(name), escape(name)))
        return mark_safe('<span class="wf-klasse wf-klasse-lose">%s</span>' % escape(name))

    def zeit(self, zeit):
        """Die Zeit-Marke: Stufenfarbe, Text und die Nummer der Quelle — als HTML markiert."""
        nummer = self.quellen.nummer(zeit.quelle) if zeit.quelle else 0
        quelle = '<a class="wf-qnr" href="#quelle-%d">%d</a>' % (nummer, nummer) if nummer else ''
        return mark_safe(
            '<span class="wf-zeit %s"><i class="bi bi-stopwatch"></i> %s%s</span>'
            % (zeit.klasse, escape(zeit.text), quelle)
        )

    def hinweis(self, zeit):
        return '<div class="wf-hinweis">%s</div>' % escape(zeit.hinweis) if zeit.hinweis else ''

    @staticmethod
    def balken(wert, groesste):
        """Ein Balken, dessen Füllung `wert` gegen `groesste` ist (Prozent der Breite)."""
        prozent = 100.0 * wert / groesste if groesste > 0 else 0.0
        return (
            '<span class="wf-balken"><span class="wf-fuellung" style="width:%.1f%%"></span></span>' % prozent
        )

    def teile(self, teile):
        groesste = max([z.wert for _n, z in teile] + [0.0])
        zeilen = []
        for name, zeit in teile:
            zeilen.append(
                '<div class="wf-teil"><span class="wf-teilname">%s</span>%s%s</div>%s'
                % (escape(name), self.balken(zeit.wert, groesste), self.zeit(zeit), self.hinweis(zeit))
            )
        return '<div class="wf-teile">%s</div>' % ''.join(zeilen)

    # ------------------------------------------------------------------ Kasten und Zweig

    def knoten(self, k):
        klassen = (' wf-vorgabe' if k.vorgabe else '') + (' wf-ausnahme' if k.ausnahme else '')
        marke = (
            '<span class="wf-marke-vorgabe">Vorgabe</span>' if k.vorgabe else
            '<span class="wf-marke-ausnahme">Ausnahme</span>' if k.ausnahme else ''
        )
        kopf = '<div class="wf-kopf"><i class="bi %s"></i><span class="wf-titel">%s</span>%s</div>' % (
            self.ICONS[k.art],
            escape(k.titel),
            marke,
        )
        text = '<div class="wf-text">%s</div>' % escape(k.text) if k.text else ''
        teile = self.teile(k.teile) if k.teile else ''
        fuss = ''.join(self.klasse(c) for c in k.klassen)
        zeit = self.zeit(k.zeit) + self.hinweis(k.zeit) if k.zeit is not None else ''
        fuss = '<div class="wf-fuss">%s</div>' % fuss if fuss else ''
        return '<div class="wf-knoten wf-%s%s">%s%s%s%s%s</div>' % (
            k.art,
            klassen,
            kopf,
            text,
            teile,
            fuss,
            zeit,
        )

    def zweig(self, k):
        """Der Knoten und rechts daneben seine Kinder, jedes mit der Kante, die zu ihm führt."""
        aus = '<div class="wf-zweig">%s' % self.knoten(k)
        if k.kinder:
            aeste = []
            for kind in k.kinder:
                kante = (
                    '<span class="wf-kante">%s</span>' % escape(kind.kante)
                    if kind.kante
                    else '<span class="wf-kante wf-kante-leer"></span>'
                )
                aeste.append(
                    '<div class="wf-ast"><span class="wf-linie"></span>%s<span class="wf-linie"></span>%s</div>'
                    % (kante, self.zweig(kind))
                )
            aus += '<div class="wf-kinder">%s</div>' % ''.join(aeste)
        return aus + '</div>'

    def baum(self, baum):
        """Der ganze Kartenblock eines Baums: Überschrift, Frage, Baum und die Fundstelle im Code."""
        return mark_safe(
            '<section class="wf-baumkarte" id="%s"><h3>%s</h3><p class="wf-frage">%s</p>'
            '<div class="wf-baumrahmen"><div class="wf-baum">%s</div></div><p class="wf-codestelle">Code und Quellen: %s</p></section>'
            % (
                escape(baum.anker),
                escape(baum.titel),
                escape(baum.frage),
                self.zweig(baum.wurzel),
                escape(baum.quelle),
            )
        )
