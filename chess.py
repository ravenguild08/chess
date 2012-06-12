""" 
chess.py

Peter Hung
060612-060812
for shits and giggles
"""

import random
import unittest
import string

# enums
BPawn, BBishop, BKnight, BRook, BQueen, BKing, No, WKing, WQueen, WRook, WKnight, WBishop, WPawn = range(-6, 7)
King, Queen, Rook, Knight, Bishop, Pawn = range(1, 7)
B, W = [-1, 1]

class MoveError(Exception):
    def __init__(self, value):
        self.parameter = value
    def __str__(self):
        return repr(self.parameter)
    
class Space():
    def __init__(self, board, x, y):
        self.board = board
        self.x = x
        self.y = y
        self.nHoriz = [[],[],[],[]]
        self.nDiag = [[],[],[],[]]
        self.nKnight = []
        self.unit = No
        self.moves = []
    def add_iff_legal(self, x, y):
        if x >= 0 and x < 8 and y >= 0 and y < 8:
            self.nKnight.append(self.board[x][y])
    def set_neighbors(self):
        # print "space " + str(self.x) + " " + str(self.y)
        for n in range(self.y + 1, 8):
            self.nHoriz[0].append(self.board[self.x][n])
        for e in range(self.x + 1, 8):
            self.nHoriz[1].append(self.board[e][self.y])
        for s in range(self.y - 1, -1, -1):
            self.nHoriz[2].append(self.board[self.x][s])        
        for w in range(self.x - 1, -1, -1):
            self.nHoriz[3].append(self.board[w][self.y])
        # ne
        x = self.x + 1
        y = self.y + 1
        while x < 8 and y < 8:
            self.nDiag[0].append(self.board[x][y])
            x += 1
            y += 1
        # se
        x = self.x + 1
        y = self.y - 1
        while x < 8 and y >= 0:
            self.nDiag[1].append(self.board[x][y])
            x += 1
            y -= 1
        # sw
        x = self.x - 1
        y = self.y - 1
        while x >= 0 and y >= 0: 
            self.nDiag[2].append(self.board[x][y])
            x -= 1
            y -= 1
        # nw
        x = self.x - 1
        y = self.y + 1
        while x >= 0 and y < 8:
            self.nDiag[3].append(self.board[x][y])
            x -= 1
            y += 1
        self.add_iff_legal(self.x + 1, self.y + 2)
        self.add_iff_legal(self.x + 2, self.y + 1)
        self.add_iff_legal(self.x + 2, self.y - 1)
        self.add_iff_legal(self.x + 1, self.y - 2)
        self.add_iff_legal(self.x - 1, self.y - 2)
        self.add_iff_legal(self.x - 2, self.y - 1)
        self.add_iff_legal(self.x - 2, self.y + 1)
        self.add_iff_legal(self.x - 1, self.y + 2)
        return

    def get_team(self):
        if self.unit < 0:
            return B
        elif self.unit > 0:
            return W
        else:
            return 0
        
    def add_first_moves(self, arr, list):
        if not arr:
            return list
        team = self.get_team()
        space = arr[0]
        spaceTeam = space.get_team()
        if team == spaceTeam:
            return list
        elif team == -spaceTeam:
            return list.append(space)
        else:
            return list.append(space)
    def add_row_moves(self, arr, list):
        if not arr:
            return list
        team = self.get_team()
        for space in arr:
            spaceTeam = space.get_team()
            if team == spaceTeam:
                return list
            elif team == -spaceTeam:
                list.append(space)
                return list
            else:
                list.append(space)
        return list
    def get_moves(self):
        list = []
        if self.unit == No:
            return list
        elif abs(self.unit) == King:
            for i in range(4):
                self.add_first_moves(self.nHoriz[i], list)
                self.add_first_moves(self.nDiag[i], list)
            # TODO: castle
        elif abs(self.unit) == Queen:
            for i in range(4):
                self.add_row_moves(self.nHoriz[i], list)
                self.add_row_moves(self.nDiag[i], list)
        elif abs(self.unit) == Rook:
            for i in range(4):
                self.add_row_moves(self.nHoriz[i], list)
        elif abs(self.unit) == Knight:
            team = self.get_team()
            for space in self.nKnight:                
                if team != space.get_team():
                    list.append(space)
        elif abs(self.unit) == Bishop:
            for i in range(4):
                self.add_row_moves(self.nDiag[i], list)
        elif self.unit == WPawn:
            if self.y == 7:
                # TODO: promote
                
                return []
            if self.board[self.x][self.y + 1].unit == No:
                list.append(self.board[self.x][self.y + 1])
                if self.y == 1 and self.board[self.x][3].unit == No:
                    list.append(self.board[self.x][3])
            if self.x < 7 and self.board[self.x + 1][self.y + 1].get_team() == B:
                list.append(self.board[self.x + 1][self.y + 1])
            if self.x > 0 and self.board[self.x - 1][self.y + 1].get_team() == B:
                list.append(self.board[self.x - 1][self.y + 1])
            # TODO: en pessant
            
        elif self.unit == BPawn:
            if self.y == 0:
                # TODO: promote
                
                return []
            if self.board[self.x][self.y - 1].unit == No:
                list.append(self.board[self.x][self.y - 1])
                if self.y == 6 and self.board[self.x][4].unit == No:
                    list.append(self.board[self.x][4])
            if self.x < 7 and self.board[self.x + 1][self.y - 1].get_team() == W:
                list.append(self.board[self.x + 1][self.y - 1])
            if self.x > 0 and self.board[self.x - 1][self.y - 1].get_team() == W:
                list.append(self.board[self.x - 1][self.y - 1])
            # TODO: en pessant
            
        # TODO: check avoiding
        self.moves = list
        return list

    def coord_string(self):    
        return "abcdefgh"[self.x] + str(self.y + 1)
    def x_string(self):
        return "abcdefgh"[self.x]
    def y_string(self):
        return str(self.y + 1)
    def id_string(self):
        letters = ["K", "Q", "R", "N", "B", "P"]
        return letters[abs(self.unit) - 1]
    def unit_string(self):
        if self.unit == 0:
            return "  "
        elif self.unit < 0:
            return " " + self.id_string()
        else:
            return self.id_string() + " "


class Game():
    def __init__(self):
        #create the board grid and set the neighbors
        self.b = {}
        for i in range(8):
            self.b[i] = {}
            for j in range(8):
                self.b[i][j] = Space(self.b, i, j)
        for i in range(8):
            for j in range(8):
                self.b[i][j].set_neighbors()
        
        # place pieces on board
        self.white = [[], [], [], [], [], [], []]
        self.black = [[], [], [], [], [], [], []]
        self.fill_board()       
        
        # set up the history, turn count, and everything
        self.count = 0
        self.removes = []
        self.adds = []
        self.log = []
        
        # TODO: no progress counter
        return
    def put(self, unit, space):
        space.unit = unit
        index = abs(unit)
        team = space.get_team()
        if team == W:
            self.white[index].append(space)
        elif team == B:
            self.black[index].append(space)
        return
    def remove(self, space):
        team = space.get_team()
        index = abs(space.unit)
        if team == W:
            self.white[index].remove(space)
        elif team == B:
            self.black[index].append(space)
        space.unit = No        
        return
    def fill_board(self):
        self.put(WRook, self.b[0][0])
        self.put(WKnight, self.b[1][0])
        self.put(WBishop, self.b[2][0])
        self.put(WQueen, self.b[3][0])
        self.put(WKing, self.b[4][0])
        self.put(WBishop, self.b[5][0])
        self.put(WKnight, self.b[6][0])
        self.put(WRook, self.b[7][0])
        self.put(BRook, self.b[0][7])
        self.put(BKnight, self.b[1][7])
        self.put(BBishop, self.b[2][7])
        self.put(BQueen, self.b[3][7])
        self.put(BKing, self.b[4][7])
        self.put(BBishop, self.b[5][7])
        self.put(BKnight, self.b[6][7])
        self.put(BRook, self.b[7][7])
        for i in range(8):
            self.put(WPawn, self.b[i][1])
            self.put(BPawn, self.b[i][6])
        return
    def print_board(self):
        print " "
        print "     a  b  c  d  e  f  g  h  "
        print "   +--+--+--+--+--+--+--+--+ "
        for i in range(7, -1, -1):
            line = " " + str(i + 1) + " |"
            for j in range(8):
                line += self.b[j][i].unit_string()
                line += "|"
            line += " " + str(i + 1)
            print line
            print "   +--+--+--+--+--+--+--+--+"
        print "    a  b  c  d  e  f  g  h   "
        print " "
        return

    def undo_move(self):
        if self.count == 0:
            raise MoveError("there are no more moves to undo!")
        # regress the turn counter
        self.count -= 1
        # remove the moved pieces
        for loc, unit in self.adds.pop():
            self.remove(loc)
        # add back all the pieces that were removed
        for loc, unit in self.removes.pop():
            self.put(unit, loc)
        self.log.pop()
        return
        
    def parse_move_string(self, s):
        turn = self.whose_turn()
        team = self.black
        if turn == W:
            team = self.white

        if s == "O-O" or s == "0-0":
            # kingside castle
            return
        elif s == "O-O-O" or s == "0-0-0":
            # queenside castle
            return
            
        if len(s) == 2:
            # pawn moving forward
            try:
                space = self.parse_coord_string(s)
            except ValueError:
                raise MoveError("that's not a coordinate!")
            unit = Pawn
            col = space.x
        else:
            try:
                unit = self.parse_id_char(s[0])
                if unit == Pawn:
                    col = "abcdefgh".find(s[0])
                    print col
            except ValueError:
                raise MoveError("first letter not recognized")            
            index = len(s) - 1
            while index >= 1:
                index -= 1
                try:
                    space = self.parse_coord_string(s[index:(index + 2)])
                    break
                except ValueError:
                    if index == 1:
                        raise MoveError("couldn't find a coordinate!")
        print space.coord_string()
        print unit
        
        # attempt to find the piece that wants to move there
        if unit == Pawn:
            count = 0
            for guy in team[Pawn]:
                if guy.x == col and space in guy.get_moves():
                    piece = guy
                    count += 1
                    break
            if count == 0:
                raise MoveError("no such move is possible!")
        else:
            count = 0
            for guy in team[unit]:
                if space in guy.get_moves():
                    piece = guy
                    print "found piece at " + piece.coord_string()
                    count += 1
            if count > 1:
                # TODO: ambiguity decoding
                print "it's ambiguous! until i implement it, you don't get to choose..."
            if count == 0:
                raise MoveError("no such move is possible!")
                
        """
        if piece.unit == No:
            raise MoveError("there is no piece there!")
        if self.whose_turn() == W and piece.get_team() == B or self.whose_turn() == B and piece.get_team() == W:
            raise MoveError("that's not your piece!")
        if space not in piece.get_moves(): # careful... do we want to rerun?
            raise MoveError("that piece can't move there!")
        """
        
        # remember if it's a capture
        capture = False
        # enpassant, kingcastle, queencastle, promotion
        if space.unit != No:
            capture = True
        
        # save the history
        if capture:
            self.removes.append([(piece, piece.unit), (space, space.unit)])
        else:
            self.removes.append([(piece, piece.unit)])
        self.adds.append([(space, piece.unit)])
        
        # TODO: recompose the string in case it's actually wrong
        self.log.append(s)
        
        # actually move the piece
        if turn == W:
            self.put(unit, space)
        elif turn == B:
            self.put(-unit, space)
        self.remove(piece)

        # progress the turn counter
        self.count += 1
        return

    def parse_coord_string(self, s):
        if len(s) != 2:
            raise ValueError
        try: 
            file = "abcdefgh".find(s[0])
            rank = int(s[1]) - 1
            if rank >= 0 and rank < 8 and file >= 0 and file < 8:
                return(self.b[file][rank])
            else:
                raise ValueError
        except ValueError:
            raise ValueError # lol
    def parse_id_char(self, c):
        result = "KQRNBabcdefgh".find(c) + 1
        if result == 0:
            raise ValueError
        elif result >= 6:
            return Pawn
        else:
            return result
    def move_string(self, piece, space):
        string = ""
        if space not in piece.moves:
            return string
        # TODO: castle
        
        # if not pawn, need letter
        if abs(piece.piece) != Pawn:
            string += piece.id_string()
        # pawn capture takes file
        elif space.piece != No:
            string += piece.x_string()

        # TODO: ambiguity; check if other pieces can go there

        # if capture
        if space.piece != No:
            string += "x"
        
        string += space.coord_string()
        
        # TODO: promotion
        
        # TODO: mate check
        
        return string

    def whose_turn(self):
        if self.count % 2:
            return B
        else:
            return W
        
game = Game()
for i in range(8):
    for j in range(8):
        p = game.b[i][j]
        p.get_moves()

while True:
    game.print_board()
    string = raw_input("Move: ")
    if string == "quit" or string == "exit":
        exit()
    elif string == "undo":
        try:
            game.undo_move()
        except MoveError, (instance):
            print instance.parameter
    elif string == "list":
        team = game.black
        if game.whose_turn() == W:
            team = game.white
        for ls in team:
            line = ""
            for space in ls:
                line += space.coord_string() + " "
            print line
    else:
        try:
            game.parse_move_string(string)
        except MoveError, (instance):
            print instance.parameter
