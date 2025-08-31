import argparse
import logging
import os
import shutil
from collections import defaultdict

import exifread

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler()  # 输出到控制台
    ]
)
logger = logging.getLogger(__name__)

# 支持的图像格式
SUPPORTED_IMAGE_FORMATS = {
    'compressed': ['.JPG', '.JPEG', '.HEIC', '.PNG', '.WEBP'],
    'raw': ['.3FR', '.ARW', '.CR2', '.CR3', '.CRW', '.DCR', '.DNG', '.ERF', '.FFF', '.GPR', '.IIQ', '.KDC', '.MEF',
            '.MOS', '.MRW', '.NEF', '.NEFX', '.NRW', '.ORF', '.PEF', '.RAF', '.RAW', '.RW2', '.RWL', '.SRF', '.SRW',
            '.TIF', '.X3F']
}


def find_camera_drives(exclude_drives=None):
    """查找所有包含DCIM文件夹的相机存储盘符，排除指定盘符"""
    if exclude_drives is None:
        exclude_drives = []

    camera_drives = []

    # Windows系统
    for drive_letter in range(ord('C'), ord('Z') + 1):
        drive = chr(drive_letter) + ":\\"

        # 排除指定盘符
        if any(drive.upper().startswith(exclude_drive.upper()) for exclude_drive in exclude_drives):
            continue

        dcim_path = os.path.join(drive, "DCIM")
        if os.path.exists(dcim_path) and os.path.isdir(dcim_path):
            camera_drives.append(drive)

    return camera_drives


def get_exif_tags(file_path):
    """读取文件的EXIF信息（Make, Model, DateTime）"""
    try:
        with open(file_path, 'rb') as f:
            tags = exifread.process_file(f, details=False, extract_thumbnail=False)

            # 提取所需的EXIF标签
            make = str(tags.get('Image Make', ''))
            model = str(tags.get('Image Model', ''))
            datetime = str(tags.get('Image DateTime', ''))

            return make, model, datetime
    except Exception as e:
        logger.warning(f"无法读取EXIF信息 {file_path}: {e}")
        return None, None, None


def find_files_by_extension(root_dir, extensions):
    """递归查找指定扩展名的文件，返回文件名到路径列表的映射"""
    file_dict = defaultdict(list)

    for root, _, files in os.walk(root_dir):
        for file in files:
            file_ext = os.path.splitext(file)[1].upper()
            if file_ext in extensions:
                base_name = os.path.splitext(file)[0]
                file_dict[base_name].append(os.path.join(root, file))

    return file_dict


def get_user_confirmation(prompt, message=None, details=None, default_confirm=False):
    """
    获取用户确认的通用函数
    """
    # 打印主要信息
    if message:
        print(message)

    # 如果有详细信息，逐条打印
    if details:
        for item in details:
            print(item)

    # 根据默认选择设置提示信息
    prompt += "[Y/n]" if default_confirm else "[y/N]"

    while True:
        response = input(prompt).strip().lower()

        # 处理空输入（使用默认选择）
        if response == '':
            return default_confirm

        # 确认选项
        if response in ['y', 'yes', '是']:
            return True

        # 拒绝选项
        if response in ['n', 'no', '否']:
            return False

        # 无效输入
        print("输入无效，请重新输入")


def process_material_folder(folder_path, folder_files, camera_raw_files, auto_confirm=False):
    """处理单个素材文件夹"""
    copied_count = 0

    # 查找当前文件夹中的图像文件
    compressed_files = []
    raw_files = []

    for file in folder_files:
        file_ext = os.path.splitext(file)[1].upper()
        if file_ext in SUPPORTED_IMAGE_FORMATS['compressed']:
            compressed_files.append(file)
        elif file_ext in SUPPORTED_IMAGE_FORMATS['raw']:
            raw_files.append(file)

    # 获取当前文件夹中已有的RAW文件的基本名（不含扩展名）
    existing_raw_basenames = {os.path.splitext(f)[0] for f in raw_files}

    # 收集当前文件夹需要复制的文件
    files_to_copy = []
    copy_mapping = {}  # 存储目标路径和源路径的映射

    # 对于每个压缩图像文件，如果没有对应的RAW文件，则尝试从相机存储复制
    for compressed_file in compressed_files:
        compressed_basename = os.path.splitext(compressed_file)[0]

        # 如果已经有对应的RAW文件，跳过
        if compressed_basename in existing_raw_basenames:
            continue

        # 检查相机存储中是否有同名RAW文件
        if compressed_basename not in camera_raw_files:
            continue

        # 获取压缩图像文件的EXIF信息
        compressed_path = os.path.join(folder_path, compressed_file)
        compressed_make, compressed_model, compressed_datetime = get_exif_tags(compressed_path)
        if not all([compressed_make, compressed_model, compressed_datetime]):
            logger.warning(f"无法读取压缩图像文件的EXIF信息: {compressed_path}")
            continue

        # 检查相机存储中的候选RAW文件
        for raw_path in camera_raw_files[compressed_basename]:
            # 懒加载：只在需要时读取RAW文件的EXIF信息
            raw_make, raw_model, raw_datetime = get_exif_tags(raw_path)

            # 比较EXIF信息
            if (compressed_make == raw_make and
                    compressed_model == raw_model and
                    compressed_datetime == raw_datetime):
                # 确定目标路径
                target_path = os.path.join(folder_path, os.path.basename(raw_path))

                # 添加到复制列表
                files_to_copy.append(raw_path)
                copy_mapping[raw_path] = target_path
                existing_raw_basenames.add(compressed_basename)  # 更新已存在的RAW文件列表
                break  # 找到一个匹配后就跳出循环

    # 如果有文件需要复制，询问用户确认
    if files_to_copy:
        if auto_confirm or get_user_confirmation(
                '是否导入？',
                f'\n素材文件夹 {folder_path} 将导入以下RAW文件：',
                files_to_copy,
                True
        ):
            for raw_path in files_to_copy:
                try:
                    # 复制RAW文件
                    shutil.copy2(raw_path, copy_mapping[raw_path])
                    logger.info(f"已复制: {raw_path} -> {copy_mapping[raw_path]}")
                    copied_count += 1
                except Exception as e:
                    logger.error(f"复制文件失败 {raw_path}: {e}")
        else:
            logger.info(f"用户取消了文件夹 {folder_path} 的导入操作")

    return copied_count


def import_raw_photos(material_dir=None, camera_drives=None, auto_confirm=False):
    """主函数：导入RAW照片"""
    # 1. 确定素材文件夹
    if material_dir is None:
        material_dir = os.path.dirname(os.path.abspath(__file__))
    logger.info(f"素材文件夹: {material_dir}")

    # 2. 查找相机存储盘符
    if camera_drives is None:
        # 排除素材文件夹所在盘符
        material_drive = os.path.splitdrive(material_dir)[0]
        camera_drives = find_camera_drives(exclude_drives=[material_drive])
        if camera_drives:
            logger.info(f"找到相机存储: {', '.join(camera_drives)}")
        else:
            logger.error("未找到相机存储")
            return 0

    # 3. 查找所有相机存储中的RAW文件
    camera_raw_files = defaultdict(list)

    for drive in camera_drives:
        dcim_path = os.path.join(drive, "DCIM")
        # 具体的目录
        if not os.path.exists(dcim_path) or not os.path.isdir(dcim_path):
            if get_user_confirmation(f"未找到 {dcim_path}，是否使用 {drive} 继续扫描？"):
                dcim_path = drive
            else:
                logger.info(f"跳过目录 {drive}")
                continue
        logger.info(f"扫描相机存储 {drive} 中的RAW文件...")

        drive_raw_files = find_files_by_extension(dcim_path, SUPPORTED_IMAGE_FORMATS['raw'])

        # 合并到总字典中
        for base_name, paths in drive_raw_files.items():
            camera_raw_files[base_name].extend(paths)
    if not camera_raw_files:
        logger.error("未找到RAW文件")
        return 0
    logger.info(f"在所有相机存储中找到 {len(camera_raw_files)} 个RAW文件")

    # 4. 处理素材文件夹的所有子文件夹
    logger.info("开始处理素材文件夹...")
    total_copied = 0

    for root, dirs, files in os.walk(material_dir):
        # 跳过没有文件的文件夹
        if not files:
            continue

        logger.info(f"扫描文件夹: {root}")
        copied_count = process_material_folder(root, files, camera_raw_files, auto_confirm)
        total_copied += copied_count

    logger.info(f"导入结束，共复制了 {total_copied} 个RAW文件")
    return total_copied


def main():
    """主函数：解析参数并执行RAW导入"""
    parser = argparse.ArgumentParser(description='从相机存储中自动导入RAW格式照片')
    parser.add_argument('-s', '--source', nargs='+', help='相机存储路径（盘符或路径）')
    parser.add_argument('-d', '--destination', default=os.getcwd(),
                        help='素材文件夹路径，默认为当前工作目录')
    parser.add_argument('-y', '--yes', action='store_true', help='自动确认所有RAW导入')

    args = parser.parse_args()

    # 处理源路径参数，支持不带冒号的盘符
    camera_drives = []
    if args.source:
        for source in args.source:
            # 如果是不带冒号的单个字母，添加冒号和反斜杠
            if len(source) == 1 and source.isalpha():
                camera_drives.append(source.upper() + ":\\")
            else:
                camera_drives.append(source)

    # 执行RAW导入
    while True:
        import_raw_photos(
            material_dir=args.destination,
            camera_drives=camera_drives if args.source else None,
            auto_confirm=args.yes
        )

        if args.yes and not get_user_confirmation('是否再次运行？'):
            break


if __name__ == "__main__":
    main()

# pyinstaller.exe -F .\main.py -n import_photo_raw.exe
