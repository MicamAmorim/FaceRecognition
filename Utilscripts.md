
___

# Utils scripts

___

## Allowing user uses scripts commands on windows
> Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned

## Creating and using virtual envs
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
