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
