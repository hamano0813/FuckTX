#!/usr/bin/env python
# -*- coding: utf-8 -*-

#############################################################################
#
#  Created by Hamano0813
#  用于将项目以二进制码发布的小工具
#  命令行执行输入 python release.py main.py
#  可直接将项目入口的main文件拖放到工具上执行
#
#############################################################################

import os
import py_compile
import shutil
import sys


def remove_cache(folder: str):
    for r, dirs, _ in os.walk(folder):
        [shutil.rmtree(os.path.join(r, d)) for d in dirs if d == '__pycache__']


def release_project(s_path):
    cache = '.cpython-' + sys.version[0:4].replace('.', '') + '.pyc'
    count = 0
    p_folder = os.path.split(s_path)[0]
    p_name = p_folder.split('/')[-1]

    remove_cache(p_folder)

    r_folder = p_folder.rstrip(p_name) + 'release'
    if os.path.exists(r_folder):
        shutil.rmtree(r_folder)
    os.mkdir(r_folder)

    for r, _, files in os.walk(p_folder):
        for f in files:
            f_path = os.path.join(r, f)
            if os.path.normcase(f_path) == os.path.normcase(s_path) or not f_path.endswith('.py'):
                shutil.copy(f_path, f_path.replace(p_name, 'release'))
            else:
                c_path = os.path.join(r, '__pycache__', f.replace('.py', cache))
                t_path = f_path.replace(p_name, 'release') + 'c'
                py_compile.compile(f_path)
                if os.path.exists(c_path):
                    if not os.path.exists(t_root := os.path.dirname(t_path)):
                        os.mkdir(t_root)
                    shutil.move(c_path, t_path)
                    count += 1

    print(f'转换了{count}个文件...')
    remove_cache(p_folder)


def process():
    if len(sys.argv) != 2:
        return input('必须传入1个程序入口...')

    path = sys.argv[1]
    if path.endswith('.py') or path.endswith('.pyw'):
        release_project(path)

        return print('程序发布完成...')

    return input('必须传入.py或.pyw文件作为程序入口...')


if __name__ == '__main__':
    process()
