# -*- coding: utf-8 -*-
"""Kleiderverwaltung: Umbenennen, Verschieben, Kopieren, Löschen in der
Kleider-Bibliothek.

DER BEFUND (17.08.2026): Die Kontextmenüs der Kleider- und der MakeHuman-Liste
bieten seit langem vier Aktionen an und rufen dafür
`/api/character/garment/manage/`. **Diesen Endpunkt gab es nicht.** Acht
Aufrufstellen in zwei Modulen liefen in eine 404; `Serverabruf.senden` prüft
`.ok`, wirft — und der umgebende `catch` schrieb die Meldung nur in die Konsole.
Für den Benutzer passierte beim Klick auf „Umbenennen" also gar nichts, ohne
jeden Hinweis. Gefunden nicht durch Ausprobieren, sondern durch einen Abgleich
aller Adress-Literale des Frontends gegen Djangos URL-Konfiguration.

AUFBAU wie `Bvhverwaltung` (dasselbe Muster, dieselbe Fehlerklasse): eine
Zuordnung Aktion → Methode statt einer Kette von `elif`, und die Pfadprüfung an
genau einer Stelle.

WAS EIN KLEID IST: ein VERZEICHNIS unter `<bibliothek>/<kategorie>/<name>/`,
darin Metadaten, Netz und Textur. Die Kennung ist `"<kategorie>/<name>"` — so
bildet `GarmentLibrary.scan()` sie, und so schickt sie das Frontend zurück.

WARUM „LÖSCHEN" NICHT LÖSCHT: `delete` verschiebt das Verzeichnis nach
`<bibliothek>/.trash/<kategorie>__<name>/`. Der Bibliotheks-Scanner überspringt
Ordner, die mit einem Punkt beginnen — für die Oberfläche ist das Kleid damit
weg, auf der Platte bleibt es. Diese Bibliothek liegt unter
`HumanBody/data/garment_library`, also in den Produktivdaten; ein `rmtree` dort
ist unumkehrbar, und ein Fehlklick im Kontextmenü wäre nicht zu heilen. Wer
wirklich Platz braucht, leert `.trash` von Hand.
"""

import logging
import shutil
from pathlib import Path

from django.conf import settings

from .dienstfehler import DienstFehler

logger = logging.getLogger('core')

#: Ordner für gelöschte Kleider. Der Punkt hält ihn aus dem Bibliotheks-Scan.
PAPIERKORB = '.trash'


class KleiderFehler(DienstFehler):
    """Ablehnung der Kleider-Verwaltung. Rumpf und Kennzahl siehe `DienstFehler`."""


class Kleiderverwaltung:
    """Die vier Verwaltungsaktionen der Kleider-Bibliothek."""

    @staticmethod
    def ausfuehren(daten):
        """Aktion aus den Anfragedaten ausführen. Wirft KleiderFehler."""
        aktion = str(daten.get('action', '')).strip()
        arbeit = {
            'rename': Kleiderverwaltung._umbenennen,
            'move': Kleiderverwaltung._verschieben,
            'copy': Kleiderverwaltung._kopieren,
            'delete': Kleiderverwaltung._loeschen,
        }.get(aktion)
        if not arbeit:
            raise KleiderFehler(f'Unknown action: {aktion}')
        logger.info('[garment-manage] action=%s id=%s', aktion,
                    daten.get('id', ''))
        return arbeit(daten)

    # ------------------------------------------------------------- Hilfsmittel

    @staticmethod
    def wurzel():
        return Path(settings.HUMANBODY_GARMENT_LIBRARY_DIR)

    @staticmethod
    def _pflicht(daten, *felder):
        """Verlangte Felder lesen; fehlt eines, mit 400 abbrechen."""
        werte = [str(daten.get(f, '')).strip() for f in felder]
        if not all(werte):
            raise KleiderFehler('%s required' % ', '.join(felder))
        return werte

    @staticmethod
    def _teil(name, was):
        """Ein einzelner Pfadteil — kein Trenner, kein `..`, kein Punkt vorn.

        Ohne diese Prüfung wäre `new_name = "../../andere"` ein Weg aus der
        Bibliothek heraus. Der Punkt vorn ist ausgeschlossen, weil der Scanner
        solche Ordner überspringt: Ein Kleid namens `.x` wäre nach dem
        Umbenennen unsichtbar und sähe wie Datenverlust aus.
        """
        if '/' in name or '\\' in name or name.startswith('.') or name == '..':
            raise KleiderFehler(f'Invalid {was}: {name}')
        return name

    @staticmethod
    def _kleid(kennung):
        """Vorhandenes Kleid-Verzeichnis zu `"<kategorie>/<name>"`."""
        teile = [t for t in str(kennung).replace('\\', '/').split('/') if t]
        if len(teile) != 2:
            raise KleiderFehler(f'Invalid id: {kennung}')
        kategorie = Kleiderverwaltung._teil(teile[0], 'category')
        name = Kleiderverwaltung._teil(teile[1], 'name')
        pfad = Kleiderverwaltung.wurzel() / kategorie / name
        if not Kleiderverwaltung._liegt_in_bibliothek(pfad):
            raise KleiderFehler(f'Invalid id: {kennung}')
        if not pfad.is_dir():
            raise KleiderFehler('Garment not found', 404)
        return kategorie, name, pfad

    @staticmethod
    def _liegt_in_bibliothek(pfad):
        """Doppelte Sicherung: liegt der aufgelöste Pfad unter der Wurzel?

        Die Teilprüfung oben verhindert `..` schon im Namen; das hier fängt
        zusätzlich Symlinks und Groß-/Kleinschreibungs-Eigenheiten von Windows.
        """
        try:
            wurzel = Kleiderverwaltung.wurzel().resolve()
            ziel = Path(pfad).resolve()
        except OSError:
            logger.debug('Pfad %s nicht auflösbar — gilt als außerhalb', pfad,
                         exc_info=True)
            return False
        return wurzel == ziel or wurzel in ziel.parents

    @staticmethod
    def _freies_ziel(pfad, meldung):
        """Geprüftes Ziel, das es noch nicht gibt."""
        if not Kleiderverwaltung._liegt_in_bibliothek(pfad):
            raise KleiderFehler('Invalid target path')
        if pfad.exists():
            raise KleiderFehler(meldung, 409)
        return pfad

    # ------------------------------------------------------------------ Aktionen

    @staticmethod
    def _umbenennen(daten):
        kennung, neu = Kleiderverwaltung._pflicht(daten, 'id', 'new_name')
        kategorie, _name, alt = Kleiderverwaltung._kleid(kennung)
        neu = Kleiderverwaltung._teil(neu, 'new_name')
        ziel = Kleiderverwaltung._freies_ziel(
            Kleiderverwaltung.wurzel() / kategorie / neu,
            f'{neu} exists already')
        alt.rename(ziel)
        logger.info('[garment-manage] Renamed: %s -> %s', alt, ziel)
        return {'ok': True, 'id': f'{kategorie}/{neu}', 'new_name': neu}

    @staticmethod
    def _verschieben(daten):
        kennung, ziel_kategorie = Kleiderverwaltung._pflicht(
            daten, 'id', 'target_category')
        _kategorie, name, alt = Kleiderverwaltung._kleid(kennung)
        ziel_kategorie = Kleiderverwaltung._teil(ziel_kategorie,
                                                 'target_category')
        ordner = Kleiderverwaltung.wurzel() / ziel_kategorie
        if not Kleiderverwaltung._liegt_in_bibliothek(ordner):
            raise KleiderFehler('Invalid target category')
        ordner.mkdir(parents=True, exist_ok=True)
        ziel = Kleiderverwaltung._freies_ziel(
            ordner / name, f'{name} already in {ziel_kategorie}')
        shutil.move(str(alt), str(ziel))
        logger.info('[garment-manage] Moved: %s -> %s', alt, ziel)
        return {'ok': True, 'id': f'{ziel_kategorie}/{name}'}

    @staticmethod
    def _kopieren(daten):
        kennung, neu = Kleiderverwaltung._pflicht(daten, 'id', 'new_name')
        kategorie, _name, alt = Kleiderverwaltung._kleid(kennung)
        ziel_kategorie = Kleiderverwaltung._teil(
            str(daten.get('target_category', '')).strip() or kategorie,
            'target_category')
        ordner = Kleiderverwaltung.wurzel() / ziel_kategorie
        ordner.mkdir(parents=True, exist_ok=True)
        neu = Kleiderverwaltung._teil(neu, 'new_name')
        ziel = Kleiderverwaltung._freies_ziel(ordner / neu,
                                              f'{neu} already exists')
        shutil.copytree(str(alt), str(ziel))
        logger.info('[garment-manage] Copied: %s -> %s', alt, ziel)
        return {'ok': True, 'id': f'{ziel_kategorie}/{neu}'}

    @staticmethod
    def _loeschen(daten):
        """In den Papierkorb verschieben, nicht von der Platte nehmen.

        Begründung im Modulkopf: Die Bibliothek liegt in den Produktivdaten.
        """
        (kennung,) = Kleiderverwaltung._pflicht(daten, 'id')
        kategorie, name, pfad = Kleiderverwaltung._kleid(kennung)
        korb = Kleiderverwaltung.wurzel() / PAPIERKORB
        korb.mkdir(parents=True, exist_ok=True)
        ziel = korb / f'{kategorie}__{name}'
        zaehler = 2
        while ziel.exists():                 # zweimal dasselbe gelöscht
            ziel = korb / f'{kategorie}__{name}_{zaehler}'
            zaehler += 1
        shutil.move(str(pfad), str(ziel))
        logger.info('[garment-manage] In den Papierkorb: %s -> %s', pfad, ziel)
        return {'ok': True, 'papierkorb': str(ziel.relative_to(
            Kleiderverwaltung.wurzel()))}
