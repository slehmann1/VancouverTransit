from django.apps import AppConfig
import sys


_started_poll = False
class VancouverTransitAnalyzerConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "vancouver_transit_analyzer"

    def ready(self, *args, **kwargs):
        global _started_poll
        is_manage_py = any(arg.casefold().endswith("manage.py") for arg in sys.argv)
        is_runserver = any(arg.casefold() == "runserver" for arg in sys.argv)

        if ((is_manage_py and is_runserver) or (not is_manage_py)) and not _started_poll:
            _started_poll = True
            # Can't import until after apps are ready
            from scripts import gtfs_poller
            gtfs_poller.run()
            