
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
> Cmake is needed for face-recognition
> Ferramentas de compilação do Microsoft C++

## Install pre-commit for automate freeze
> pip install pre-commit
> create a file named pre-commit-config.yaml