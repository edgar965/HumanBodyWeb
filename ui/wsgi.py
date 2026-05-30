import os
from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ui.settings')
application = get_wsgi_application()

from core.logging_utils import install_stdout_timestamps  # noqa: E402
install_stdout_timestamps()
