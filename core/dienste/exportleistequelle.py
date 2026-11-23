# -*- coding: utf-8 -*-
"""Exportleistequelle — was die Exportleiste von einem Bereich wissen muss (31.10.2026).

Edgar: „baue die ganze Exportleiste auf mit Physik usw." — „mach das als wiederverwendbares Modul". Die Leiste (`Exportleiste`, Vorlage `_exportleiste.html`, Seite
`static/viewer/exportleiste/`) kennt keinen Bereich; je Bereich erbt eine Klasse hiervon und sagt nur: Name des Modells, Vorgabe des Exportordners, eigener Arbeitsordner
(Render-Läufe, Regler, Bewegungen) und die Pfade für „Gespeichert unter". Das Modell selbst baut der Browser (die Figur der Seite) und schickt es mit jedem Export und
jedem Render als GLB; Bewegung, Blender und Render rechnet der Server. Eingetragen wird eine neue Quelle in `Exportleistebereiche`.

    quelle = Exportleistebereiche.quelle('meshgenesistest', 'koenigin1')     # oder None
    quelle.name(), quelle.exportordner(), quelle.arbeitsordner(), quelle.pfade()

Baut der Server die Figur selbst (2D3D Kleider: das Stand-Modell mit den Stoffstücken `kleidung__gc_` und den Haarsträhnen `haar__`, die der Render simuliert), setzt die Quelle
`EIGENES_MODELL`: Export (GLB, Blender) und Render nehmen dann `modell()` und `bewegung()` des Bereichs, die Seite schickt keine GLB, und der Render baut die Figur nicht aus der GLB der
Seite neu (`Exportleisterendermodell` benennt alle Stücke in `kleidung__eigen_…` um — Stoff und Strähnen wären starr). OBJ schreibt weiter der Browser aus der Figur der Seite.
"""

__all__ = ['Exportleistequelle']


class Exportleistequelle:
    #: Kennung des Bereichs in der Adresse (`/api/exportleiste/<bereich>/<kennung>/`).
    BEREICH = ''
    #: True: Export und Render nehmen das Modell des Bereichs (`modell`, `bewegung`), nicht die GLB der Seite.
    EIGENES_MODELL = False

    def __init__(self, kennung):
        self.kennung = str(kennung)

    @classmethod
    def finden(cls, kennung):
        """Die Quelle zu dieser Kennung — oder None (unbekannt; die Kennung kommt aus der Adresse)."""
        raise NotImplementedError

    def name(self):
        """Der Name des Modells — Vorgabe für Dateiname und Modellname."""
        raise NotImplementedError

    def exportordner(self):
        """Vorgabe des Feldes „Ordner“ (Path): dort landen GLB, OBJ, .blend und die Kopie des Videos."""
        raise NotImplementedError

    def arbeitsordner(self):
        """Eigener Ordner der Leiste (Path): `arbeit/` (Render-Programme, Regler, Läufe), `ergebnis/` (Videos, Bögen), Protokoll."""
        raise NotImplementedError

    def bvh_vorgabe(self):
        """Vorschlag für die Animation, wenn die Seite selbst keinen gibt (Pfad oder `Kategorie/Name`) — Vorgabe: keiner."""
        return ''

    def kacheln(self):
        """Hautkacheln der Figur für den Render (`{1001: Pfad}`, `Exportleisterendermodell`) — Vorgabe: keine, dann die Daz-Haut der Grundfigur."""
        return {}

    def ton_vorgabe(self):
        """Vorschlag für die Tonspur (Pfad oder '') — Vorgabe: die Audiospur des jüngsten Studio-Projekts."""
        from .studioton import Studioton
        return Studioton.pfad() or ''

    def regler_vorgabe(self):
        """Werte der Regler für Rendering und Physik, solange die Leiste keine eigenen hat (`{gruppe: {schluessel: wert}}`) — Vorgabe: keine, es gilt der Katalog."""
        return {}

    def sperre(self):
        """Grund, warum gerade nicht exportiert oder gerendert werden darf (Text) — oder None."""
        return None

    def modell(self):
        """Nur mit `EIGENES_MODELL`: die GLB des Bereichs (Path, mit Rig, ohne Animation) — ValueError mit der Meldung für die Seite, wenn es noch keine gibt."""
        raise NotImplementedError

    def kollision(self):
        """`(kapseln, kinematik)` für das Wegschieben der Stücke aus fremden Gliedern in der exportierten Bewegung (`Exportleistekollision`) — Vorgabe: None (keine Kapseln)."""
        return None

    def bewegung(self, bvh, stellung):
        """Die BVH (Path) auf die Figur gerechnet (`Bewegungsspuren.als_dict()`) — Vorgabe: derselbe Retarget wie im Browser aus der Stellung der Seite (`Exportleistebewegung`)."""
        from .exportleistebewegung import Exportleistebewegung
        return Exportleistebewegung.rechnen(bvh, stellung)

    # „Als Modell speichern“ — EIN Weg für jede Exportleiste (23.11.2026, Edgar: „nutze gemeinsamen Code für alle, was soll das???“, „eine einzige Speicherart!“). Bis dahin band jede
    # Seite den Knopf selbst (Mesh-Genesis-Test, Foto-Genesis, 2D3D Kleider: drei Klassen, drei Adressen); die Karte „Genesis-Ergebnis“ auf Foto-Genesis rief den Weg der Testseite mit einer
    # eigenen Prüfung und scheiterte an Edgar 1. Jetzt: `POST|GET /api/exportleiste/<bereich>/<kennung>/modell/` → diese zwei Methoden; was ein Modell ist, sagt `modellbau()` des Bereichs.

    def modellbau(self):
        """Wer das Modell baut: eine Klasse mit `starten(kennung, geschlecht, name, methoden)`, `stand(kennung, geschlecht)` und gern `methoden(kennung, geschlecht)` (Häkchen der
        Kleider; `Meshgenesistestmodell` und Ableitungen) — None: der Bereich speichert kein Modell."""
        return None

    def modell_geschlecht(self):
        """Das Geschlecht der Figur für `modellbau()` — Vorgabe: keins."""
        return None

    def modellname(self):
        """Vorgabe für das Feld „Modellname“."""
        return self.name()

    def modell_stand(self):
        """`{status: nie|laeuft|fertig|fehler|kein, name, meldung, fehler, methoden}` — `kein`: dieser Bereich speichert kein Modell. `methoden` (23.11.2026): die Häkchen der Kleider
        (`[{wert, text, anzahl}]`, `Meshgenesistestkleidmethoden.angebot`), nur wo der Bau sie kennt."""
        bau = self.modellbau()
        if bau is None:
            return {'status': 'kein', 'meldung': 'Hier gibt es kein „Als Modell speichern“.'}
        stand = dict(bau.stand(self.kennung, self.modell_geschlecht()) or {'status': 'nie'})
        if hasattr(bau, 'methoden'):
            stand['angebot'] = bau.methoden(self.kennung, self.modell_geschlecht())
        return stand

    def modell_speichern(self, name, methoden=None):
        """(Antwort, HTTP-Status) — startet „Als Modell speichern“; die Antwort trägt `stand` wie `modell_stand`. `methoden`: die angehakten Methoden der Kleider."""
        bau = self.modellbau()
        if bau is None:
            return {'error': 'Hier gibt es kein „Als Modell speichern“'}, 400
        return bau.starten(self.kennung, self.modell_geschlecht(), name, methoden)

    def pfade(self, exportordner=None):
        """„Gespeichert unter“: `[{art, label, pfad, fehlt}]` (`Meshpfadliste`). Vorgabe: Exportordner und Arbeitsordner."""
        ziel = exportordner or self.exportordner()
        arbeit = self.arbeitsordner()
        return [{'art': 'export', 'label': 'Exportordner (GLB, OBJ, Blender, Video)', 'pfad': str(ziel), 'fehlt': not ziel.is_dir()},
                {'art': 'arbeit', 'label': 'Arbeitsordner der Exportleiste (Render-Läufe, Regler)', 'pfad': str(arbeit), 'fehlt': not arbeit.is_dir()}]
