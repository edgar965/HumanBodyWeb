# -*- coding: utf-8 -*-
u"""Was ein Datei- oder Pfadname unter Windows NICHT sein darf.

WARUM EIGENE DATEI (30.08.2026): In ``safe_paths.py`` prüften ``pruefe`` und
``dateiname`` dieselben drei Dinge — verbotene Zeichen, Gerätenamen, Punkt oder
Leerzeichen am Ende — jede mit ihrem eigenen ``if`` und ihrer eigenen Meldung.
Beide lagen dadurch bei Rang C der zyklomatischen Komplexität (14 und 11
Verzweigungen), und die Regeln waren schon einmal auseinandergelaufen: Die
Zeichenprüfung fehlte in ``dateiname``, bis ``video:1.mp4`` durchkam.

WARUM DAS KEINE KOSMETIK IST: Jede Regel beschreibt eine Stelle, an der Windows
etwas ANDERES tut, als der Name verspricht — und zwar ohne Fehlermeldung:

    Gerätename         ``COM1.txt`` öffnet die serielle Schnittstelle, keine
                       Datei. Auch als VERZEICHNIS (``…\\COM1\\datei.txt``) —
                       das kam bis zum 18.08.2026 durch die Prüfung und
                       scheiterte erst beim Zugriff, mit einem ``OSError``
                       statt einer klaren Absage.
    Punkt/Leerzeichen  ``resolve()`` behält sie, das Dateisystem schneidet sie
                       ab (gemessen 13.08.2026). Die Antwort nennt dann einen
                       Pfad, den es so nie gab.
    Verbotene Zeichen  ``<>:"|?*`` und alles unter 0x20. Der Doppelpunkt ist der
                       gefährliche: ``video:1.mp4`` ist unter NTFS kein
                       Dateiname, sondern der Datenstrom ``1.mp4`` der Datei
                       ``video``. Gemessen wurde eine 0 Byte große Datei
                       ``video``, der Inhalt lag unsichtbar im Datenstrom — und
                       der Export meldete Erfolg.

Die Meldungstexte sind Teil der Schnittstelle: Sie gehen als Ablehnungsgrund an
den Aufrufer und stehen so in ``test_safe_paths``.
"""

#: Windows-Gerätenamen. Ein Schreibversuch darauf ist nie gewollt. Auch mit
#: Endung (``COM1.txt``) und in jeder Schreibweise — deshalb wird vor dem
#: Vergleich auf Großbuchstaben gehoben und ab dem ersten Punkt abgeschnitten.
GERAETE = {
    'CON', 'PRN', 'AUX', 'NUL', 'CLOCK$',
    *('COM%d' % i for i in range(1, 10)),
    *('LPT%d' % i for i in range(1, 10)),
}

#: Zeichen, die in einem Namensbestandteil nicht vorkommen dürfen (13.08.2026).
#: Die übrigen kann Windows ohnehin nicht anlegen — sie früh abzulehnen erspart
#: einen ``OSError`` an einer Stelle, die nichts mehr erklären kann.
VERBOTEN = frozenset('<>:"|?*') | frozenset(chr(c) for c in range(32))


class Namensregeln:
    u"""Die Einzelprüfungen. Jede gibt einen Ablehnungsgrund oder ``None``."""

    @staticmethod
    def geraet(teil, was='Pfadteil'):
        if teil.split('.')[0].upper() in GERAETE:
            return 'Gerätename ist kein gültiger %s: %s' % (was.lower(), teil)
        return None

    @staticmethod
    def zeichen(teil, was='Pfad'):
        if VERBOTEN & set(teil):
            return 'Unzulässiges Zeichen im %s' % was
        return None

    @staticmethod
    def endet_sauber(teil, was='Pfadteil'):
        if teil != teil.rstrip(' .'):
            return '%s darf nicht auf Punkt oder Leerzeichen enden' % was
        return None

    @classmethod
    def teil(cls, teil):
        u"""Erster Ablehnungsgrund für einen PFADbestandteil — oder ``None``."""
        return (cls.zeichen(teil, 'Pfad')
                or cls.geraet(teil, 'Pfadteil')
                or cls.endet_sauber(teil, 'Pfadteil'))

    @classmethod
    def datei(cls, name):
        u"""Erster Ablehnungsgrund für einen DATEInamen — oder ``None``.

        Zusätzlich zum Pfadteil: kein führender Bindestrich. Der Name landet in
        Kommandozeilen (ffmpeg im Videoexport), und ``-i.mp4`` würde dort als
        OPTION gelesen. Praktisch schützt der vorangestellte Verzeichnispfad —
        aber die nächste Aufrufstelle stellt ihn vielleicht nicht davor
        (Einwand aus dem Sparring, 12.08.2026).
        """
        grund = (cls.zeichen(name, 'Dateinamen')
                 or cls.geraet(name, 'Dateiname')
                 or cls.endet_sauber(name, 'Dateiname'))
        if grund:
            return grund
        if name.startswith('-'):
            return 'Dateiname darf nicht mit einem Bindestrich beginnen'
        return None
