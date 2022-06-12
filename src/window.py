#!/usr/bin/env python
# -*- coding: utf-8 -*-

import ctypes.wintypes

from PySide6.QtCore import QAbstractListModel, QModelIndex
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QWidget, QGroupBox, QLineEdit, QListView, QPushButton, QCheckBox, QHBoxLayout, \
    QVBoxLayout, QFileDialog

from process import Process
from rec import *


class PathModel(QAbstractListModel):
    def __init__(self):
        super(PathModel, self).__init__(parent=None)
        self.path_list = []

    def rowCount(self, parent: QModelIndex = ...) -> int:
        return len(self.path_list)

    def data(self, index: QModelIndex, role: int = ...) -> any:
        if not index.isValid():
            return None
        if not role == QtCore.Qt.DisplayRole:
            return None
        return self.path_list[index.row()]

    def add_path(self, path: str):
        self.beginInsertRows(QModelIndex(), self.rowCount() + 1, self.rowCount() + 1)
        self.path_list.append(path)
        self.endInsertRows()

    def del_path(self, row: int):
        self.beginRemoveRows(QModelIndex(), row, row)
        self.path_list.pop(row)
        self.endRemoveRows()


class PathList(QListView):
    def __init__(self):
        super(PathList, self).__init__(parent=None)
        self.setModel(PathModel())
        self.setSelectionMode(QListView.SingleSelection)

    def add_path(self):
        buf = ctypes.create_unicode_buffer(ctypes.wintypes.MAX_PATH)
        ctypes.windll.shell32.SHGetFolderPathW(None, 5, None, 0, buf)
        path = QFileDialog.getExistingDirectory(self, "选择文件夹", buf.value)
        self.model().add_path(path)

    def del_path(self):
        row = self.currentIndex().row()
        self.model().del_path(row)

    def argv(self):
        return self.model().path_list


class Window(QWidget):
    def __init__(self, target: str, source: str):
        # noinspection PyTypeChecker
        super(Window, self).__init__(parent=None, f=QtCore.Qt.WindowCloseButtonHint)
        self.process = None
        self.source = source

        # 输入待处理列表
        input_group = QGroupBox('待处理列表')
        self.path_list = PathList()
        self.path_list.setContextMenuPolicy(QtCore.Qt.NoContextMenu)

        add_button = QPushButton('＋')
        del_button = QPushButton('－')
        add_button.setFixedSize(30, 30)
        del_button.setFixedSize(30, 30)
        add_button.setToolTip('添加')
        del_button.setToolTip('删除')

        path_button = QVBoxLayout()
        path_button.addWidget(add_button)
        path_button.addWidget(del_button)
        path_button.addStretch()

        input_layout = QHBoxLayout()
        input_layout.addWidget(self.path_list)
        input_layout.addLayout(path_button)
        input_group.setLayout(input_layout)

        # 输出目录选择
        output_group = QGroupBox('输出目录')
        self.output_line = QLineEdit()
        self.output_line.setText(target)
        self.output_line.setReadOnly(True)
        self.output_line.setContextMenuPolicy(QtCore.Qt.NoContextMenu)
        output_button = QPushButton('选择')

        output_layout = QHBoxLayout()
        output_layout.addWidget(self.output_line)
        output_layout.addWidget(output_button)
        output_group.setLayout(output_layout)

        # 设置选项
        option_group = QGroupBox('整理选项')
        self.image_check = QCheckBox('图片')
        self.video_check = QCheckBox('视频')
        self.document_check = QCheckBox('其他文件')
        self.remove_check = QCheckBox('完成后删除原文件')
        self.image_check.setChecked(True)
        self.video_check.setChecked(True)
        self.document_check.setChecked(True)
        option_layout = QHBoxLayout()
        option_layout.addWidget(self.image_check)
        option_layout.addWidget(self.video_check)
        option_layout.addWidget(self.document_check)
        option_layout.addWidget(self.remove_check)
        option_group.setLayout(option_layout)

        process_button = QPushButton('开始整理')
        process_button.setFixedHeight(50)
        bottom_layout = QHBoxLayout()
        bottom_layout.addWidget(option_group)
        bottom_layout.addStretch()
        bottom_layout.addWidget(process_button)
        bottom_layout.setContentsMargins(0, 0, 10, 0)

        # 信号槽连接
        # noinspection PyUnresolvedReferences
        add_button.clicked.connect(self.path_list.add_path)
        # noinspection PyUnresolvedReferences
        del_button.clicked.connect(self.path_list.del_path)
        # noinspection PyUnresolvedReferences
        process_button.clicked.connect(self.start_process)

        # 主界面及布局
        main_layout = QVBoxLayout()
        main_layout.addWidget(input_group)
        main_layout.addWidget(output_group)
        main_layout.addLayout(bottom_layout)
        self.setLayout(main_layout)
        self.setWindowTitle('腾讯即时通讯软件缓存清理')
        self.setWindowIcon(QIcon(":icon.ico"))
        self.setFixedSize(640, 480)

    def start_process(self):
        if self.process is not None:
            return self.process.quit()

        argv = self.path_list.argv()
        target = self.output_line.text()
        conf = self.get_options()

        self.process = Process(self, argv, target, **conf, source=self.source)
        self.process.logPrint[str].connect(print)
        self.process.start()

    def get_options(self):
        image = bool(self.image_check.isChecked())
        video = bool(self.video_check.isChecked())
        document = bool(self.document_check.isChecked())
        remove = bool(self.remove_check.isChecked())
        return {'image': image, 'video': video, 'document': document, 'remove': remove}
