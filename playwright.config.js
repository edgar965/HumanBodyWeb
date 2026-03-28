module.exports = {
    testDir: '.',
    testMatch: ['test_anim_debug.js'],
    timeout: 120000,
    use: {
        headless: false,
        viewport: { width: 1920, height: 1080 },
        launchOptions: {
            executablePath: 'C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe',
        },
    },
};
