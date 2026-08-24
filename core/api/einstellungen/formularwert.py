# -*- coding: utf-8 -*-
"""Formularwert — ein Wert aus einem POST, geprüft und begrenzt.

WARUM DIESE KLASSE (Umbau 17.08.2026)
=====================================
In `core/api/einstellungen.py` stand dieselbe Rechnung 24 Mal:

    s.mp_min_detection_confidence = max(0.0, min(1.0,
        float(request.POST.get('mp_min_detection_confidence', 0.5))))

    s.rtmpose_model_size = request.POST.get('rtmpose_model_size', 'l')
    if s.rtmpose_model_size not in ('m', 'l', 'x'):
        s.rtmpose_model_size = 'l'

Zwölf Zahlen mit Grenzen, acht Auswahlfelder mit Vorgabe, dazu Text und
Ankreuzfelder. Jede Kopie kann eine andere Grenze haben, und beim Lesen sieht
man den Unterschied nicht — genau die Sorte Stelle, an der später ein
Schreibfehler sitzt (Kriterium 6).

Hier steht jede Sorte EINMAL, und die Seiten sagen nur noch, welche Grenze gilt.
"""


class Formularwert:
    """Statische Leser für die vier Sorten Formularfeld."""

    @staticmethod
    def text(post, name, vorgabe=''):
        """Getrimmter Text; leer bedeutet Vorgabe (auch die leere Vorgabe)."""
        return post.get(name, '').strip() or vorgabe

    @staticmethod
    def schalter(post, name):
        """Ankreuzfeld: `on` heißt an, alles andere aus."""
        return post.get(name) == 'on'

    @staticmethod
    def zahl(post, name, vorgabe, mini=None, maxi=None, ganz=False):
        """Zahl mit Grenzen. `ValueError`/`TypeError` gehen an den Aufrufer.

        Absichtlich NICHT abgefangen: Die Seite antwortet mit „Invalid value."
        und protokolliert — das ist der gemeinsame Ablauf in
        `Einstellungsseite.post`. Ein stiller Rückfall auf die Vorgabe würde
        einen Tippfehler im Formular unsichtbar machen.
        """
        roh = post.get(name, vorgabe)
        wert = int(roh) if ganz else float(roh)
        if mini is not None:
            wert = max(mini, wert)
        if maxi is not None:
            wert = min(maxi, wert)
        return wert

    @staticmethod
    def auswahl(post, name, erlaubt, vorgabe):
        """Einer aus `erlaubt` — was nicht dazugehört, wird zur Vorgabe.

        Hier ist der stille Rückfall richtig: Ein Auswahlfeld schickt nur, was
        im Formular steht; ein anderer Wert kommt von Hand oder von einer alten
        Seite, und dann ist die Vorgabe die einzige sinnvolle Antwort.
        """
        wert = post.get(name, vorgabe)
        return wert if wert in erlaubt else vorgabe

    @staticmethod
    def aufgeklappt(post, vorsilbe):
        """Namen der angekreuzten Klapp-Bereiche (`panel_scene_licht` → `licht`)."""
        return [k[len(vorsilbe):] for k in post
                if k.startswith(vorsilbe) and post[k] == 'on']
