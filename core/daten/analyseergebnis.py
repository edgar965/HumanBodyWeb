# -*- coding: utf-8 -*-
"""Analyseergebnis — was die Fotoanalyse ueber eine Person herausgefunden hat.

WARUM EINE KLASSE (Umbau 15.08.2026): In `analyze_photo` wuchs ein Dict `resp`
ueber 150 Zeilen: erst zwoelf Felder auf einmal, dann `cam_data`, dann
`estimated_gender`, dann `measurements`, dann `skin_color`, dann `expression`,
dann `job_id`, dann `alignment_data`. Zwischendurch wurde es zweimal nach JSON
geschrieben und einmal wieder eingelesen (`data = dict(resp)`), und welche
Felder wann gesetzt sind, liess sich nur durch Lesen der ganzen Funktion
beantworten.

Das JSON fuer den Browser bleibt ein Dict — das ist die Zielform. Der Weg
dorthin fuehrt jetzt ueber benannte Felder mit einer Stelle je Bedeutung.
"""


class Analyseergebnis:
    """Ergebnis einer Fotoanalyse: Form, Herkunft, Zusatzangaben."""

    #: Kameraangaben, die fuer die automatische Ausrichtung gebraucht werden.
    #: Verschiedene Backends liefern verschiedene Teilmengen davon.
    KAMERAFELDER = ('cam_trans', 'processed_bbox', 'cam_focal', 'cam_princpt',
                    'input_body_shape', 'image_width', 'image_height',
                    'pred_cam', 'bbox_cxcywh', 'bbox_scale',
                    'focal_length', 'crop_res')

    def __init__(self, roh, zuordnung, backend, foto_url, dauer):
        self.roh = roh                      # Rueckgabe des Analyse-Backends
        self.zuordnung = zuordnung          # betas -> Morph-Regler
        self.backend = roh.get('backend', backend)
        self.foto_url = foto_url
        self.dauer = round(dauer, 2)
        self.job_id = None
        self.ausrichtung = None
        self.hautfarbe = roh.get('skin_color')

    # ------------------------------------------------------------------ lesen

    @property
    def geschlecht(self):
        """Geschaetztes Geschlecht schlaegt das angefragte."""
        return self.zuordnung.get('estimated_gender') or self.roh['gender']

    @property
    def betas(self):
        return self.roh['betas']

    @property
    def koerpertyp(self):
        return self.zuordnung['body_type']

    @property
    def masse(self):
        return self.roh.get('measurements') or self.zuordnung.get('measurements')

    @property
    def kameradaten(self):
        return {f: self.roh[f] for f in self.KAMERAFELDER
                if self.roh.get(f) is not None}

    @property
    def hat_kamera(self):
        k = self.kameradaten
        return bool(k.get('cam_trans') or k.get('pred_cam'))

    # ----------------------------------------------------------------- ausgeben

    def als_dict(self):
        """Die Form, die der Browser erwartet — Feldnamen unveraendert."""
        d = {
            'ok': True,
            'gender': self.geschlecht,
            'betas': self.betas,
            'body_type': self.koerpertyp,
            'meta_sliders': self.zuordnung['meta_sliders'],
            'morphs': self.zuordnung['morphs'],
            'confidence': self.roh['confidence'],
            'mock': self.roh.get('mock', False),
            'backend': self.backend,
            'photo_url': self.foto_url,
            'duration': self.dauer,
            'bbox_xyxy': self.roh.get('bbox_xyxy'),
        }
        kamera = self.kameradaten
        if kamera:
            d['cam_data'] = kamera
        if self.zuordnung.get('estimated_gender'):
            d['estimated_gender'] = self.zuordnung['estimated_gender']
        if self.masse:
            d['measurements'] = self.masse
        if self.hautfarbe:
            d['skin_color'] = self.hautfarbe
        if self.roh.get('expression'):
            d['expression'] = self.roh['expression']
        if self.job_id:
            d['job_id'] = str(self.job_id)
        if self.ausrichtung:
            d['alignment_data'] = self.ausrichtung
        return d

    def archivdaten(self, job, dateiname, erstellt):
        """Die Felder, die neben dem Netz als JSON abgelegt werden."""
        return {
            'job_id': str(job.id),
            'betas': self.betas,
            'expression': self.roh.get('expression', []),
            'gender': self.geschlecht,
            'backend': self.backend,
            'confidence': self.roh['confidence'],
            'body_type': self.koerpertyp,
            'meta_sliders': self.zuordnung['meta_sliders'],
            'morphs': self.zuordnung['morphs'],
            'measurements': self.masse,
            'skin_color': self.hautfarbe,
            'original_filename': dateiname,
            'created_at': str(erstellt),
            'bbox_xyxy': self.roh.get('bbox_xyxy'),
            'image_width': self.roh.get('image_width'),
            'image_height': self.roh.get('image_height'),
            'cam_data': self.kameradaten or None,
        }
