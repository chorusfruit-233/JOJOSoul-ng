# 应用图标

此目录用于存放不同平台的图标文件。

## 需要的图标文件

### Linux
- `josoul.png` - PNG 格式图标（建议 256x256 或 512x512 像素）

### macOS
- `josoul.icns` - macOS 图标格式（可以使用 iconutil 从 PNG 转换）

### Windows
- `josoul.ico` - Windows 图标格式（可以使用 ImageMagick 或在线工具转换）

## 生成图标

### 从 SVG 生成各平台图标

如果你有一个 SVG 源文件，可以使用以下工具生成各平台图标：

```bash
# 生成 PNG (Linux)
inkscape --export-type=png --export-filename=josoul.png josoul.svg

# 生成 ICO (Windows)
convert josoul.png josoul.ico

# 生成 ICNS (macOS)
mkdir josoul.iconset
sips -z 16 16     josoul.png --out josoul.iconset/icon_16x16.png
sips -z 32 32     josoul.png --out josoul.iconset/icon_16x16@2x.png
sips -z 32 32     josoul.png --out josoul.iconset/icon_32x32.png
sips -z 64 64     josoul.png --out josoul.iconset/icon_32x32@2x.png
sips -z 128 128   josoul.png --out josoul.iconset/icon_128x128.png
sips -z 256 256   josoul.png --out josoul.iconset/icon_128x128@2x.png
sips -z 256 256   josoul.png --out josoul.iconset/icon_256x256.png
sips -z 512 512   josoul.png --out josoul.iconset/icon_256x256@2x.png
sips -z 512 512   josoul.png --out josoul.iconset/icon_512x512.png
sips -z 1024 1024 josoul.png --out josoul.iconset/icon_512x512@2x.png
iconutil -c icns josoul.iconset
```

### 在线工具
- https://icoconvert.com/ - 转换 ICO 和 ICNS
- https://cloudconvert.com/ - 各种格式转换