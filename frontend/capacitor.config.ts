import type { CapacitorConfig } from '@capacitor/cli'

// Android shell for the existing React editor. The web app keeps working as-is;
// `pnpm build:android` + `pnpm cap:sync` only produce the packaged WebView bundle.
const config: CapacitorConfig = {
  appId: 'com.maptoposter.app',
  appName: 'MapToPoster',
  webDir: 'dist',
  server: {
    androidScheme: 'https',
  },
}

export default config
