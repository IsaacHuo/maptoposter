# Android 套壳（Capacitor）

React 编辑器原样复用，Capacitor 只负责把它装进 Android WebView；后端仍是现有的 FastAPI 服务。

## 目录

- `frontend/capacitor.config.ts`：Capacitor 配置（appId `com.maptoposter.app`、`webDir: dist`）。
- `frontend/android/`：原生工程（由 `cap add android` 生成，需提交）。
- `frontend/.env.capacitor`：Android 构建使用的 API 地址。
- `frontend/android/app/src/debug/AndroidManifest.xml`：仅 debug 允许明文 HTTP。

## 准备

- Node 22+（仓库里是 pnpm 11）。
- JDK 21 与 Android SDK（`ANDROID_HOME` 或 `android/local.properties` 的 `sdk.dir`）。

## 构建

```bash
corepack pnpm --dir frontend install --frozen-lockfile
corepack pnpm --dir frontend build:android   # vite build --mode capacitor
corepack pnpm --dir frontend cap:sync        # dist -> android/app/src/main/assets/public
gradlew.bat -p frontend/android assembleDebug
```

产物：`frontend/android/app/build/outputs/apk/debug/app-debug.apk`。

## API 地址

打包后的页面 origin 是 `https://localhost`，Web 端默认的相对路径 `/api/v1` 会打到 App 内的静态资源，
所以 Android 构建必须给出绝对地址：

- 默认值（`frontend/.env.capacitor`）：`http://10.0.2.2:7860/api/v1`，对应模拟器访问宿主机的 `uv run python app.py`。
- 真机：在 `frontend/.env.capacitor.local`（已被 gitignore）里写局域网地址，例如
  `VITE_API_URL=http://192.168.1.20:7860/api/v1`，再跑一次 `build:android`。
- 漏配置时不会静默失败：`frontend/src/api.ts` 会在请求前抛出说明，提示设置 `VITE_API_URL`。

明文 HTTP 只在 debug 构建里放开（`src/debug/AndroidManifest.xml`）；release 构建保持 Android 默认，
即后端必须走 HTTPS。

## 已知缺口

- 导出下载仍走 `blob:` + `<a download>`，WebView 里不会落盘，也没有系统分享（下一步用 Filesystem/Share）。
- 图标、启动图仍是 Capacitor 默认素材（路线图第 5 步）。
- 触摸手势、触控目标尺寸、横屏安全区留到第 5 步打磨。
