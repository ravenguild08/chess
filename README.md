chess.py

Peter Hung
060612-061512

a chess engine and parser
for now, asks for text-inputted moves per player and prints board to console.
the game fully implemented, including all special moves and draw conditions
the parser is robust and attempts to extract algebraic notation out of input
  e.g. e4, Nxc3, Qf5+, Rae8, O-O
stores generous amounts of extra informtion in a board object per turn,
  meant to be the basis for an AI
