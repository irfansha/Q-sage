# **Q-sage**
QBF encoder for various 2-player games including Positional games (like hex), Connect4, Breakthrough, Domineering etc.
Generates lifted QBF encodings for finding winning strategies of bounded depth.

## Positional Games, lifted Hex encodings:
## Usage:

Generating Hex QBF Instances:

    python3 Q-sage.py -e [pg | cp | eg | ew] --problem ./testcases/Hein-hex-Lifted/hein_04_3x3-05.pg --run 0 --encoding_out [path-to-out-file]

help:

    python3 Q-sage.py -h

_Input:_  pg format positional game inputs for Hex like games.

_Output:_  generates a qbf instances that encodes the existence of bounded winning strategy

## Non-Positional Games:
## Usage:
TBU


## Dependencies:
For visualization of qcir encoding generated, we use pyvis.network

Install using:

    pip install pyvis.network
    pip install pyvis

## Author:

    Irfansha Shaik
    Aarhus
