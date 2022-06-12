#!/usr/bin/env python
# -*- coding: utf-8 -*-

import hashlib
import os
import shutil
from ctypes import CDLL, POINTER, byref, c_ubyte

from PySide6.QtCore import QThread, Signal


class Process(QThread):
    logPrint = Signal(str)

    EXCLUDES = ('THUMB', 'CACHE', 'CUSTOMEMOTION', 'FAV', 'GENERAL', 'SNS', 'TEMP', 'TEMPFROMPHONE')  # 排除的文件夹名
    EXTHEADER = {  # 文件类型头部数据
        (0x00, 0x00, 0x00): '.mp4',
        (0x89, 0x50, 0x4e): '.png',
        (0x47, 0x49, 0x46): '.gif',
        (0xff, 0xd8, 0xff): '.jpg',
    }

    def __init__(self, parent,
                 args: list[str],  # 文件夹或文件路径
                 target: str,  # 目标文件夹
                 image: bool = True,  # 是否整理图片
                 video: bool = True,  # 是否整理视频
                 document: bool = True,  # 是否整理文件
                 remove: bool = False,  # 整理后删除源文件
                 source: str = '',
                 ):
        super(Process, self).__init__(parent)

        self.args = args
        self.target = target
        self.image = image
        self.video = video
        self.document = document
        self.remove = remove

        self.dll = CDLL(f'{source}/decrypt')

        self.hash_table: set[str] = set()
        self.state_count: dict[str, int] = dict()
        self.pending_files: set[str] = set()
        self.pending_folders: set[str] = set()

    # QThead启动
    def run(self):
        self.init_count()
        self.init_pending()
        self.process_start()
        self.clear_empty()

        length = len(str(len(self.pending_files)))
        # noinspection PyUnresolvedReferences
        self.logPrint.emit(
            f"""
文件整理
总文件数: {self.state_count['All']:>{length}d}个
整理文件: {self.state_count['Done']:>{length}d}个
视频预览: {self.state_count['Thumb']:>{length}d}个
无法识别: {self.state_count['Failed']:>{length}d}个
空文件夹: {self.state_count['Empty']:>{length}d}个
.nomedia: {self.state_count['Nomedia']:>{length}d}个
""")

    # 计数器初始化
    def init_count(self):
        self.state_count['All'] = 0
        self.state_count['Done'] = 0
        self.state_count['Thumb'] = 0
        self.state_count['Failed'] = 0
        self.state_count['Empty'] = 0
        self.state_count['Nomedia'] = 0

    # 初始化待整理文件列表
    def init_pending(self) -> None:
        # noinspection PyUnresolvedReferences
        self.logPrint.emit('分析待整理文件...')
        for arg in self.args:
            # 参数为文件夹
            path = arg.strip('"')
            if os.path.isdir(path):
                for folder_path, _, files in os.walk(path):
                    if self.check_exclude(folder_path):
                        continue
                    self.pending_folders.add(folder_path)
                    for file_path in files:
                        file = os.path.join(folder_path, file_path)
                        self.pending_files.add(file)
                        self.state_count['All'] += 1
            # 参数为文件
            elif os.path.isfile(path):
                self.pending_files.add(path)
                self.state_count['All'] += 1

    # 检查是否为排除文件夹
    def check_exclude(self, folder_path: str) -> bool:
        for exclude in self.EXCLUDES:
            if exclude in folder_path.upper():
                return True
        return False

    # 按序处理文件
    def process_start(self):
        for fid, file_path in enumerate(self.pending_files):
            # 获取文件路径、名称、后缀名
            file_folder, file_name = os.path.split(file_path)
            name, ext = os.path.splitext(file_name)

            length = len(str(len(self.pending_files)))
            # noinspection PyUnresolvedReferences
            self.logPrint.emit(f'进度[{fid + 1:>{length}d}/{len(self.pending_files):>{length}d}] {file_name}')

            # 处理.nomedia
            if file_name == '.nomedia':
                os.remove(file_path)
                self.state_count['Nomedia'] += 1
                continue

            # 如果文件已经移除
            if not os.path.exists(file_path):
                self.state_count['Done'] += 1
                continue

            # 无后缀名时猜测文件类型
            if not ext:
                ext = self.guess_ext(file_path)
                if ext is None:
                    self.state_count['Failed'] += 1
                    continue

            # 按需整理各类文件
            target = os.path.join(self.target, ext.lstrip('.'), name)
            if ext == '.dat' and self.image:
                result = self.process_dat(file_path, target)
            elif ext in ('.png', '.gif', '.jpg') and self.image:
                result = self.process_image(file_path, target + ext)
            elif ext == '.mp4' and self.video:
                result = self.process_video(file_path, target + ext)
            elif self.document:
                result = self.process_file(file_path, target + ext)
            else:
                result = False

            self.state_count['Done'] += result

    # 处理图片加密后的DAT文件
    def process_dat(self, file_path: str, target: str) -> bool:
        # 获取原始数据
        with open(file_path, 'rb') as dat:
            buffer = dat.read()

        # 解密DAT
        ext, xor = self.decrypt_dat(tuple(buffer[:3]))
        if not ext:
            self.state_count['Failed'] += 1
            return False

        # C数据交互
        length = len(buffer)
        c_buffer = (c_ubyte * length)(*buffer)
        self.dll.iter_xor.restype = POINTER(c_ubyte)
        p_buffer = bytes(self.dll.iter_xor(byref(c_buffer), length, xor)[:length])

        # 检测MD5是否已经存在
        md5 = hashlib.md5(p_buffer).hexdigest()
        if md5 in self.hash_table:
            if self.remove:
                os.remove(file_path)
            return False

        # 目标文件夹建立及重名时处理
        target_path = target.replace('dat\\', f'{ext.lstrip(".")}\\') + ext
        target_folder = os.path.split(target_path)[0]
        if not os.path.exists(target_folder):
            os.mkdir(target_folder)
        while os.path.exists(target_path):
            target_path = self.new_target(target_path)

        # 写入解密后图片数据将MD5加入hash表并计数
        with open(target_path, 'wb') as img:
            img.write(p_buffer)
        self.hash_table.add(md5)
        self.type_count(target_path)

        if self.remove:
            os.remove(file_path)
        return True

    # 按文件类型计数
    def type_count(self, target_path: str):
        if (f_type := os.path.splitext(target_path)[-1].lstrip('.')) in self.state_count:
            self.state_count[f_type] += 1
        else:
            self.state_count[f_type] = 1

    # 解密DAT图片格式和XOR码
    def decrypt_dat(self, header: tuple):
        for h, ext in self.EXTHEADER.items():
            xor = tuple(map(lambda x, y: x ^ y, h, header))
            if xor.count(xor[0]) == len(xor):
                return ext, xor[0]
        return None, None

    # 处理普通图片文件
    def process_image(self, file_path: str, target_path: str) -> bool:
        # 检测是否为视频缩略图
        file, ext = os.path.splitext(file_path)
        if os.path.exists(file + '.mp4'):
            with open(file_path, 'rb') as f:
                md5 = hashlib.md5(f.read()).hexdigest()
            if self.remove:
                os.remove(file_path)
            if md5 in self.hash_table:
                return False
            self.hash_table.add(md5)
            self.state_count['Thumb'] += 1
            return False

        return self.process_file(file_path, target_path)

    # 处理视频文件
    def process_video(self, file_path: str, target_path: str) -> bool:
        # 检测是否有视频缩略图
        file, ext = os.path.splitext(file_path)

        if os.path.exists(file + '.png'):
            with open(file + '.png', 'rb') as f:
                md5 = hashlib.md5(f.read()).hexdigest()
            if self.remove:
                os.remove(file + '.png')
            if md5 not in self.hash_table:
                self.hash_table.add(md5)
                self.state_count['Thumb'] += 1

        if os.path.exists(file + '.jpg'):
            with open(file + '.jpg', 'rb') as f:
                md5 = hashlib.md5(f.read()).hexdigest()
            if self.remove:
                os.remove(file + '.jpg')
            if md5 not in self.hash_table:
                self.hash_table.add(md5)
                self.state_count['Thumb'] += 1

        return self.process_file(file_path, target_path)

    # 处理普通文件
    def process_file(self, file_path: str, target_path: str) -> bool:
        # 检测MD5是否已经存在
        with open(file_path, 'rb') as f:
            md5 = hashlib.md5(f.read()).hexdigest()
        if md5 in self.hash_table:
            if self.remove:
                os.remove(file_path)
            return False
        # 目标文件夹建立及重名时处理
        target_folder = os.path.split(target_path)[0]
        if not os.path.exists(target_folder):
            os.mkdir(target_folder)
        while os.path.exists(target_path):
            target_path = self.new_target(target_path)
        # 移动文件将MD5加入hash表并计数
        if self.remove:
            shutil.move(file_path, target_path)
        else:
            shutil.copy(file_path, target_path)
        self.hash_table.add(md5)
        self.type_count(target_path)
        return True

    # 目标文件已存在时调整目标文件名
    @staticmethod
    def new_target(path: str) -> str:
        f, ext = os.path.splitext(path)
        return f + '_' + ext

    # 判断无后缀名文件真实类型
    def guess_ext(self, file_path: str) -> str:
        with open(file_path, 'rb') as f:
            header = tuple(f.read(3))
        return self.EXTHEADER.get(header, None)

    # 清理空文件夹
    def clear_empty(self) -> bool:
        # noinspection PyUnresolvedReferences
        self.logPrint.emit('清理空文件夹...')
        for folder in self.pending_folders:
            child_list = [r for r, d, f in os.walk(folder)][::-1]
            for child in child_list:
                if not os.listdir(child):
                    try:
                        os.rmdir(child)
                        self.state_count['Empty'] += 1
                    except PermissionError:
                        pass
        return True
