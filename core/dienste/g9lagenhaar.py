# -*- coding: utf-8 -*-
u"""G9lagenhaar — wie Haar, Kleidung und Kopfbedeckung übereinander liegen, wo die Tiefenregel (`G9lagen.einordnen`) es anders misst. Besitzer: Garderobe (Charakter-Seite),
genutzt von `G9lagenanfrage` (Browser und Mesh-Genesis-Kette, `Kleiderbau`).

Haar liegt über Kleidung (17.10.2026, Edgar mit Bild „02 Stretching G9B“: Shirt zerrissen, die Pose dauerte 30–60 s): Mit erhobenen Armen liegen die Ärmel am Haar; dort stand
das Haar näher an der Haut (des Arms) und galt als INNERES Stück. Das Shirt wurde über beide Haare gehoben — `_aeussere_stuecke` rechnete über 7.389 + 319.503 + 433.212 Punkte
20,8 s, ohne Pose 0,24 s (`ProjektTemp/_wegwerf/posen_lagen_diag.py`). In Daz weicht ebenso das Haar der Kleidung aus, nicht umgekehrt.

Eine Kopfbedeckung liegt über dem Haar (13.11.2026, „Genesis zuerst“ am Zauberer): Mit der Regel oben hob die Lagenrechnung das Haar über den Hut, der Hut (`mh_fedora01`,
1,48–1,66 m) lag ganz im Haar (`eirgrid_hair_g9`, bis 1,67 m) und war nicht zu sehen. In Daz sitzt der Hut außen und das Haar weicht ihm (Hut-Morph der Frisur oder Glättung mit
Kollision); unsere Lagen können nur das äußere Stück heben — also sitzt der Hut auf dem Haar. Kopfbedeckung = Kategorie der Garderobe (`G9garderobekategorien`, Edgars Zuordnung oder
Daz' Metadaten). Haar gegen Haar und Requisiten bleiben bei der Tiefenregel.
"""

__all__ = ['G9lagenhaar']


class G9lagenhaar:
    KOPFBEDECKUNG = 'Kopfbedeckung'

    @staticmethod
    def ordnen(kennung, innen, aussen, art, kopf):
        u"""(innen, aussen) nach den Regeln oben. `art(k)`: `art` des Eintrags (`kleidung`, `haar`, …); `kopf(k)`: ist `k` eine Kopfbedeckung?"""
        eigene = art(kennung)
        if eigene == 'haar':
            unter = [k for k in aussen if art(k) == 'kleidung' and not kopf(k)]
            ueber = [k for k in innen if art(k) == 'kleidung' and kopf(k)]
            return ([k for k in innen if k not in ueber] + unter, [k for k in aussen if k not in unter] + ueber)
        if eigene == 'kleidung' and kopf(kennung):
            haar = [k for k in aussen if art(k) == 'haar']
            return (innen + haar, [k for k in aussen if k not in haar])
        if eigene == 'kleidung':
            return ([k for k in innen if art(k) != 'haar'], aussen + [k for k in innen if art(k) == 'haar'])
        return innen, aussen

    @classmethod
    def ist_kopfbedeckung(cls, kennung):
        from Genesis9.garderobe import G9garderobe
        from Genesis9.garderobekategorien import G9garderobekategorien
        eintrag = G9garderobe.eintrag(kennung)
        return bool(eintrag) and eintrag.get('art') == 'kleidung' and G9garderobekategorien.kategorie(eintrag) == cls.KOPFBEDECKUNG
