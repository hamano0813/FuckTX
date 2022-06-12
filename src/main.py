#!/usr/bin/env python
# -*- coding: utf-8 -*-

def get_option(argv_list: list):
    options = ['image=', 'video=', 'document=', 'remove=']
    opts, args = getopt.getopt(argv_list, '', options)
    option_conf = dict()
    for opt, arg in opts:
        if opt == '--image':
            option_conf['image'] = eval(arg.capitalize())
        if opt == '--video':
            option_conf['video'] = eval(arg.capitalize())
        if opt == '--document':
            option_conf['document'] = eval(arg.capitalize())
        if opt == '--remove':
            option_conf['remove'] = eval(arg.capitalize())
    return option_conf


if __name__ == '__main__':
    import getopt
    import os
    import sys

    from PySide6.QtWidgets import QApplication, QWidget

    from process import Process
    from window import Window

    app = QApplication(sys.argv)
    target = os.path.split(sys.argv[0])[0]

    if len(sys.argv) > 1:

        w = QWidget()

        conf = get_option(sys.argv[1:])

        w.process = Process(w, sys.argv[1:], target, **conf, source=target)
        w.process.logPrint[str].connect(print)
        w.process.start()
        # noinspection PyUnresolvedReferences
        w.process.finished.connect(input)
        # noinspection PyUnresolvedReferences
        w.process.finished.connect(sys.exit)

    elif len(sys.argv) == 1:
        w = Window(target, target)
        w.show()

    sys.exit(app.exec())
