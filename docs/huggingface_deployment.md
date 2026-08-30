# Hugging Face 部署与维护 / Deployment and operations

## 中文

### 部署结构

- GitHub 仓库 `IsaacHuo/maptoposter` 的 `main` 是唯一源码来源。
- `.github/workflows/publish-hugging-face.yml` 先运行 Python、前端和 Docker 检查。
- 所有检查通过后，官方 `huggingface/hub-sync` Action 将文件镜像到 `isaachwf/MapToPoster`。
- Hugging Face 根据 README 元数据以 Docker SDK 构建，并暴露容器的 7860 端口。

`hub-sync` 是文件镜像而不是 Git 强推。它会同步删除 GitHub 已移除的文件，同时排除 `.git/` 和 `.github/`，因此两个仓库不需要共享 Git 历史。

### 首次配置凭据

1. 打开 <https://huggingface.co/settings/tokens>。
2. 创建一个单独的 fine-grained Token，只授予 `isaachwf/MapToPoster` 写权限。
3. 打开 GitHub 仓库的 **Settings → Secrets and variables → Actions**。
4. 新建 Repository Secret，名称必须是 `HF_TOKEN`，值为刚创建的 Token。
5. 不要把 Token 写入代码、`.env`、提交记录、Issue 或聊天消息。

Token 只用于 GitHub Actions 发布。删除或轮换 Token 后，应立即更新同名 GitHub Secret。

### 发布

正常发布只需要将已验证的提交推送到 GitHub `main`：

```bash
git push origin main
```

工作流的 `validate` job 失败时，`publish` job 不会运行，线上 Space 保持原版本。工作流也支持在 GitHub Actions 页面手动运行。

### 环境和存储

容器默认使用：

```text
MAPTOPOSTER_CACHE_DIR=/data/cache
MAPTOPOSTER_OUTPUT_DIR=/data/posters
MPLCONFIGDIR=/tmp/matplotlib
```

CPU Basic 的磁盘是临时磁盘。Factory reboot、重新部署或平台重启可能清除 `/data`。当前应用只把可重新生成的 OSM/地理编码缓存放在那里，因此无需数据迁移。

### 验证

发布完成后检查：

1. Space 设置仍显示 `cpu-basic`，运行阶段为 `RUNNING`，SDK 为 Docker。
2. `GET https://isaachwf-maptoposter.hf.space/api/v1/health` 返回 `status: ok`。
3. 首页加载 React 编辑器，样式缩略图和交互地图正常。
4. 搜索“北京”，用小范围视口完成地图准备和预览。
5. 分别下载 PNG、SVG 和 PDF，确认文件非空且 Content-Type 正确。

### 回滚

GitHub `main` 是源码真相，不直接修改 Space 仓库进行长期修复。

1. 使用 `git revert <bad-commit>` 创建回滚提交，不重写 `main` 历史。
2. 在本地运行完整检查。
3. 将回滚提交推送到 `main`，等待自动镜像完成。

如果 Space 构建失败，旧容器通常仍会保留或显示构建错误。不要删除或重新创建 Space；先从构建日志修复 Docker 问题，再推送修复提交。

## English

### Deployment model

GitHub `IsaacHuo/maptoposter` `main` is the single source of truth. The publish workflow validates Python, the frontend, and the Linux container before the official `huggingface/hub-sync` Action mirrors repository files to `isaachwf/MapToPoster`. Hugging Face then builds the Docker Space and exposes port 7860.

The sync action mirrors files rather than force-pushing Git history. It propagates deletions and excludes `.git/` and `.github/`, so the GitHub repository and Space can retain independent histories.

### One-time credentials

Create a fine-grained token at <https://huggingface.co/settings/tokens> with write access limited to `isaachwf/MapToPoster`. Save it as a GitHub Actions repository secret named `HF_TOKEN`. Never store the token in source files, environment files, commits, issues, or chat messages.

### Release and rollback

A push to GitHub `main` starts validation and publishes only after every check succeeds. To roll back, revert the faulty GitHub commit and push the revert to `main`; do not rewrite `main` or maintain a manual fork of the Space source.

Free CPU Basic storage is ephemeral. `/data/cache` and `/data/posters` contain only reproducible runtime files and may be cleared during rebuilds or restarts.
