# pydayz - A DayZ tools collection

![detection](preview/logo.png)

<https://www.bohemia.net/games/dayz/>

In this repository are collected tools and scripts for the game DayZ.

## Installing

### Windows

```powershell
git clone --recurse-submodules git@github.com:tassoneroberto/py-dayz.git
cd pydayz
py -3.10 -m venv venv
.\venv\Scripts\Activate.ps1
py -m pip install iocontroller
py -m pip install .
```

## Passcode cracking

Bruteforce the 3 and 4 discs combination locks (vanilla only).

![detection](preview/combination_lock_green.png)

### Usage

It is recommended to set the game in window mode.

Note: Press `ESC` to interrupt the bot.

```powershell
pydayz_crack_passcode
```

Get the arguments list with the `help` function:

```powershell
pydayz_crack_passcode --help
```

### Command line arguments

The following table is listing all the arguments you can use:

| arg           |  description      |
|:-------------:|:-----------------:|
| help          | Arguments description |
| timeout       | Maximum time in seconds allowed |
