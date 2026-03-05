/**
 * VideoExporter — record the Three.js canvas to WebM via MediaRecorder.
 */
export class VideoExporter {
    constructor(canvas) {
        this._canvas = canvas;
        this._recorder = null;
        this._chunks = [];
    }

    /**
     * Start recording.
     * @param {number} fps Frames per second (default 30)
     */
    start(fps = 30) {
        const stream = this._canvas.captureStream(fps);
        this._chunks = [];

        // Prefer VP9, fallback to VP8
        const mimeType = MediaRecorder.isTypeSupported('video/webm;codecs=vp9')
            ? 'video/webm;codecs=vp9'
            : 'video/webm;codecs=vp8';

        this._recorder = new MediaRecorder(stream, {
            mimeType,
            videoBitsPerSecond: 8_000_000,
        });

        this._recorder.ondataavailable = (e) => {
            if (e.data.size > 0) this._chunks.push(e.data);
        };

        this._recorder.start();
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
     * Stop recording and trigger a download.
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
}
