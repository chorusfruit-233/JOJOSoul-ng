#!/bin/bash

# JOJO Soul Debian 包构建脚本
# 支持 amd64 和 arm64 架构

set -e

VERSION="2.3.0"
ARCH=${1:-amd64}

if [ "$ARCH" != "amd64" ] && [ "$ARCH" != "arm64" ]; then
    echo "错误: 不支持的架构 '$ARCH'"
    echo "用法: $0 [amd64|arm64]"
    exit 1
fi

echo "正在构建 $ARCH 架构的 Debian 包..."

# 构建镜像
echo "构建 Docker 镜像..."
docker build -f linux/Dockerfile.$ARCH -t josoul-builder:$ARCH .

# 运行容器并提取 .deb 包
echo "构建 .deb 包..."
docker run --rm -v $PWD:/output josoul-builder:$ARCH

echo "构建完成: josoul_${VERSION}_${ARCH}.deb"
echo "使用以下命令安装:"
echo "  sudo dpkg -i josoul_${VERSION}_${ARCH}.deb"