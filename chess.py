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
def parse_x_char(c):
    return "abcdefgh".find(c)
def parse_y_char(c):
    return int(c) - 1
def parse_id_char(c):
    result = "KQRNBabcdefgh".find(c) + 1
    if result == 0:
        raise ValueError
    elif result >= 6:
        return Pawn
    else:
        return result
def x_char(x):
    return "abcdefgh"[x]
def y_char(y):
    return str(y + 1)
def unit_char(unit):
    letters = ["K", "Q", "R", "N", "B", "P"]
    return letters[abs(unit) - 1]
def team_string(team):
    if team == W:
        return "White"
    elif team == B:
        return "Black"
    else:
        return ""
    

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
        self.moves = [] # list of moves        
        self.protects = [] # list of friendly pieces who if captured can be avenged
        self.protectedBy = [] # list of friendly pieces who protects self
        self.canMoveTo = [] # list of pieces who can move to self
        self.threatens = [] # list of pieces who self can capture
        self.threatenedBy = [] # list of pieces who can capture self
        
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
    
    def mark_move(self, space):
        self.moves.append(space)
        space.canMoveTo.append(self)
    def mark_protect(self, space):
        self.protects.append(space)
        space.protectedBy.append(self)
    def mark_threaten(self, space):
        self.threatens.append(space)
        space.threatenedBy.append(self)
    def add_first_moves(self, arr):
        if not arr:
            return
        team = self.get_team()
        space = arr[0]
        spaceTeam = space.get_team()
        if team == spaceTeam:
            self.mark_protect(space)
        elif team == -spaceTeam:
            self.mark_move(space)
            self.mark_threaten(space)
        else:
            self.mark_move(space)
            self.mark_threaten(space)
    def add_row_moves(self, arr):
        if not arr:
            return
        team = self.get_team()
        for space in arr:
            spaceTeam = space.get_team()
            if team == spaceTeam:
                self.mark_protect(space)
                return
            elif team == -spaceTeam:
                self.mark_move(space)
                self.mark_threaten(space)
                return
            else:
                self.mark_move(space)
                self.mark_threaten(space)
        return
    def get_moves(self):
        unit = abs(self.unit)
        if unit == No:
            return
        elif unit == King:
            for i in range(4):
                self.add_first_moves(self.nHoriz[i])
                self.add_first_moves(self.nDiag[i])
            # TODO: castle
        elif unit == Queen:
            for i in range(4):
                self.add_row_moves(self.nHoriz[i])
                self.add_row_moves(self.nDiag[i])
        elif unit == Rook:
            for i in range(4):
                self.add_row_moves(self.nHoriz[i])
        elif unit == Knight:
            team = self.get_team()
            for space in self.nKnight:
                spaceTeam = space.get_team()
                if team == spaceTeam:
                    self.mark_protect(space)
                elif team == -spaceTeam:
                    self.mark_move(space)
                    self.mark_threaten(space)
                else:
                    self.mark_move(space)
                    self.mark_threaten(space)
        elif unit == Bishop:
            for i in range(4):
                self.add_row_moves(self.nDiag[i])
        elif self.unit == WPawn:
            if self.y == 7:
                # TODO: promote
                
                return []
            if self.board[self.x][self.y + 1].unit == No:
                self.mark_move(self.board[self.x][self.y + 1])
                if self.y == 1 and self.board[self.x][3].unit == No:
                    self.mark_move(self.board[self.x][3])
            diagonals = []
            if self.x > 0:
                diagonals.append(self.board[self.x - 1][self.y + 1])
            if self.x < 7:
                diagonals.append(self.board[self.x + 1][self.y + 1])
            for space in diagonals:
                spaceTeam = space.get_team()
                if spaceTeam == B:
                    self.mark_move(space)
                    self.mark_threaten(space)
                elif spaceTeam == W:
                    self.mark_protect(space)
                else:
                    self.mark_threaten(space)

            # TODO: en passant
            
        elif self.unit == BPawn:
            if self.y == 0:
                # TODO: promote
                
                return []
            if self.board[self.x][self.y - 1].unit == No:
                self.mark_move(self.board[self.x][self.y - 1])
                if self.y == 6 and self.board[self.x][4].unit == No:
                    self.mark_move(self.board[self.x][4])
            diagonals = []
            if self.x > 0:
                diagonals.append(self.board[self.x - 1][self.y - 1])
            if self.x < 7:
                diagonals.append(self.board[self.x + 1][self.y - 1])
            for space in diagonals:
                spaceTeam = space.get_team()
            for space in diagonals:
                spaceTeam = space.get_team()
                if spaceTeam == W:
                    self.mark_move(space)
                    self.mark_threaten(space)
                elif spaceTeam == B:
                    self.mark_protect(space)
                else:
                    self.mark_threaten(space)

            # TODO: en pessant
            
        return self.moves

    def coord_string(self):    
        return x_char(self.x) + y_char(self.y)
    def unit_string(self):
        if self.unit == 0:
            return "  "
        elif self.unit < 0:
            return " " + unit_char(self.unit)
        else:
            return unit_char(self.unit) + " "
    def unit_char(self):
        return unit_char(self.unit)

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
            self.black[index].remove(space)
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

    def update_moves(self):
        for i in range(8):
            for j in range(8):
                space = self.b[i][j]
                space.moves = []
                space.threatens = []
                space.protects = []
                space.protectedBy = []
                space.canMoveTo = []
                space.threatenedBy = []
        for i in range(8):
            for j in range(8):
                self.b[i][j].get_moves()
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
   
    # takes a string and attempts to parse it and execute it
    # raises MoveError if string can't be parsed or move isn't legal
    def execute_move(self, s):
        if len(s) < 2:
            raise MoveError("algebraic notation needs at least two characters!")
        capture = False
        check = False
        mate = False
        promotion = False
        ambiguity = ""
        promotion = No
        
        turn = self.whose_turn()
        army = self.black
        if turn == W:
            army = self.white

        # kingside castle
        if s == "O-O" or s == "0-0":
            unit = King
        
        # queenside castle
        elif s == "O-O-O" or s == "0-0-0":
            unit = King
        
        # other move
        else:
            # pawn moving forward
            if len(s) == 2:
                try:
                    space = self.parse_coord(s)
                except ValueError:
                    raise MoveError("that's not a coordinate!")
                unit = Pawn
                col = space.x
            else:
                # parse unit type and disambiguating column if it's a pawn for capture
                try:
                    unit = parse_id_char(s[0])
                    if unit == Pawn:
                        col = parse_x_char(s[0])
                        print col
                except ValueError:
                    raise MoveError("first letter not recognized")            
                
                # attempt to parse a coordinate from the string, starting from the back
                index = len(s) - 1
                while index >= 1:
                    index -= 1
                    try:
                        space = self.parse_coord(s[index:(index + 2)])
                        break
                    except ValueError:
                        if index == 1:
                            raise MoveError("couldn't find a coordinate!")
        
            # attempt to find the piece that wants to move there
            if unit == Pawn:
                count = 0
                for guy in army[Pawn]:
                    if guy.x == col and space in guy.moves: # TODO: this can be done much more effectively now
                        piece = guy
                        count += 1
                        break
                if count == 0:
                    raise MoveError("no such move is possible!")
            else:
                count = 0
                for guy in army[unit]:
                    if space in guy.moves: # TODO: this can be done much more effectively now
                        piece = guy
                        count += 1
                if count > 1:
                    # TODO: ambiguity decoding
                    print "it's ambiguous! until i implement it, you don't get to choose... and it's probably going to break"
                if count == 0:
                    raise MoveError("no such move is possible!")
                # enpassant, promotion

                
        # remember if it's a capture
        if space.unit != No:
            capture = True
            captured = space.unit
        
        # actually move the piece
        if capture:
            self.remove(space)
        if turn == W:
            self.put(unit, space)
        elif turn == B:
            unit = -unit
            self.put(unit, space)
        self.remove(piece)

        # see if it's a check
        if self.is_check():
            print team_string(turn) + " is in check"
            
        # see if own king is checked after move and disallow if it is?
        
        
        # build the string and save it
        string = self.move_string(piece, space, capture = capture)        
        self.log.append(string)
        print string
        
        
        # save the history
        if capture:
            self.removes.append([(piece, unit), (space, captured)])
        else:
            self.removes.append([(piece, unit)])
        self.adds.append([(space, unit)])

        # progress the turn counter
        self.count += 1
        return

    def parse_coord(self, s):
        if len(s) != 2:
            raise ValueError
        try: 
            file = parse_x_char(s[0])
            rank = parse_y_char(s[1])
            if rank >= 0 and rank < 8 and file >= 0 and file < 8:
                return(self.b[file][rank])
            else:
                raise ValueError
        except ValueError:
            raise ValueError # lol
    def move_string(self, piece, space, capture = False, check = False, mate = False, kscastle = False, qscastle = False, promotion = No, ambiguity = ""):
        string = ""

        if kscastle:
            string = "0-0"
        elif qscastle:
            string = "0-0-0"
        
        # if not pawn, need letter
        elif abs(piece.unit) != Pawn:
            string = unit_char(piece.unit)
        # pawn capture takes file
        elif capture:
            string = x_char(piece.x)

        string += ambiguity
        
        if capture:
            string += "x"
        
        # add the coordinate
        if not kscastle and not qscastle:
            string += space.coord_string()
        
        if promotion != No:
            string += "=" + unit_char(promotion)
            
        if mate:
            string += "#"
        elif check:
            string += "+"
        
        return string

    def whose_turn(self):
        if self.count % 2:
            return B
        else:
            return W
    def is_check(self, team = 0):
        if team == W:
            return len(self.white[King][0].threatenedBy) > 0
        elif team == B:
            return len(self.black[King][0].threatenedBy) > 0
        else:
            return self.is_check(self.whose_turn() * -1)
        
        
game = Game()

while True:
    game.print_board()
    game.update_moves()
    string = raw_input("Command: ")
    if string == "quit" or string == "exit":
        exit()
    elif string == "undo":
        try:
            game.undo_move()
        except MoveError, (instance):
            print instance.parameter
    elif string == "list":
        army = game.black
        if game.whose_turn() == W:
            army = game.white
        for ls in army:
            for piece in ls:
                line = piece.unit_string() + " at " + piece.coord_string() + " can move to "
                for space in piece.moves:
                    line += space.coord_string() + ","
                print line
    elif string == "moves":
        coordStr = raw_input("which coordinate? ")
        piece = game.parse_coord(coordStr)
        if piece.unit != No:
            line = "This piece can move to: "
            for space in piece.moves:
                line += space.coord_string() + ","
            print line
            line = "This piece threatens: "
            for space in piece.threatens:
                line += space.coord_string() + ","
            print line
            line = "This piece protects: "
            for space in piece.protects:
                line += space.unit_char() + space.coord_string() + ","
            print line
            line = "This piece is protected by: "
            for space in piece.protectedBy:
                line += space.unit_char() + space.coord_string() + ","
            print line            
        line = "This space can be moved to by: "
        for space in piece.canMoveTo:
            line += space.unit_char() + space.coord_string() + ","
        print line
        line = "This space is threatened by: "
        for space in piece.threatenedBy:
            line += space.unit_char() + space.coord_string() + ","
        print line
    else:
        try:
            game.execute_move(string)
        except MoveError, (instance):
            print instance.parameter
