# Debian 包构建指南

本目录包含 JOJO Soul 的 Debian 包构建配置，支持 amd64 和 arm64 架构。

## 支持的架构

- **amd64**: x86_64 架构（标准 PC/服务器）
- **arm64**: ARM64 架构（树莓派 4、Apple Silicon Mac、ARM 服务器等）

## 本地构建

### 前置要求

- Docker
- Docker Compose（可选）

### 构建步骤

```bash
# 构建 amd64 包
./linux/build-deb.sh amd64

# 构建 arm64 包（需要 QEMU 支持）
./linux/build-deb.sh arm64
```

### 手动构建

```bash
# 构建 amd64
docker build -f linux/Dockerfile.amd64 -t josoul-builder:amd64 .
docker run --rm -v $PWD:/output josoul-builder:amd64

# 构建 arm64
docker build -f linux/Dockerfile.arm64 -t josoul-builder:arm64 .
docker run --rm -v $PWD:/output josoul-builder:arm64
```

## 安装

```bash
# 安装 amd64 包
sudo dpkg -i josoul_2.3.0_amd64.deb

# 安装 arm64 包
sudo dpkg -i josoul_2.3.0_armd64.deb

# 如果有依赖问题
sudo apt-get install -f
```

## 卸载

```bash
sudo dpkg -r josoul
```

## 文件位置

安装后的文件位置：

| 文件 | 位置 |
|------|------|
| 可执行文件 | `/usr/local/bin/josoul` |
| 桌面文件 | `/usr/share/applications/josoul.desktop` |
| 图标 | `/usr/share/icons/hicolor/256x256/apps/josoul.png` |
| 存档文件 | `~/.josoul/savegame.dat` |

## CI/CD 构建

GitHub Actions 会自动构建两个架构的包：

- `debian-package-amd64`
- `debian-package-arm64`

构建产物会作为 artifacts 上传，可以在 Actions 页面下载。

## ARM64 设备

### 树莓派 4

```bash
# 下载 arm64 包
wget https://github.com/your-repo/releases/download/v2.3.0/josoul_2.3.0_arm64.deb

# 安装
sudo dpkg -i josoul_2.3.0_arm64.deb
sudo apt-get install -f
```

### Apple Silicon Mac (使用 Asahi Linux)

```bash
# 下载 arm64 包
wget https://github.com/your-repo/releases/download/v2.3.0/josoul_2.3.0_arm64.deb

# 安装
sudo dpkg -i josoul_2.3.0_arm64.deb
sudo apt-get install -f
```

## 故障排除

### QEMU 未安装（构建 arm64 时）

```bash
# Ubuntu/Debian
sudo apt-get install qemu-user-static

# macOS
brew install qemu
```

### 依赖问题

```bash
sudo apt-get install -f
```

### 权限问题

```bash
sudo chmod +x /usr/local/bin/josoul
```

## 开发

### 修改构建配置

- `Dockerfile.amd64` - amd64 架构构建配置
- `Dockerfile.arm64` - arm64 架构构建配置
- `josoul.desktop` - 桌面文件配置

### 测试构建

```bash
# 测试 amd64
docker build -f linux/Dockerfile.amd64 --target builder -t josoul-builder:test .
docker run --rm -it josoul-builder:test /bin/bash

# 测试 arm64
docker build -f linux/Dockerfile.arm64 --target builder -t josoul-builder:test .
docker run --rm -it josoul-builder:test /bin/bash
```

## 参考资源

- [Debian 打包指南](https://www.debian.org/doc/manuals/debian-faq/ch-pkg_basics.html)
- [PyInstaller 文档](https://pyinstaller.org/)
- [Docker 多架构构建](https://docs.docker.com/build/building/multi-platform/)