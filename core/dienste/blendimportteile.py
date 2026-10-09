# -*- coding: utf-8 -*-
"""Blendimportteile — welche Körperteile ein Stück der .blend tragen dürfen (für `Kleidungsentposen.teile_von`).

Warum (09.10.2026, „Asian girl", rechte Hand auf der Hüfte): Ein Saum, der neben der Hand hängt, fand dort die meisten
Käfigpunkte und drehte mit der Hand zurück — der Pullover zog sich zur Hand, die Shorts rissen. Ein Pullover trägt Rumpf,
Becken, Arme und Oberschenkel, nie eine Hand; Shorts tragen Becken und Beine; Schuhe die Füße und den Unterschenkel.
Hände gehören keinem Stück (Handschuhe gibt es in dieser Rollenzuordnung nicht).
"""

from Genesis9.koerperteile import G9koerperteile

__all__ = ['Blendimportteile']


class Blendimportteile:
    RUMPF = ('hals', 'rumpf', 'becken', 'l_schulter', 'r_schulter')
    ARME = ('l_oberarm', 'r_oberarm', 'l_unterarm', 'r_unterarm')
    OBERSCHENKEL = ('l_oberschenkel', 'r_oberschenkel')
    UNTERSCHENKEL = ('l_unterschenkel', 'r_unterschenkel')
    FUESSE = ('l_fuss', 'r_fuss')

    #: Ordner der Rolle (`Blendimportrollen.kategorie`) → Teile.
    JE_ORDNER = {
        'tops': RUMPF + ARME + OBERSCHENKEL,
        'dresses': RUMPF + ARME + OBERSCHENKEL + UNTERSCHENKEL,
        'pants': ('rumpf', 'becken') + OBERSCHENKEL + UNTERSCHENKEL,
        'shoes': FUESSE + UNTERSCHENKEL,
        'accessories': OBERSCHENKEL + UNTERSCHENKEL + FUESSE,        # Socken, Strümpfe (Strumpfhalter hängen am Oberschenkel)
    }
    #: Teil → Knochen, der es führt (für Stücke, die ganz an EINEM Teil hängen: Requisiten, `Blendimportrequisit`; das Haar hängt an `head`).
    KNOCHEN = {'kopf': 'head', 'hals': 'neck2', 'rumpf': 'spine4', 'becken': 'pelvis',
               'l_schulter': 'l_shoulder', 'l_oberarm': 'l_upperarm', 'l_unterarm': 'l_forearm', 'l_hand': 'l_hand',
               'r_schulter': 'r_shoulder', 'r_oberarm': 'r_upperarm', 'r_unterarm': 'r_forearm', 'r_hand': 'r_hand',
               'l_oberschenkel': 'l_thigh', 'l_unterschenkel': 'l_shin', 'l_fuss': 'l_foot',
               'r_oberschenkel': 'r_thigh', 'r_unterschenkel': 'r_shin', 'r_fuss': 'r_foot'}
    #: Unterwäsche: der BH trägt den Rumpf, alles andere Becken und Oberschenkel.
    BH = ('hals', 'rumpf', 'l_schulter', 'r_schulter', 'becken')
    SLIP = ('rumpf', 'becken') + OBERSCHENKEL

    @classmethod
    def erlaubt(cls, ordner, name=''):
        """Teilnummern, die ein Stück dieser Art tragen dürfen — None: alle."""
        if ordner == 'underwear':
            namen = cls.BH if 'bra' in str(name).lower() else cls.SLIP
        else:
            namen = cls.JE_ORDNER.get(ordner)
        if namen is None:
            return None
        return sorted(G9koerperteile.NUMMER[n] for n in namen)
