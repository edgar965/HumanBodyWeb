from django.conf import settings


def version(request):
    """App-Version + Cache-Buster für JS/CSS.

    JS_VERSION wird von djangoBases _shell.html für ``extra_css`` mit
    ``?v={{ JS_VERSION|default:1 }}`` genutzt (Cache-Bust gegen Service-Worker/
    Browser-Cache). Wir hängen die App-Version dran, damit jeder Versions-Bump
    auch das djangoBase-seitige CSS frisch zieht.
    """
    return {
        'APP_VERSION': settings.VERSION,
        'JS_VERSION': settings.VERSION,
    }


def active_theme(request):
    """Aktiver Theme-Modus für ``<body data-theme="…">`` (Server-Render).

    djangoBases _shell.html rendert ``data-theme="{{ aktives_theme|default:
    theme_default }}"``. Damit es nur EINE Quelle gibt (HOWTO §5.4), leiten wir
    den Initial-Modus aus dem djangoBase-Profil ab: das helle CleanOrga-Layout
    -> 'light', sonst der konfigurierte theme_default ('dark').

    Der 5-Modi-Schalter im Topbar (base_app.html) überschreibt diesen Wert
    danach clientseitig aus localStorage — der Server-Wert verhindert nur das
    Aufblitzen des falschen Themes beim ersten Paint.
    """
    try:
        from djangobase.conf import conf
        c = conf()
        if (c.get('base_template') or '').endswith('base_cleanorga.html'):
            return {'aktives_theme': 'light'}
        return {'aktives_theme': c.get('theme_default') or 'dark'}
    except Exception:
        return {'aktives_theme': 'dark'}
