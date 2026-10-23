# -*- coding: utf-8 -*-
"""Mesh3daitestkleidspeichern — Name und Kategorie, unter denen ein Stück eines Tests von Mesh3D-AI in die Garderobe kommt (22.10.2026).

Edgar (Karte „Kleider und Bestandteile“ der Testseite): „ich brauche hier eine Möglichkeit, sie unter einem bestimmten Namen und in einer Kategorie zu speichern. Mach die Namenänderung möglich und die
Kategorieauswahl der Combo, zum Beispiel Oberteile, Schuhe und so weiter“.
Gilt für die Stücke, die bei „Übernehmen und als Modell speichern“ eigene Genesis-Stücke werden (Wege b, k, s, f, g — `Mesh3daitesteigenstueck`); a und h sind schon Stücke der Garderobe.
Die Wahl steht in `einstellung.json` des Tests (`kleider_speichern` `{geschlecht: {id: {name, kategorie}}}`, nur Gesetztes); angewandt nach dem Bau des Stücks über die Pflege der Garderobe —
Anzeigename (`G9garderobepflege.umbenennen`, die Kennung bleibt) und Kategorie (`G9garderobekategorien.verschieben`, wie das Kontextmenü der Garderobe).
"""
import logging

logger = logging.getLogger('core')

__all__ = ['Mesh3daitestkleidspeichern']


class Mesh3daitestkleidspeichern:
    #: Wege, deren Stück bei der Übernahme ein eigenes Genesis-Stück wird.
    EIGENE = ('b', 'k', 's', 'f', 'g')
    #: Kategorie der Garderobe je Art bzw. Region eines Stücks (Vorgabe der Auswahl).
    KATEGORIE = {'oberteil': 'Oberteile', 'hose': 'Hosen', 'rock': 'Röcke', 'kleid': 'Kleider', 'anzug': 'Anzüge', 'unterwaesche': 'Unterwäsche', 'schuh': 'Schuhe', 'schuhe': 'Schuhe',
                 'kopfbedeckung': 'Kopfbedeckung', 'kopf': 'Kopfbedeckung', 'zubehoer': 'Zubehör', 'teil': 'Zubehör', 'haar': 'Haare'}
    MAXLAENGE = 80

    @classmethod
    def vorgabe(cls, st):
        return cls.KATEGORIE.get(st.get('art')) or cls.KATEGORIE.get(st.get('region')) or 'Zubehör'

    @staticmethod
    def kategorien():
        """Die Kategorien der Garderobe (Vorgaben, dann eigene)."""
        from Genesis9.garderobekategorien import G9garderobekategorien
        return G9garderobekategorien.laden()['kategorien']

    @classmethod
    def ergaenzen(cls, stuecke, einstellung, geschlecht):
        """Je Stück `speichern: {name, kategorie, kategorie_vorgabe, eigen}` (`eigen`: der gewählte Weg ergibt ein eigenes Stück)."""
        je = ((einstellung.get('kleider_speichern') or {}).get(geschlecht) or {})
        for st in stuecke:
            sp = je.get(st['id']) or {}
            st['speichern'] = {'name': sp.get('name') or '', 'kategorie': sp.get('kategorie') or cls.vorgabe(st), 'kategorie_vorgabe': cls.vorgabe(st),
                               'eigen': st.get('art') != 'haut' and st.get('wahl') in cls.EIGENE}

    @classmethod
    def pruefen(cls, name, kategorie):
        """→ (Name, Kategorie) gesäubert; `ValueError` mit Grund."""
        name = ' '.join(str(name or '').split())
        if len(name) > cls.MAXLAENGE or any(ord(z) < 32 for z in name):
            raise ValueError('Der Name ist zu lang (höchstens %d Zeichen) oder enthält Steuerzeichen.' % cls.MAXLAENGE)
        kategorie = ' '.join(str(kategorie or '').split())
        if kategorie and (len(kategorie) > 40 or not kategorie.isprintable()):
            raise ValueError('Kategorie „%s“ taugt nicht (1–40 Zeichen).' % kategorie)
        return name, kategorie

    @classmethod
    def anwenden(cls, stueck_kennung, sp, eintrag=None):
        """Nach dem Bau eines eigenen Stücks: Anzeigename und Kategorie in der Garderobe setzen → Text für den Bericht."""
        from Genesis9.garderobekategorien import G9garderobekategorien
        from Genesis9.garderobepflege import G9garderobepflege
        aus = {}
        if sp.get('name'):
            G9garderobepflege.umbenennen(stueck_kennung, sp['name'])
            aus['name'] = sp['name']
        if sp.get('kategorie'):
            vorgabe = G9garderobekategorien.vorgabe(eintrag) if eintrag else None
            G9garderobekategorien.verschieben(stueck_kennung, sp['kategorie'], vorgabe=vorgabe)
            aus['kategorie'] = sp['kategorie']
        logger.info('Mesh3D-AI Test: Stück %s in der Garderobe: %s', stueck_kennung, aus)
        return aus
