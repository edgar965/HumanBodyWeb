import sys

from django.apps import AppConfig


class CoreConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'core'

    def ready(self):
        """Beim Serverstart: Zwischendateien aufräumen, verwaiste Aufträge einordnen.

        Der Ablauf steht in `core.dienste.startaufraeumen.Startaufraeumen` (bis
        zum 17.08.2026 waren es hier 92 Zeilen). In einer `ready()` gehört
        möglichst wenig: Sie läuft beim Start JEDES Serverprozesses, und was
        dort scheitert, verhindert den Start.

        Nur für den echten Server, nicht für `manage.py migrate` und Co. — sonst
        würde ein `migrate` laufende Aufträge als gescheitert vermerken.
        """
        if 'runserver' not in sys.argv:
            return
        from core.dienste.startaufraeumen import Startaufraeumen
        aufraeumen = Startaufraeumen()
        aufraeumen.zwischendateien()
        aufraeumen.durchgehen()
        # Genesis-9-Merker im Hintergrund fuellen (18.09.2026 abends): die
        # erste Figur nach einem Neustart kostete sonst 10–30 s.
        from core.dienste.g9aufwaermen import G9aufwaermen
        if G9aufwaermen.angebracht():
            G9aufwaermen.starten()
        # HumanBody-Merker (Hautgewichte, Morphs) ebenso (22.09.2026): BVH
        # Studio ruft sie bei JEDEM Start ab, auch fuer reine Genesis-9-
        # Projekte — kalt kosteten sie zusammen ueber 10 s (`hbaufwaermen.py`).
        # `G9aufwaermen.angebracht()` prueft nur runserver/RUN_MAIN, nichts
        # Genesis-9-Spezifisches — derselbe Gate fuer beide Faeden.
        from core.dienste.hbaufwaermen import Hbaufwaermen
        if G9aufwaermen.angebracht():
            Hbaufwaermen.starten()
