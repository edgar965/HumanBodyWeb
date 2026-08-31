# -*- coding: utf-8 -*-
u"""Einstellungsfelder — das Register aller erklärten Einstellungen.

Die eine Quelle für Titel, Erklärung und Grenzen; das Model holt seinen
`help_text` hier, die Vorlagen ihre Zeile. Begründung und Vorgeschichte
stehen in `einstellungsfeld.py`.

WAS SICH DABEI GEÄNDERT HAT (30.08.2026), damit es niemand für einen
Fehler hält:

- `mp_min_detection_confidence` und `mp_min_tracking_confidence` heissen
  jetzt auf BEIDEN Seiten gleich. Vorher stand auf der 2D-Seite
  „Detection Confidence" mit der Erklärung „Mindest-Konfidenz damit ein
  Pose-Ergebnis als erkannt gilt", auf der 3D-Seite „MediaPipe Detection
  Confidence" mit „Mindest-Konfidenz für die Pose-Erkennung" — dasselbe
  Feld, dieselbe Datenbankspalte.
- `progress_update_interval` erklärt sich auf Deutsch wie alle anderen.
- Die drei Rig-Felder sagen, welche Seite sie meinen. Sie standen mit
  wortgleicher Beschriftung untereinander; erkennbar waren sie nur an der
  Gruppenüberschrift darüber.
"""
from .einstellungsfeld import Einstellungsfeld as F


class Einstellungsfelder:
    u"""Nachschlagewerk: Feldname → `Einstellungsfeld`."""

    #: Feldname wie in `AppSettings` — die Vorlagen greifen mit diesem Namen zu.
    REGISTER = {
        # ----------------------------------------------------- Modelle/Prozess
        'progress_update_interval': F(
            u'Fortschritt', u'Nach wie vielen Bildern der Balken weiterrückt. '
            u'Kleinere Werte melden häufiger und kosten etwas Rechenzeit',
            min=1, max=10000, schritt=1),
        'show_rig_config': F(
            u'', u'Rig auf der Konfigurationsseite von Anfang an einblenden',
            zusatz=u'Rig beim Start anzeigen'),
        'show_rig_animations': F(
            u'', u'Rig auf der Animationsseite von Anfang an einblenden',
            zusatz=u'Rig beim Start anzeigen'),
        'show_rig_scene': F(
            u'', u'Rig auf der Szenenseite von Anfang an einblenden',
            zusatz=u'Rig beim Start anzeigen'),
        'smpl_default_wireframe': F(
            u'Wireframe', u'Body als Drahtgitter anzeigen',
            zusatz=u'Wireframe aktivieren'),

        # ------------------------------------------ Standard-Animationen
        # Fuenfmal dasselbe Feld fuer fuenf Seiten. Vier davon hatten gar
        # keinen Titel und liefen unter der Vorgabe „Default Animation" —
        # englisch, mitten unter deutschen Zeilen.
        'default_anim_config': F(
            u'Standard-Animation',
            u'Welche Animation die Konfigurationsseite von sich aus lädt'),
        'default_anim_animations': F(
            u'Standard-Animation',
            u'Welche Animation die Animationsseite von sich aus lädt'),
        'default_anim_scene': F(
            u'Standard-Animation',
            u'Welche Animation die Szenenseite von sich aus lädt'),
        'default_anim_result': F(
            u'Standard-Animation',
            u'Welche Animation die Ergebnisseite von sich aus lädt'),
        'theatre_default_animation': F(
            u'Standard-Animation',
            u'Welche Animation beim Laden der Theatre-Seite abgespielt wird'),

        # --------------------------------------------- MediaPipe (2D UND 3D)
        'mp_min_detection_confidence': F(
            u'MediaPipe Detection Confidence',
            u'Mindest-Konfidenz, damit eine Pose als erkannt gilt',
            min='0.0', max='1.0', schritt='0.05'),
        'mp_min_tracking_confidence': F(
            u'MediaPipe Tracking Confidence',
            u'Mindest-Konfidenz für das Pose-Tracking zwischen Bildern. '
            u'Niedrig = seltener neu erkennen',
            min='0.0', max='1.0', schritt='0.05'),

        # ------------------------------------------------------- MocapNET v4
        'v4_hcd_iterations': F(
            u'HCD Iterations',
            u'IK-Gradient-Descent-Iterationen pro Bild. Mehr = genauer, '
            u'aber langsamer', min=1, max=100, schritt=1),
        'v4_hcd_epochs': F(
            u'HCD Epochs',
            u'IK-Epochen pro Bild. Mehr Epochen verbessern die Pose-Qualität',
            min=1, max=200, schritt=1),
        'v4_hcd_learning_rate': F(
            u'HCD Learning Rate', u'Lernrate für den IK-Gradient-Descent-Solver',
            min='0.0001', max='0.1', schritt='0.0001'),
        'v4_smoothing_cutoff': F(
            u'Smoothing Cutoff (Hz)',
            u'Butterworth-Tiefpass-Grenzfrequenz. Niedrigere Werte = glattere '
            u'Animation', min='0.5', max='15.0', schritt='0.5'),
        'v4_smoothing_sampling': F(
            u'Smoothing Sampling (Hz)',
            u'Abtastfrequenz für den Butterworth-Filter. Sollte zur Bildrate '
            u'des Videos passen', min='10.0', max='120.0', schritt='1.0'),

        # -------------------------------------------------------------- GVHMR
        'gvhmr_static_cam': F(
            u'Static Camera',
            u'Statische Kamera annehmen (kein DPVO). Empfohlen für eine feste '
            u'Kameraperspektive'),
        'gvhmr_focal_length_mm': F(
            u'Focal Length (mm)',
            u'Brennweite der Kamera in mm. 0 = automatisch schätzen '
            u'(empfohlen)', min=0, max=200, schritt='0.5'),

        # --------------------------------------------------------------- WHAM
        'wham_estimate_local_only': F(
            u'Estimate Local Only',
            u'Nur die lokale Körperbewegung schätzen, keine globale Bahn'),
        'wham_run_smplify': F(
            u'Run SMPLify',
            u'SMPLify-Verfeinerung ausführen. Langsamer, aber genauer'),

        # ---------------------------------------------------------- PromptHMR
        'prompthmr_static_camera': F(
            u'Static Camera',
            u'Statische Kamera annehmen. Empfohlen für die meisten Videos'),
    }

    @classmethod
    def feld(cls, kennung):
        u"""Das `Einstellungsfeld` zu einem Feldnamen.

        WIRFT, wenn es den Namen nicht gibt. Ein stiller Rückfall auf einen
        leeren Datensatz gäbe eine Einstellungszeile ohne Titel und ohne
        Grenzen — sie sähe fertig aus und liesse jeden Wert durch.
        """
        try:
            return cls.REGISTER[kennung]
        except KeyError:
            raise KeyError(
                u'Kein Einstellungsfeld "%s". Bekannt sind: %s'
                % (kennung, ', '.join(sorted(cls.REGISTER))))

    @classmethod
    def hilfetext(cls, kennung):
        u"""Der `help_text` fürs Model — dieselbe Erklärung wie auf der Seite."""
        return cls.feld(kennung).hilfetext
