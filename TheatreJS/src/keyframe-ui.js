/**
 * Simple Keyframe UI for Camera/Light Animation
 * Uses Theatre.js Core API without Studio UI
 */

export class KeyframeUI {
    constructor(project, sheet, objects) {
        this.project = project;
        this.sheet = sheet;
        this.objects = objects; // { Camera: theatreObj, 'Spot Left': theatreObj, ... }
        this.keyframes = []; // { time, objectName, values }
        this.isPlaying = false;
        this.currentTime = 0;
        this.duration = 10; // Default 10 seconds

        this.setupUI();
        this.setupSequence();
    }

    setupUI() {
        // Create Keyframe panel in right sidebar
        const tabPane = document.getElementById('tab-keyframes');
        if (!tabPane) {
            console.error('Keyframe tab pane not found');
            return;
        }

        tabPane.innerHTML = `
            <div class="keyframe-panel">
                <div class="kf-controls">
                    <h3 style="margin: 0 0 12px 0; font-size: 0.9rem; color: #aaa;">Animation Timeline</h3>

                    <div style="display: flex; gap: 8px; margin-bottom: 12px;">
                        <button id="kf-play" class="btn-secondary" style="flex: 1;">
                            <i class="fas fa-play"></i> Play
                        </button>
                        <button id="kf-stop" class="btn-secondary" style="flex: 1;">
                            <i class="fas fa-stop"></i> Stop
                        </button>
                    </div>

                    <div style="margin-bottom: 12px;">
                        <label style="font-size: 0.75rem; color: #888;">Duration (seconds)</label>
                        <input type="number" id="kf-duration" value="10" min="1" max="300"
                               style="width: 100%; padding: 6px; background: rgba(0,0,0,0.3); border: 1px solid rgba(255,255,255,0.1); color: #fff; border-radius: 4px;">
                    </div>

                    <div style="margin-bottom: 12px;">
                        <label style="font-size: 0.75rem; color: #888;">Current Time: <span id="kf-time-display">0.00s</span></label>
                        <input type="range" id="kf-timeline" min="0" max="10" step="0.1" value="0"
                               style="width: 100%; margin-top: 4px;">
                    </div>

                    <div style="margin-bottom: 16px; padding-top: 12px; border-top: 1px solid rgba(255,255,255,0.1);">
                        <label style="font-size: 0.75rem; color: #888; display: block; margin-bottom: 8px;">Add Keyframe</label>
                        <select id="kf-object-select" style="width: 100%; padding: 6px; background: rgba(0,0,0,0.3); border: 1px solid rgba(255,255,255,0.1); color: #fff; border-radius: 4px; margin-bottom: 8px;">
                            ${Object.keys(this.objects).map(name => `<option value="${name}">${name}</option>`).join('')}
                        </select>
                        <button id="kf-add" class="btn-primary" style="width: 100%;">
                            <i class="fas fa-plus"></i> Add Keyframe at Current Time
                        </button>
                    </div>
                </div>

                <div class="kf-list">
                    <h4 style="margin: 0 0 8px 0; font-size: 0.8rem; color: #888;">Keyframes</h4>
                    <div id="kf-keyframes" style="max-height: 300px; overflow-y: auto;">
                        <div style="color: #666; font-size: 0.75rem; padding: 12px; text-align: center;">
                            No keyframes yet. Add one to start animating!
                        </div>
                    </div>
                </div>

                <div style="margin-top: 16px; padding-top: 16px; border-top: 1px solid rgba(255,255,255,0.1); display: flex; gap: 8px;">
                    <button id="kf-export" class="btn-secondary" style="flex: 1; font-size: 0.75rem;">
                        <i class="fas fa-download"></i> Export
                    </button>
                    <button id="kf-import" class="btn-secondary" style="flex: 1; font-size: 0.75rem;">
                        <i class="fas fa-upload"></i> Import
                    </button>
                    <button id="kf-clear" class="btn-secondary" style="flex: 1; font-size: 0.75rem;">
                        <i class="fas fa-trash"></i> Clear
                    </button>
                </div>
            </div>
        `;

        this.attachEventListeners();
    }

    setupSequence() {
        this.sequence = this.sheet.sequence;
    }

    attachEventListeners() {
        // Play/Stop controls
        document.getElementById('kf-play').addEventListener('click', () => this.play());
        document.getElementById('kf-stop').addEventListener('click', () => this.stop());

        // Duration change
        document.getElementById('kf-duration').addEventListener('change', (e) => {
            this.duration = parseFloat(e.target.value);
            document.getElementById('kf-timeline').max = this.duration;
        });

        // Timeline scrubbing
        const timeline = document.getElementById('kf-timeline');
        timeline.addEventListener('input', (e) => {
            this.currentTime = parseFloat(e.target.value);
            this.sequence.position = this.currentTime;
            this.updateTimeDisplay();
        });

        // Add keyframe
        document.getElementById('kf-add').addEventListener('click', () => this.addKeyframe());

        // Export/Import/Clear
        document.getElementById('kf-export').addEventListener('click', () => this.exportKeyframes());
        document.getElementById('kf-import').addEventListener('click', () => this.importKeyframes());
        document.getElementById('kf-clear').addEventListener('click', () => this.clearKeyframes());
    }

    addKeyframe() {
        const objectName = document.getElementById('kf-object-select').value;
        const theatreObj = this.objects[objectName];
        if (!theatreObj) return;

        // Get current values from Theatre.js object
        const values = theatreObj.value;

        // Store keyframe
        const keyframe = {
            id: Date.now(),
            time: this.currentTime,
            objectName: objectName,
            values: JSON.parse(JSON.stringify(values)) // Deep copy
        };

        this.keyframes.push(keyframe);
        this.keyframes.sort((a, b) => a.time - b.time);

        // Update Theatre.js sequence with keyframe
        this.applyKeyframesToSequence();
        this.renderKeyframeList();

        console.log(`✓ Keyframe added for ${objectName} at ${this.currentTime.toFixed(2)}s`, values);
    }

    applyKeyframesToSequence() {
        // Group keyframes by object
        const byObject = {};
        for (const kf of this.keyframes) {
            if (!byObject[kf.objectName]) byObject[kf.objectName] = [];
            byObject[kf.objectName].push(kf);
        }

        // Apply to each object's track
        for (const [objName, kfList] of Object.entries(byObject)) {
            const theatreObj = this.objects[objName];
            if (!theatreObj) continue;

            // Theatre.js uses sequence.position to set keyframes
            for (const kf of kfList) {
                this.sequence.position = kf.time;
                // Set values at this position
                for (const [key, value] of Object.entries(kf.values)) {
                    if (typeof value === 'object' && !Array.isArray(value)) {
                        // Compound prop (position, rotation, etc.)
                        for (const [subKey, subValue] of Object.entries(value)) {
                            theatreObj.props[key][subKey].setValue(subValue);
                        }
                    } else {
                        theatreObj.props[key].setValue(value);
                    }
                }
            }
        }

        // Return to current time
        this.sequence.position = this.currentTime;
    }

    renderKeyframeList() {
        const container = document.getElementById('kf-keyframes');
        if (this.keyframes.length === 0) {
            container.innerHTML = '<div style="color: #666; font-size: 0.75rem; padding: 12px; text-align: center;">No keyframes yet</div>';
            return;
        }

        container.innerHTML = this.keyframes.map(kf => `
            <div class="kf-item" data-id="${kf.id}" style="padding: 8px; margin-bottom: 4px; background: rgba(255,255,255,0.05); border-radius: 4px; font-size: 0.75rem; display: flex; justify-content: space-between; align-items: center;">
                <div>
                    <div style="color: #aaa; font-weight: 500;">${kf.objectName}</div>
                    <div style="color: #666; font-size: 0.7rem;">${kf.time.toFixed(2)}s</div>
                </div>
                <button class="kf-delete" data-id="${kf.id}" style="background: rgba(231, 76, 60, 0.2); border: none; color: #e74c3c; padding: 4px 8px; border-radius: 3px; cursor: pointer; font-size: 0.7rem;">
                    <i class="fas fa-trash"></i>
                </button>
            </div>
        `).join('');

        // Attach delete handlers
        container.querySelectorAll('.kf-delete').forEach(btn => {
            btn.addEventListener('click', (e) => {
                const id = parseInt(e.currentTarget.dataset.id);
                this.deleteKeyframe(id);
            });
        });
    }

    deleteKeyframe(id) {
        this.keyframes = this.keyframes.filter(kf => kf.id !== id);
        this.applyKeyframesToSequence();
        this.renderKeyframeList();
    }

    clearKeyframes() {
        this.keyframes = [];
        this.renderKeyframeList();
        // Trigger the Tools > Timeline löschen menu action
        const btn = document.getElementById('menu-tracks-clear');
        if (btn) btn.click();
    }

    play() {
        if (this.isPlaying) return;
        this.isPlaying = true;

        const playBtn = document.getElementById('kf-play');
        playBtn.innerHTML = '<i class="fas fa-pause"></i> Pause';
        playBtn.onclick = () => this.pause();

        // Use Theatre.js sequence play
        this.sequence.play({ range: [0, this.duration], rate: 1 });

        // Update UI in sync
        this.playLoop();
    }

    pause() {
        this.isPlaying = false;
        const playBtn = document.getElementById('kf-play');
        playBtn.innerHTML = '<i class="fas fa-play"></i> Play';
        playBtn.onclick = () => this.play();
    }

    stop() {
        this.isPlaying = false;
        this.currentTime = 0;
        this.sequence.position = 0;
        document.getElementById('kf-timeline').value = 0;
        this.updateTimeDisplay();

        const playBtn = document.getElementById('kf-play');
        playBtn.innerHTML = '<i class="fas fa-play"></i> Play';
        playBtn.onclick = () => this.play();
    }

    playLoop() {
        if (!this.isPlaying) return;

        this.currentTime = this.sequence.position;
        if (this.currentTime >= this.duration) {
            this.stop();
            return;
        }

        document.getElementById('kf-timeline').value = this.currentTime;
        this.updateTimeDisplay();

        requestAnimationFrame(() => this.playLoop());
    }

    updateTimeDisplay() {
        document.getElementById('kf-time-display').textContent = this.currentTime.toFixed(2) + 's';
    }

    exportKeyframes() {
        const data = {
            duration: this.duration,
            keyframes: this.keyframes
        };
        const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = 'theatre_keyframes.json';
        a.click();
        console.log('✓ Keyframes exported');
    }

    importKeyframes() {
        const input = document.createElement('input');
        input.type = 'file';
        input.accept = '.json';
        input.onchange = (e) => {
            const file = e.target.files[0];
            const reader = new FileReader();
            reader.onload = (ev) => {
                try {
                    const data = JSON.parse(ev.target.result);
                    this.keyframes = data.keyframes || [];
                    this.duration = data.duration || 10;
                    document.getElementById('kf-duration').value = this.duration;
                    document.getElementById('kf-timeline').max = this.duration;
                    this.applyKeyframesToSequence();
                    this.renderKeyframeList();
                    console.log('✓ Keyframes imported:', this.keyframes.length);
                } catch (err) {
                    alert('Import failed: ' + err.message);
                }
            };
            reader.readAsText(file);
        };
        input.click();
    }
}
