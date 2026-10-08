# -*- coding: utf-8 -*-
"""Die Optionen `iterationen.haltung_je_foto` und `iterationen.foto_abgleich` (08.10.2026) — Katalogeinträge (`FOTOOPTIONEN`, in `Iterationsoptionen.KATALOG` eingefügt) und Zugriff auf den Auftrag
(`Iterationsoptionenfoto.haltung_je_foto(job)`, `.foto_abgleich(job)`), aus `Iterationsoptionen` ausgelagert: die Datei war schon über 300 Zeilen. Was die Optionen tun: `Haltungsansichten`, `Fotoabgleich`."""

__all__ = ['FOTOOPTIONEN', 'Iterationsoptionenfoto']

HALTUNG_JE_FOTO = {
    'schluessel': 'haltung_je_foto',
    'titel': 'Haltung je Foto',
    'art': 'wahl',
    'vorgabe': 'an',
    'werte': [
        ('an', 'An — jedes Foto bekommt für Render, Maske und Fotohaut die Haltung, die es zeigt (Arme und Beine einzeln, auch gekreuzt oder angehoben)'),
        ('aus', 'Aus — alle Fotos teilen EINE Haltung, gemittelt über die Fotos, beide Arme und beide Beine gleich'),
    ],
    'hinweis': 'Haltung je Foto (Edgar, 08.10.2026: „Beine: nur 7 % Fotohaut. Eine Haltung passt nicht auf zwei verschiedene Aufnahmen"): Die Fotos eines Auftrags sind oft verschiedene Momente — an N1 zeigt das Vorderfoto einen Arm waagerecht und die Beine im Schritt '
    '(links 10° nach innen, rechts 9° nach außen), das Rückfoto hängende Arme und gerade Beine. Die gemittelte Haltung traf keins: Die Modellbeine lagen neben den Fotobeinen, die Fotohaut deckte die Unterschenkel zu 0 %. Je Foto wird Oberarm (Winkel zur Senkrechten), Ellbogen (Beugung) und '
    'Oberschenkel (Spreizung mit Vorzeichen) aus den Posenlandmarken des Fotos gestellt (Seitenansichten behalten die gemittelte Haltung; Knie, Schritt nach vorn und Arme nach vorn sind nicht erfasst). Gilt für Render, Teilmasken und die Fotohaut des Körpers, nicht für Kleider-Fototextur, Netznote und Befund.',
}

FOTO_ABGLEICH = {
    'schluessel': 'foto_abgleich',
    'titel': 'Foto auf die Silhouette des Modells legen (Fotohaut)',
    'art': 'wahl',
    'vorgabe': 'an',
    'werte': [
        ('an', 'An — vor der Projektion der Haut wird das Foto per optischem Fluss der Silhouetten in den Rahmen des Modells gezogen (Kniee, Schritt, Hüftversatz, Körperform)'),
        ('aus', 'Aus — das Foto bleibt, wie es ist; was nicht über der Silhouette des Modells liegt, bekommt keine Fotohaut'),
    ],
    'hinweis': 'Fotoabgleich (08.10.2026): Auch mit der Haltung je Foto lagen die Modellbeine an N1 neben den Fotobeinen (Rückansicht: Unterschenkel 0 % im Foto, Fotohaut der Beinkachel 20 %). Der Abgleich legt die Fotofläche per DIS-Fluss auf die Silhouette des Modells '
    '(IoU vorn 0,58 → 0,94, hinten 0,63 → 0,92; Beinband im Foto 47/64 → 88/90 %). Er ist kein Feinabgleich: der Fluss hat dort im Median 32–57 px (4–7 cm); die Innenzeichnung (Bräunungsstreifen, Muttermale) kann um einige Zentimeter verrutschen. Nur für die Haut des Körpers, nicht für Kleider, Haar und Kopf.',
}

FOTOOPTIONEN = [HALTUNG_JE_FOTO, FOTO_ABGLEICH]


class Iterationsoptionenfoto:
    @staticmethod
    def _an(job, schluessel):
        from .iterationsoptionen import Iterationsoptionen
        return Iterationsoptionen.pruefen((job.optionen or {}).get('iterationen')).get(schluessel) != 'aus'

    @classmethod
    def haltung_je_foto(cls, job):
        """Ob jedes Foto seine eigene Haltung bekommt (`Haltungsansichten`): Option `iterationen.haltung_je_foto` des Auftrags, Vorgabe an."""
        return cls._an(job, 'haltung_je_foto')

    @classmethod
    def foto_abgleich(cls, job):
        """Ob das Foto vor der Projektion der Haut auf die Silhouette des Modells gelegt wird (`Fotoabgleich`): Option `iterationen.foto_abgleich`, Vorgabe an."""
        return cls._an(job, 'foto_abgleich')
