import { defineConfig, devices } from '@playwright/test';

export default defineConfig({
  testDir: './src/tests/browser',
  timeout: 30000,
  webServer: {
    command: 'npm run preview -- --port 4173 --host 127.0.0.1',
    port: 4173,
    reuseExistingServer: !process.env.CI,
  },
  use: {
    channel: 'chrome',
    headless: true,
  },
  projects: [
    {
      name: 'chromium-desktop',
      use: {
        ...devices['Desktop Chrome'],
        channel: 'chrome',
      },
    },
    {
      name: 'chromium-mobile',
      use: {
        ...devices['Pixel 5'],
        channel: 'chrome',
      },
    },
  ],
});
