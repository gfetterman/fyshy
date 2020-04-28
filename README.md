# fishpy

fishpy is a clone of the old Flash game "Fishy", where you control a fish trying
to survive in a dangerous pond by eating smaller neighbors and avoiding bigger
ones.

## Installation

fishpy runs under Python 3. There is no installer.

```shell
$ git clone https://github.com/gfetterman/fishpy.git
```

fishpy requires pygame to run.

```shell
$ pip install pygame
```

(You could use a conda environment if you like.)

To start:

```shell
$ python fishpy.py
```

## How to play

The arrow keys move the yellow fish around the screen.

Swim into other fish to eat them. You can safely eat anything smaller than
yourself, but anything bigger will eat you instead.

You get bigger when you've eaten a certain number of fish.

Eating bigger fish yields a bigger score, displayed at the top in the center.
The score doesn't affect anything, though.

## Notes

Fishy clones abound on the internet. This one isn't anything special, but I
wanted something to build to start fiddling with pygame, so here you are.

It's a good deal shorter than the original, mostly so I could test all of the
parts without having to play for ten minutes.

(Yes, I made the little fish icons myself. Yes, I used Paint.)
