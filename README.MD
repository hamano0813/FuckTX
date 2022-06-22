# FuckTX 腾讯即时通讯缓存整理归档工具

[![python](https://img.shields.io/badge/Python-≥3.10-darkcyan?logo=python&style=flat&labelColor=013243)](https://www.python.org/)
[![PySide6](https://img.shields.io/badge/PySide6-6.3-darkcyan?logo=qt&style=flat&labelColor=013243)](https://doc.qt.io/qtforpython/)
[![pyinstaller](https://img.shields.io/badge/pyinstaller-5.1-darkcyan?style=flat&labelColor=013243)](https://pypi.org/project/pyinstaller/)

- [FuckTX 腾讯即时通讯缓存整理归档工具](#fucktx-腾讯即时通讯缓存整理归档工具)
  - [项目说明](#项目说明)
  - [功能说明](#功能说明)
  - [操作方法](#操作方法)
    - [常见缓存目录](#常见缓存目录)
    - [使用界面操作](#使用界面操作)
    - [使用命令行操作](#使用命令行操作)
    - [使用拖放操作](#使用拖放操作)
  - [系统支持](#系统支持)

## 项目说明
* 因为腾讯系通讯软件的缓存机制，导致大量图片或视频文件被缓存在许多零散路径中，不便整理，所以写了这个工具。

## 功能说明
* 将指定目录中所有文件按照后缀名格式复制到目标目录下的对应后缀名文件夹中，以实现文件按类型分类
* 对文件通过MD5校验进行排重
* 将PC版微信对图片缓存加密为.dat文件进行解密，并对手机版QQ部分缓存无后缀名的文件类型（**仅图片或视频类型**）进行推测
* 整理后强制删除空文件夹，可选强制删除原始文件（**无法在回收站中找回**）

## 操作方法

* PC版可直接在PC上操作，手机版需要将文件从手机上拷贝到PC再操作。

### 常见缓存目录
* QQ PC版 图片： `我的文档\\Tencent Files\\11111111\\image`
* QQ PC版 视频： `我的文档\\Tencent Files\\11111111\\video`
* QQ PC版 文件： `我的文档\\Tencent Files\\11111111\\FileRecv`
* QQ Android版 图片： `Android\\data\\com.tencent.mobileqq\\Tencent\\MobileQQ\\chatpic & photo`
* QQ Android版 视频： `Android\\data\\com.tencent.mobileqq\\Tencent\\MobileQQ\\shortvideo`
* QQ Android版 文件： `Android\\data\\com.tencent.mobileqq\\Tencent\\QQfile_recv`
* WeChat PC版 图片： `我的文档\\WeChat Files\\wxid_aaaaaaaaaaaa\\FileStorage\\Image`
* WeChat PC版 视频： `我的文档\\WeChat Files\\wxid_aaaaaaaaaaaa\\FileStorage\\Video`
* WeChat PC版 文件： `我的文档\\WeChat Files\\wxid_aaaaaaaaaaaa\\FileStorage\\File`
* WeChat 新PC版 图片&视频&文件： `我的文档\\WeChat Files\\wxid_aaaaaaaaaaaa\\FileStorage\\MsgAttach`
* WeChar Android版： `Android\\data\\com.tencent.mm\\MicroMsg\\aaaaaaaaaa\\image & image2`
* WeChar Android版： `Android\\data\\com.tencent.mm\\MicroMsg\\aaaaaaaaaa\\video`
* WeChar Android版 文件： `Android\\data\\com.tencent.mm\\MicroMsg\\Download`
  
其他目录中也可能有部分缓存，总量相对不多，可按需自行调整

### 使用界面操作
* 双击程序后添加需要整理的文件夹
* 手动指定输出的文件夹 **默认为程序目录**
* 勾选需要整理的文件类型及是否删除原文件
* 点击运行后开始整理
* 界面操作仅支持对指定文件夹进行整理

### 使用命令行操作
* 命令行输入 `FTX.exe "d:/folder1/" "d:/folder2/" "d:/folder3/1.dat"...` 后回车
* 支持4个入参
* 1. `--image=true` **默认为True**
* 2. `--video=true` **默认为True**
* 3. `--document=true` **默认为True**
* 4. `--remove=false` **默认为False**
* 完整命令行 `FTX.exe --image=true --video=true --document=true --remove=false "d:/folder1/" "d:/folder2/" "d:/folder3/1.dat" ...`
* 命令行支持指定文件夹和指定文件两种模式

### 使用拖放操作
* 将需要整理的文件或文件夹拖放到程序上则开始自动整理
* 拖放操作不可更改默认的入参
* 拖放操作支持拖放文件夹和文件两种模式，需要注意拖放文件过多可能会超出操作系统命令行字符字数限制

## 系统支持
* 目前exe程序只支持win10 64位
* 最低支持win7，如果需要在win7上运行，则按如下操作：
* 1. 下载并解压全部源码
* 2. 安装操作系统对应的CPYTHON解释器，大版本号为3.8，小版本号越高越好
* 3. 下载安装MinGW并将目录加入系统path路径以便使用gcc
* 4. 双击源码文件夹内的build.bat等待构建完成
* 5. 需要程序尽量小一点的，可以自行下载upx放在源代码根目录后再build