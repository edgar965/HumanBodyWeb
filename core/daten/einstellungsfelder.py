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

        # ------------------------------------------------- Effekte (12.09.2026)
        # Edgar: „erstelle eine Seite Einstellungen - Effekte wo man das
        # Standard Modell auswählen kann … standard: Female2 sowie andere
        # settings". Die Zahlen sind die Startwerte der Regler auf der
        # Effekte-Seite; die Grenzen sind die der `Figurparameter`-Felder.
        'effekte_default_animation': F(
            u'Standard-Animation',
            u'Welche Animation die Effekte-Seite beim Laden vorwählt; ohne '
            u'Angabe die neueste passende aus „Process Videos"'),
        'effekte_video_fps': F(
            u'Bildrate', u'Bilder je Sekunde des Videos; bei 60-fps-BVHs gibt '
            u'30 den Schritt 1, 24 gäbe Zeitlupe', min=10, max=60, schritt=1),
        'effekte_video_width': F(
            u'Breite (px)', u'Videobreite — Vorgabe des Reglers auf der Effekte-Seite',
            min=320, max=3840, schritt=1),
        'effekte_video_height': F(
            u'Höhe (px)', u'Videohöhe — Vorgabe des Reglers auf der Effekte-Seite',
            min=240, max=2160, schritt=1),
        'effekte_wind': F(
            u'Wind (m/s)', u'Windstärke der Stoffdynamik (HumanBody-Figur); '
            u'0 = kein Wind', min=0, max=30, schritt=0.1),

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
        'gvhmr_smooth_sigma': F(
            u'Temporal Smoothing',
            u'Gaußsche Glättung der Gelenkwinkel im BVH (0 = aus, 2 = Standard, '
            u'4 und mehr = stark). Vorgabe für die Karte auf der Uploadseite; '
            u'gilt auch für den Körper-Durchlauf des Hybrid-Laufs',
            min=0, max=10, schritt='0.5'),
        'gvhmr_joint_limits': F(
            u'Joint Limits',
            u'Anatomische Grenzen für Knie, Ellbogen und Hüfte im BVH anwenden. '
            u'Vorgabe für die Karte auf der Uploadseite'),
        'gvhmr_use_dpvo': F(
            u'DPVO',
            u'Kamerabahn mit DPVO statt SimpleVO schätzen (genauer, langsamer, '
            u'mehr VRAM). Wirkt nur ohne statische Kamera. Vorgabe für die Karte'),
        'gvhmr_verbose': F(
            u'Verbose',
            u'Debug-Videos der Vorstufen ausgeben (Personenkästen, ViTPose-'
            u'Skelett) — liest das Video dafür komplett in den Speicher. '
            u'Vorgabe für die Karte'),
        'gvhmr_render': F(
            u'Demo-Videos rendern',
            u'Kamera-, Welt- und Vergleichsvideo erzeugen (pytorch3d). Bei '
            u'7.538 Bildern die Hälfte der Laufzeit; ohne sie bleibt das BVH. '
            u'Die Videos kopiert „3D Video Output" in den Ausgabeordner'),

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

        # ----------------------------------------------------------- GEM-SMPL
        'gem_static_cam': F(
            u'Static Camera',
            u'Statische Kamera annehmen. Das Video-Demo von GEM verfolgt die '
            u'Kamera ohnehin nicht; der Schalter setzt nur die Kamera-Maske '
            u'des Modells'),
        'gem_smooth_sigma': F(
            u'Temporal Smoothing',
            u'Gaußsche Glättung der Gelenkwinkel im BVH (0 = aus, 2 = Standard, '
            u'4 und mehr = stark). Vorgabe für die Karte auf der Uploadseite',
            min=0, max=10, schritt='0.5'),
        'gem_joint_limits': F(
            u'Joint Limits',
            u'Anatomische Grenzen für Knie, Ellbogen und Hüfte im BVH anwenden. '
            u'Vorgabe für die Karte auf der Uploadseite'),
        'gem_render': F(
            u'Demo-Videos rendern',
            u'Kamera-, Welt- und Vergleichsvideo mit Open3D erzeugen (dauert '
            u'länger, liest das Video komplett in den Speicher). Vorgabe für '
            u'die Karte'),

        # -------------------------------------------------------------- DuoMo
        'duomo_static_cam': F(
            u'Static Camera',
            u'Statische Kamera annehmen. DuoMo liefert ohne Kamerabahn ohnehin '
            u'eine feste Kamera; der Schalter ist die Vorgabe der Karte'),
        'duomo_smooth_sigma': F(
            u'Temporal Smoothing',
            u'Gaußsche Glättung der Gelenkwinkel im BVH (0 = aus, 2 = Standard, '
            u'4 und mehr = stark). Vorgabe für die Karte auf der Uploadseite',
            min=0, max=10, schritt='0.5'),
        'duomo_joint_limits': F(
            u'Joint Limits',
            u'Anatomische Grenzen für Knie, Ellbogen und Hüfte im BVH anwenden. '
            u'Vorgabe für die Karte auf der Uploadseite'),

        # -------------------------------------------------------------- GEM-X
        'gemx_static_cam': F(
            u'Static Camera',
            u'Statische Kamera annehmen — wie bei GEM-SMPL nur die Kamera-Maske '
            u'des Modells. Vorgabe für die Karte auf der Uploadseite'),
        'gemx_smooth_sigma': F(
            u'Temporal Smoothing',
            u'Gaußsche Glättung der Gelenkwinkel im BVH (0 = aus, 4 = Standard seit '
            u'12.09.2026: gemessen halbiert sie das Körperzittern von GEM-X bei '
            u'gleicher Deckung; 2 = weniger). Gelenkgrenzen gibt es für GEM-X nicht: SOMA '
            u'hat 77 Gelenke, die Grenzen sind SMPL-Indizes',
            min=0, max=10, schritt='0.5'),
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
