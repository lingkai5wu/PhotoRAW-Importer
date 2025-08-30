# PhotoRAW Importer

RAW照片导入工具，从相机存储中匹配并导入与素材对应的RAW文件。

## 使用场景

摄影后期工作流程中，摄影师通常先筛选JPG，然后将满意的RAW复制到素材文件夹。本工具匹配压缩格式图片，并导入对应的原始RAW文件，极大提升素材整理效率。

## 核心功能

- 🔍 自动检测所有连接的相机存储设备
- 📁 智能匹配压缩格式图片和对应的RAW文件
- ⚡ 基于EXIF元数据精确验证文件匹配关系
- ✅ 支持交互式确认与全自动批量导入模式
- 🖼️ 广泛支持CR2、NEF、ARW等主流RAW格式及JPG/HEIC压缩格式
- 🔄 灵活指定源设备与目标素材文件夹

## 支持的格式

### 压缩格式

- JPG, JPEG
- HEIC
- PNG
- WEBP

### RAW格式

所有[Adobe Camera Raw支持的相机型号](https://helpx.adobe.com/cn/camera-raw/kb/camera-raw-plug-supported-cameras.html)对应的
**原始图像文件扩展名**。

## 运行方式

### 方式一：使用Python直接运行（需要Python环境）

#### 运行要求

- Python 3.7 至 3.13
- [exifread](https://pypi.org/project/ExifRead/) 库

#### 安装依赖

```bash
pip install exifread
```

#### 使用方法

```bash
python main.py [选项]
```

### 方式二：使用编译后的可执行文件（无需Python环境）

直接运行下载的 `import_photo_raw.exe` 文件：

```bash
import_photo_raw.exe [选项]
```

## 使用说明

### 基本用法

```bash
# 使用Python
python main.py

# 使用可执行文件
import_photo_raw.exe
```

这将自动扫描所有连接的相机存储（除了当前工作目录所在的驱动器），并在当前目录及其子目录中查找需要导入RAW文件的素材文件夹。

### 指定源和目标

```bash
# 使用Python
python main.py -s D E -d /path/to/photos

# 使用可执行文件
import_photo_raw.exe -s D E -d /path/to/photos
```

从`D:`和`E:`驱动器导入RAW文件到指定的照片目录。

### 自动确认模式

```bash
# 使用Python
python main.py -y

# 使用可执行文件
import_photo_raw.exe -y
```

自动确认所有导入操作，无需用户交互。

### 完整参数说明

```
usage: program [-h] [-s SOURCE [SOURCE ...]] [-d DESTINATION] [-y]

从相机存储中自动导入RAW格式照片

options:
  -h, --help            显示帮助信息
  -s SOURCE [SOURCE ...], --source SOURCE [SOURCE ...]
                        相机存储路径（盘符或路径）
  -d DESTINATION, --destination DESTINATION
                        素材文件夹路径，默认为当前工作目录
  -y, --yes             自动确认所有RAW导入
```

注意：将"program"替换为`python main.py`（使用Python时）或`import_photo_raw.exe`（使用可执行文件时）

## 工作原理

1. **检测相机存储**：扫描所有驱动器，查找包含DCIM文件夹的驱动器，也可手动指定路径
2. **索引RAW文件**：在相机存储中递归查找所有支持的RAW格式文件
3. **处理素材文件夹**：遍历目标目录及其子目录，查找压缩格式图片
4. **匹配文件**：对于每个压缩图片，查找同名RAW文件并验证EXIF信息（相机型号、拍摄时间）
5. **用户确认**：显示将要导入的文件并请求用户确认
6. **复制文件**：将匹配的RAW文件复制到素材文件夹中

## 注意事项

- 确保相机存储已正确连接并可访问
- 程序需要读取文件的EXIF信息，请确保有相应权限
- 在自动确认模式下使用需谨慎，建议先测试确认匹配逻辑正确

## 贡献

欢迎提交Issue和Pull Request来改进这个项目。

## 许可证

MIT License