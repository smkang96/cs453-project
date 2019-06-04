# cs453-project

### Setup
```
$ virtualenv venv
$ venv
$ pip3 install -r pip-requirements.txt
```

### test
```
$ python3 main.py --class_file [VIRTUAL_ENV_SITE_PACKAGES_PATH]/stdnum/isbn.py --mod_name stdnum.isbn --mut_name validate
$ python3 main.py --class_file test/triangle.py --class_name Triangle --mut_name testTriangle
$ python3 main.py --class_file test/Chessnut/game.py --class_name Game --mut_name apply_move

$ python3 main.py --class_file test/sut.py --class_name C --mut_name f
```
