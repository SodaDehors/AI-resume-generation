/* ============================================================
   API Helper - AJAX communication with Flask backend
   ============================================================ */

const API = {
    /**
     * Save form step data to server session.
     */
    async saveStep(step, fields) {
        const resp = await fetch('/api/save-step', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ step, fields }),
        });
        return resp.json();
    },

    /**
     * Trigger full resume generation.
     * @param {AbortSignal} signal — optional abort signal for cancellation
     */
    async generateResume(signal = null) {
        const resp = await fetch('/api/generate', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            signal,
        });
        return resp.json();
    },

    /**
     * Generate a single resume section.
     */
    async generateSection(section, data = {}) {
        const resp = await fetch(`/api/generate-section/${section}`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data),
        });
        return resp.json();
    },

    /**
     * Validate an API key.
     */
    async validateKey(provider, apiKey) {
        const resp = await fetch('/api/validate-key', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ provider, api_key: apiKey }),
        });
        return resp.json();
    },

    /**
     * Save AI provider settings.
     */
    async setProvider(provider, apiKey) {
        const resp = await fetch('/api/set-provider', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ provider, api_key: apiKey }),
        });
        return resp.json();
    },

    /**
     * Get generation status (for polling).
     */
    async getStatus() {
        const resp = await fetch('/api/status');
        return resp.json();
    },

    /**
     * Parse a self-introduction text into structured resume fields.
     * @param {string} text - The raw self-introduction text
     */
    async parseIntro(text) {
        const resp = await fetch('/api/parse-intro', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ text }),
        });
        return resp.json();
    },

    /**
     * One-shot: parse self-intro text AND generate full resume.
     * Skips the wizard entirely — straight to preview.
     * @param {string} text - The raw self-introduction text
     */
    async quickGenerate(text) {
        const resp = await fetch('/api/quick-generate', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ text }),
        });
        return resp.json();
    },
};
