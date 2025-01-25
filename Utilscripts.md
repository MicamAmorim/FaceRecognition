
___

# Utils scripts

___

## Allowing user uses scripts commands on windows
> Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned

## Creating and using virtual envs
> pip install virtualenv
> python -m venv venv
### Activating venvs
> venv/Scripts/activate

## Change Interpreter on Vs Code
> Ctrl + Shift + P
> Select the python interpreter

## Requirements freeze
pip freeze > requirements.txt
pip install -r requirements.txt

## increase timeout on pip
> pip install face-recognition --default-timeout=100
> Cmake may be needed for face-recognition
> Microsoft C++ compiling tools
> May be necessary install dlib before using the wheel: dlib-19.24.1-cp311-cp311-win_amd64.whl

# Install only this minimal requirements on your virtual env in this order
> opencv-python==4.11.0.86
> opencv-contrib-python==4.11.0.86
> numpy==1.23.5
> cmake==3.31.4
- Change the path bellow to the path your file
> dlib @ file:///C:/Users/Windows%2011/Documents/Projects/portifolio/FaceRecognition/dlib-19.24.1-cp311-cp311-win_amd64.whl#sha256=6f1a5ee167975d7952b28e0ce4495f1d9a77644761cf5720fb66d7c6188ae496
> face-recognition==1.3.0
> tqdm==4.67.1
> pandas==2.2.3

