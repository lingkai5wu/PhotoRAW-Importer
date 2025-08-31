# PhotoRAW Importer

RAW照片导入工具，从相机存储中匹配并导入与素材对应的RAW文件。

## 应用场景

专为摄影后期工作流程设计。摄影师通常先筛选 JPEG/HEIC 格式预览图，然后将选中的 RAW 原始文件复制至素材文件夹。本工具匹配压缩格式图片并自动导入对应RAW文件，显著提升素材整理效率。

## 核心功能

- 🔍 自动识别所有已连接的相机存储设备
- 📁 智能匹配压缩格式图片与对应 RAW 文件
- ⚡ 基于 EXIF 元数据进行精准匹配验证
- ✅ 提供交互式确认与全自动导入双模式
- 🖼️ 全面支持 CR2、NEF、ARW 等主流 RAW 格式及 JPEG/HEIC 压缩格式
- 🔄 可灵活指定源设备与目标素材文件夹路径

## 支持格式

### 压缩格式

- JPG/JPEG
- HEIC
- PNG
- WEBP

### RAW 格式

支持所有 [Adobe Camera Raw 兼容相机型号](https://helpx.adobe.com/cn/camera-raw/kb/camera-raw-plug-supported-cameras.html)的原始图像文件格式。

## 使用指南

1. 从 [Releases](https://github.com/lingkai5wu/PhotoRAW-Importer/releases/latest) 下载最新版本的可执行文件，放置于素材文件夹根目录
2. 创建子文件夹（如：250831_XX公园）
3. 连接相机或将存储卡插入计算机
4. 将所有 JPEG/HEIC 等非 RAW 图像复制至子文件夹
5. 删除不需要的压缩格式图片（选片）
6. 运行本工具，自动导入匹配的 RAW 文件

## 运行方法

### 方法一：Python 环境运行

#### 环境要求

- Python 3.7 - 3.13
- [exifread](https://pypi.org/project/ExifRead/) 库

#### 安装依赖

```bash
pip install exifread
```

#### 执行命令

```bash
python main.py [选项]
```

### 方法二：可执行文件运行

双击运行下载的 `import_photo_raw.exe`，或使用命令行：

```bash
import_photo_raw.exe [选项]
```

## 使用说明

### 基本使用

```bash
# Python 方式
python main.py

# 可执行文件方式
import_photo_raw.exe
```

程序将自动扫描所有已连接的相机存储（排除当前工作目录所在驱动器），并在当前目录及子目录中查找需导入 RAW 文件的素材文件夹。

### 指定源与目标

```bash
# Python 方式
python main.py -s D E -d /path/to/photos
python main.py -s /path/from/original -d /path/to/photos

# 可执行文件方式
import_photo_raw.exe -s D E -d /path/to/photos
import_photo_raw.exe -s /path/from/original -d /path/to/photos
```

从 `D:` 和 `E:` 驱动器导入 RAW 文件至指定目录。

### 自动确认模式

```bash
# Python 方式
python main.py -y

# 可执行文件方式
import_photo_raw.exe -y
```

自动确认所有导入操作，无需人工交互。

### 参数详情

```
usage: program [-h] [-s SOURCE [SOURCE ...]] [-d DESTINATION] [-y]

自动从相机存储导入 RAW 格式照片

options:
  -h, --help            显示帮助信息
  -s SOURCE [SOURCE ...], --source SOURCE [SOURCE ...]
                        相机存储路径（盘符或路径）
  -d DESTINATION, --destination DESTINATION
                        素材文件夹路径（默认为当前目录）
  -y, --yes             自动确认所有交互操作
```

注意：使用时请将 "program" 替换为 `python main.py`（Python 方式）或 `import_photo_raw.exe`（可执行文件方式）

## 技术原理

1. **检测相机存储**：自动扫描所有驱动器，识别包含 DCIM 文件夹的设备，支持手动指定路径
2. **索引 RAW 文件**：在相机存储中递归查找所有支持的 RAW 格式文件
3. **处理素材文件夹**：遍历目标目录及子目录，定位压缩格式图片
4. **文件匹配**：对每个压缩图片查找同名 RAW 文件，验证 EXIF 信息（相机型号、拍摄时间）
5. **用户确认**：显示待导入文件列表并请求确认
6. **文件复制**：将匹配的 RAW 文件复制至素材文件夹

## 注意事项

- 请确保相机存储设备已正确连接且可访问
- 程序需要读取文件 EXIF 信息，请确保具有相应权限
- 使用自动确认模式前请先行测试，确保匹配逻辑符合预期

## 参与贡献

欢迎提交 Issue 和 Pull Request 共同改进本项目。

## 开源许可

MIT License
