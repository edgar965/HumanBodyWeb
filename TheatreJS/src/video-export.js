/**
 * VideoExporter — record the Three.js canvas to WebM via MediaRecorder,
 * with optional resolution override and MP4 server-side conversion.
 */
export class VideoExporter {
    constructor(canvas) {
        this._canvas = canvas;
        this._recorder = null;
        this._chunks = [];
        this._originalSize = null; // { width, height, pixelRatio }
    }

    /**
     * Start recording.
     * @param {Object} options
     * @param {number}  options.fps       Frames per second (default 30)
     * @param {number}  options.bitrate   Bits per second (default 8_000_000)
     * @param {number}  [options.width]   Export width (overrides canvas size)
     * @param {number}  [options.height]  Export height (overrides canvas size)
     * @param {Object}  [options.renderer] Three.js renderer (needed for resolution override)
     * @param {Object}  [options.camera]   Three.js camera (needed for aspect update)
     */
    start(options = {}) {
        const {
            fps = 30,
            bitrate = 8_000_000,
            width,
            height,
            renderer,
            camera,
        } = options;

        // Override renderer resolution if requested
        if (width && height && renderer) {
            this._originalSize = {
                width: renderer.domElement.width,
                height: renderer.domElement.height,
                pixelRatio: renderer.getPixelRatio(),
                style: {
                    width: renderer.domElement.style.width,
                    height: renderer.domElement.style.height,
                },
            };
            renderer.setPixelRatio(1);
            renderer.setSize(width, height, false);
            // Keep canvas DOM size unchanged (CSS) but internal buffer at export res
            renderer.domElement.style.width = this._originalSize.style.width;
            renderer.domElement.style.height = this._originalSize.style.height;

            if (camera && camera.isPerspectiveCamera) {
                camera.aspect = width / height;
                camera.updateProjectionMatrix();
            }
            this._renderer = renderer;
            this._camera = camera;
        }

        const stream = this._canvas.captureStream(fps);
        this._chunks = [];

        // Prefer VP9, fallback to VP8
        const mimeType = MediaRecorder.isTypeSupported('video/webm;codecs=vp9')
            ? 'video/webm;codecs=vp9'
            : 'video/webm;codecs=vp8';

        this._recorder = new MediaRecorder(stream, {
            mimeType,
            videoBitsPerSecond: bitrate,
        });

        this._recorder.ondataavailable = (e) => {
            if (e.data.size > 0) this._chunks.push(e.data);
        };

        this._recorder.start();
    }

    /**
     * Restore renderer to original size (if changed).
     */
    _restoreSize() {
        if (this._originalSize && this._renderer) {
            const s = this._originalSize;
            this._renderer.setPixelRatio(s.pixelRatio);
            // Restore from DOM element actual display size
            const container = this._renderer.domElement.parentElement;
            if (container) {
                this._renderer.setSize(container.clientWidth, container.clientHeight, false);
            } else {
                this._renderer.setSize(s.width / s.pixelRatio, s.height / s.pixelRatio, false);
            }
            if (this._camera && this._camera.isPerspectiveCamera) {
                const el = this._renderer.domElement;
                this._camera.aspect = el.clientWidth / el.clientHeight;
                this._camera.updateProjectionMatrix();
            }
            this._originalSize = null;
        }
    }

    /**
     * Stop recording and return the video as a Blob.
     * @returns {Promise<Blob>}
     */
    stop() {
        return new Promise((resolve) => {
            this._recorder.onstop = () => {
                const blob = new Blob(this._chunks, { type: 'video/webm' });
                this._chunks = [];
                this._restoreSize();
                resolve(blob);
            };
            this._recorder.stop();
        });
    }

    /**
     * Check if currently recording.
     */
    get isRecording() {
        return this._recorder?.state === 'recording';
    }

    /**
     * Stop recording and trigger a direct WebM download.
     * @param {string} filename
     */
    async stopAndDownload(filename = 'theatre-export.webm') {
        const blob = await this.stop();
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = filename;
        a.click();
        URL.revokeObjectURL(url);
    }

    /**
     * Stop recording, upload WebM to server for MP4 conversion, download result.
     * @param {string} uploadUrl  Server endpoint (e.g. '/api/theatre/convert-video/')
     * @param {string} filename   Output filename
     * @returns {Promise<void>}
     */
    async stopAndUpload(uploadUrl, filename = 'theatre-export.mp4') {
        const blob = await this.stop();
        const form = new FormData();
        form.append('video', blob, 'recording.webm');

        const resp = await fetch(uploadUrl, { method: 'POST', body: form });
        if (!resp.ok) {
            const err = await resp.json().catch(() => ({ error: 'Server error' }));
            throw new Error(err.error || `HTTP ${resp.status}`);
        }

        const mp4Blob = await resp.blob();
        const url = URL.createObjectURL(mp4Blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = filename;
        a.click();
        URL.revokeObjectURL(url);
    }
}
