@title build FuckTencent project
python -m venv venv --upgrade-deps
call venv/scripts/activate
pip install -i https://pypi.tuna.tsinghua.edu.cn/simple -r requirements.txt
python release.py src/main.py
pyinstaller project.spec
RMDIR /S /Q release
RMDIR /S /Q build
RMDIR /S /Q venv
gcc ./src/decrypt.c -shared -o ./dist/decrypt.dll
start dist