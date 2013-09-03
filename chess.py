""" 
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

"""

import unittest

# enums
BPawn, BBishop, BKnight, BRook, BQueen, BKing, No, WKing, WQueen, WRook, WKnight, WBishop, WPawn = range(-6, 7)
King, Queen, Rook, Knight, Bishop, Pawn = range(1, 7)
BWins, BChecks, Ok, WChecks, WWins, Stalemate = range(-2, 4)
Checks, Wins = [1, 2]
B, W = [-1, 1]

def parse_x_char(c):
    result = "abcdefgh".find(c)
    if result < 0 or result >= 8:
        raise ValueError
    return result
def parse_y_char(c):
    result = int(c) - 1
    if result < 0 or result >= 8:
        raise ValueError
    return result
def parse_id_char(c):
    result = "KQRNBPabcdefgh".find(c) + 1
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
    return "KQRNBP"[abs(unit) - 1]
def unit_string(unit):
    strings = ["King", "Queen", "Rook", "Knight", "Bishop", "Pawn"]
    return strings[abs(unit) - 1]
def team_string(team):
    if team == W:
        return "White"
    elif team == B:
        return "Black"
    else:
        return "?????"
def team_of_unit(unit):    
    if unit < 0:
        return B
    elif unit > 0:
        return W
    else:
        return 0

class MoveError(Exception):
    def __init__(self, value):
        self.parameter = value
    def __str__(self):
        return repr(self.parameter)
    
class Space():
    def __init__(self, game, x, y):
        self.game = game
        self.x = x
        self.y = y
        self.nHoriz = [[],[],[],[]]
        self.nDiag = [[],[],[],[]]
        self.nKnight = []
        self.unit = No
        self.moves = []         # list of moves        
        self.protects = []      # list of friendly pieces who if captured can be avenged
        self.protectedBy = []   # list of friendly pieces who protects self
        self.canMoveTo = []     # list of pieces who can move to self
        self.threatens = []     # list of pieces who self can capture
        self.threatenedBy = []  # list of pieces who can capture self
        
    def set_knight_neighbor(self, x, y):
        if x >= 0 and x < 8 and y >= 0 and y < 8:
            self.nKnight.append(self.game.b[x][y])
    def set_neighbors(self):
        for n in range(self.y + 1, 8):
            self.nHoriz[0].append(self.game.b[self.x][n])
        for e in range(self.x + 1, 8):
            self.nHoriz[1].append(self.game.b[e][self.y])
        for s in range(self.y - 1, -1, -1):
            self.nHoriz[2].append(self.game.b[self.x][s])        
        for w in range(self.x - 1, -1, -1):
            self.nHoriz[3].append(self.game.b[w][self.y])
        # ne
        x = self.x + 1
        y = self.y + 1
        while x < 8 and y < 8:
            self.nDiag[0].append(self.game.b[x][y])
            x += 1
            y += 1
        # se
        x = self.x + 1
        y = self.y - 1
        while x < 8 and y >= 0:
            self.nDiag[1].append(self.game.b[x][y])
            x += 1
            y -= 1
        # sw
        x = self.x - 1
        y = self.y - 1
        while x >= 0 and y >= 0: 
            self.nDiag[2].append(self.game.b[x][y])
            x -= 1
            y -= 1
        # nw
        x = self.x - 1
        y = self.y + 1
        while x >= 0 and y < 8:
            self.nDiag[3].append(self.game.b[x][y])
            x -= 1
            y += 1
        self.set_knight_neighbor(self.x + 1, self.y + 2)
        self.set_knight_neighbor(self.x + 2, self.y + 1)
        self.set_knight_neighbor(self.x + 2, self.y - 1)
        self.set_knight_neighbor(self.x + 1, self.y - 2)
        self.set_knight_neighbor(self.x - 1, self.y - 2)
        self.set_knight_neighbor(self.x - 2, self.y - 1)
        self.set_knight_neighbor(self.x - 2, self.y + 1)
        self.set_knight_neighbor(self.x - 1, self.y + 2)
        return

    def get_team(self):
        return team_of_unit(self.unit)
    
    # aside from checks, castles, and enpassants, remembers all possible moves. called by Game.update_moves()
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
                return []
            if self.game.b[self.x][self.y + 1].unit == No:
                self.mark_move(self.game.b[self.x][self.y + 1])
                if self.y == 1 and self.game.b[self.x][3].unit == No:
                    self.mark_move(self.game.b[self.x][3])
            diagonals = []
            if self.x > 0:
                diagonals.append(self.game.b[self.x - 1][self.y + 1])
            if self.x < 7:
                diagonals.append(self.game.b[self.x + 1][self.y + 1])
            for space in diagonals:
                spaceTeam = space.get_team()
                if spaceTeam == B:
                    self.mark_move(space)
                    self.mark_threaten(space)
                elif spaceTeam == W:
                    self.mark_protect(space)
                else:
                    self.mark_threaten(space)
        elif self.unit == BPawn:
            if self.y == 0:
                return []
            if self.game.b[self.x][self.y - 1].unit == No:
                self.mark_move(self.game.b[self.x][self.y - 1])
                if self.y == 6 and self.game.b[self.x][4].unit == No:
                    self.mark_move(self.game.b[self.x][4])
            diagonals = []
            if self.x > 0:
                diagonals.append(self.game.b[self.x - 1][self.y - 1])
            if self.x < 7:
                diagonals.append(self.game.b[self.x + 1][self.y - 1])
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
        return self.moves

    def coord_string(self):    
        return x_char(self.x) + y_char(self.y)
    def unit_draw(self):
        if self.unit == 0:
            return "  "
        elif self.unit < 0:
            return " " + unit_char(self.unit).lower()
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
                self.b[i][j] = Space(self, i, j)
        for i in range(8):
            for j in range(8):
                self.b[i][j].set_neighbors()
        
        # set up armies, turn count, history, legalMoves
        self.white = [[], [], [], [], [], [], []]
        self.black = [[], [], [], [], [], [], []]
        self.count = 0
        self.removes = []
        self.adds = []
        self.log = []
        self.lastCapture = -1        
        self.legalMoves = []

        self.promotion = Queen
    
    # places or removes unit on space and updates army
    def put(self, unit, space):
        army = self.get_army(team_of_unit(unit))
        army[abs(unit)].append(space)        
        space.unit = unit
        return
    def remove(self, space):
        army = self.get_army(space.get_team())
        army[abs(space.unit)].remove(space)
        space.unit = No
        return

    # put and remove a set of adds and removes
    def enact(self, adds, removes):
        for unit, piece in removes:
            self.remove(piece)
        for unit, piece in adds:
            self.put(unit, piece)
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
        print "     a  b  c  d  e  f  g  h   "
        print "   +--+--+--+--+--+--+--+--+ "
        for i in range(7, -1, -1):
            line = " " + str(i + 1) + " |"
            for j in range(8):
                line += self.b[j][i].unit_draw()
                line += "|"
            line += " " + str(i + 1)
            print line
            print "   +--+--+--+--+--+--+--+--+"
        print "    a  b  c  d  e  f  g  h   "
        print " "
        return

    # calls get_moves for all the spaces, finds castles and enpassants, disallows checks
    # returns a list of all legal (piece, space) pairs and leaves it in legalMoves
    def update_moves(self):
        self.legalMoves = []
        
        # clear all move and threat saves
        for i in range(8):
            for j in range(8):
                space = self.b[i][j]
                space.moves = []
                space.threatens = []
                space.protects = []
                space.protectedBy = []
                space.canMoveTo = []
                space.threatenedBy = []
        
        # calculate the moves for all pieces
        for ls in self.white:
            for piece in ls:
                piece.get_moves()
        for ls in self.black:
            for piece in ls:
                piece.get_moves()
                
        # tack on castles and enpassant if possible
        self.update_castle()
        self.update_enpassant()
        
        turn = self.get_turn()
        pieceList = [] 
        army = self.get_army()
        
        # need a non-volatile copy of pieces
        for ls in army:
            for piece in ls:
                pieceList.append(piece)
        
        # enact each move that can be made by current player and add to legalMoves if king is safe
        for piece in pieceList:
            for space in piece.moves:
                adds, removes, string = self.convert_move(piece, space)
                self.enact(adds, removes)
                if self.hypothetical_threat(army[King][0]) == 0:
                    self.legalMoves.append((piece, space))
                self.enact(removes, adds)
        return self.legalMoves
        
    # if the castles are legal for passed king, add to list of allowed moves
    def update_castle(self):
        # for each king
        for team, king, KRook, QRook in [(W, self.b[4][0], self.b[0][0], self.b[7][0]), (B, self.b[4][7], self.b[0][7], self.b[7][7])]:
            KCastle = False
            QCastle = False
            
            # if king not in original space, no castling
            if king.unit != King * team:
                break
                
            # ensure that the rook unmoved can see king. that means intervening spaces empty
            for piece in king.protectedBy:
                if piece == KRook and abs(piece.unit) == Rook:
                    KCastle = True
                if piece == QRook and abs(piece.unit) == Rook:
                    QCastle = True
            
            # save time if needed
            if KCastle == False and QCastle == False:        
                break
                
            # look into history to see if king or rooks have been moved
            for ls in self.removes:
                for unit, space in ls:
                    if KCastle and space == KRook:
                        KCastle = False
                    elif QCastle and space == QRook:
                        QCastle = False                        
                    # save time if found moves by all three pieces
                    elif space == king:
                        break
                    elif KCastle == False and QCastle == False:
                        break
                        
            # check if any of three spaces are threatened
            if KCastle:
                for space in [king, self.b[3][king.y], self.b[2][king.y]]:
                    for threat in space.threatenedBy:
                        if threat.get_team() == -team:
                            KCastle = False
                            break
                    if not KCastle:
                        break
            if QCastle:
                for space in [king, self.b[5][king.y], self.b[6][king.y]]:
                    for threat in space.threatenedBy:
                        if threat.get_team() == -team:
                            QCastle = False
                            break
                    if not QCastle:
                        break
            
            # finally, if all passed, then add as legal move
            if KCastle:
                king.mark_move(self.b[2][king.y])
            if QCastle:
                king.mark_move(self.b[6][king.y])

    # if enpassant is legal, add to list of allowed moves
    def update_enpassant(self):
        if self.count <= 0:
            return
        prevRemove = self.removes[self.count - 1]
        prevAdd = self.adds[self.count - 1]
        if len(prevRemove) != 1:
            return
        unit, piece = prevRemove[0]
        dest, space = prevAdd[0]
        # if previous move was a pawn moving two forward
        if unit == WPawn and piece.y == 1 and space.y == 3:
            file = space.x
            # check the files next to the pawn. if enemy pawn there, add to moves
            if file > 0 and self.b[space.x - 1][space.y].unit == BPawn:
                self.b[space.x - 1][space.y].mark_move(self.b[space.x][2])
            if file < 7 and self.b[space.x + 1][space.y].unit == BPawn:
                self.b[space.x + 1][space.y].mark_move(self.b[space.x][2])
        elif unit == BPawn and piece.y == 6 and space.y == 4:
            file = space.x
            if file > 0 and self.b[space.x - 1][space.y].unit == WPawn:
                self.b[space.x - 1][space.y].mark_move(self.b[space.x][5])
            if file < 7 and self.b[space.x + 1][space.y].unit == WPawn:
                self.b[space.x + 1][space.y].mark_move(self.b[space.x][5])    
   
    # takes a two character string and attempts to parse a coordinate, raising ValueError if it can't
    def parse_coord(self, string):
        if len(string) != 2:
            raise ValueError
        try: 
            file = parse_x_char(string[0])
            rank = parse_y_char(string[1])
            if rank >= 0 and rank < 8 and file >= 0 and file < 8:
                return(self.b[file][rank])
            else:
                raise ValueError
        except ValueError:
            raise ValueError # lol

    # takes a string and attempts to parse a move from it. returns the piece and space
    # raises MoveError if string can't be parsed or move isn't found to be legal or move is ambiguous
    def parse_move(self, string):
        length = len(string)
        if length < 2:
            raise MoveError("algebraic notation needs at least two characters!")
        turn = self.get_turn()
        army = self.get_army(turn)

        # queenside castle
        if length >= 5 and (string[0:5] == "O-O-O" or string[0:5] == "0-0-0"):
            if turn == W:
                space = self.b[2][0]
                for piece in space.canMoveTo:
                    if piece.unit == WKing and piece.x == 4:
                        return piece, space
            else:
                space = self.b[2][7]            
                for piece in space.canMoveTo:
                    if piece.unit == BKing and piece.x == 4:
                        return piece, space
            raise MoveError("queenside castle not possible!")
        
        # kingside castle
        if length >= 3 and (string[0:3] == "O-O" or string[0:3] == "0-0"):
            if turn == W:
                space = self.b[6][0]
                for piece in space.canMoveTo:
                    if piece.unit == WKing and piece.x == 4:
                        return piece, space
            else:
                space = self.b[6][7]
                for piece in space.canMoveTo:
                    if piece.unit == BKing and piece.x == 4:
                        return piece, space
            raise MoveError("kingside castle not possible!")        
        
        # attempt to parse a coordinate from the string, starting from the back
        index = length - 1
        while index >= 0:
            index -= 1
            try:
                space = self.parse_coord(string[index:(index + 2)])
                break           
            except ValueError:
                # if no coordinate to be found, try parsing pawn caps like 'exd' or 'ed'
                if index == 0:
                    try:
                        home = parse_x_char(string[0])
                        if string[1] == 'x' and length >= 3:
                            target = parse_x_char(string[2])
                        else:
                            target = parse_x_char(string[1])
                        save = []
                        for pawn in army[Pawn]:
                            if pawn.x == home:
                                for space in pawn.moves:
                                    if space.x == target:
                                        save.append((pawn, space))
                        saveLen = len(save)
                        if saveLen < 1:
                            raise MoveError("there's no Pawn in " + x_char(home) + " that moves to " + x_char(target))
                        elif saveLen == 1:
                            return save[0][0], save[0][1]
                        elif saveLen > 1:
                            raise MoveError("that's an ambiguous pawn move from " + x_char(home) + " to " + x_char(target)) 
                    except ValueError:
                        raise MoveError("couldn't parse a move from your input!")
                    raise MoveError("couldn't parse a move from your input!")

        # if the only coordinate is the first chars, assume that it's a pawn moving forward
        if index == 0:
            unit = Pawn
            col = space.x
        # otherwise, attempt to parse piece identity from first letter
        else:
            try:
                unit = parse_id_char(string[0])
                if string[0] == 'P':
                    col = space.x
                elif unit == Pawn:
                    col = parse_x_char(string[0])
            except ValueError:
                raise MoveError("the first letter doesn't represent a piece!")
                
        #if promotion, attempt to parse an "=Q" or "(Q" or some other letter
        if unit == Pawn and  space.y == 0 or space.y == 7:
            self.promotion = Queen
            index += 2
            while index <= length - 2:
                if string[index] == "=" or string[index] == "(":
                    try:
                        self.promotion = parse_id_char(string[index + 1])
                        if self.promotion == Pawn:
                            raise MoveError("you can't promote to a pawn!")
                        elif self.promotion == King:
                            raise MoveError("you can't promote to a king!")
                        break
                    except ValueError:
                        break
                index += 1
        
        # build a list of all pieces of correct type that can move there
        save = []
        for piece in space.canMoveTo:
            if piece.unit == unit * turn:
                save.append(piece)
        saveLen = len(save)
        if saveLen < 1:
            raise MoveError("no " + unit_string(unit) + " can move there!")
        elif saveLen == 1:                    
            return save[0], space
        # if it's ambiguous
        elif saveLen > 1:
            if unit == Pawn:
                for piece in save:
                    if piece.x == col:
                        return piece, space
            save2 = []
            # if there are no more characters between piece id and coordinate
            if index < 2:
                raise MoveError("you need to disambiguate your " + unit_string(unit) + "s!")
            try:
                # attempt to disambiguate by file
                file = parse_x_char(string[1])
                for piece in save:
                    if piece.x == file:
                        save2.append(piece)
                save2Len = len(save2)
                if save2Len < 1:
                    raise MoveError("no " + unit_string(unit) + " piece has that file!")
                elif save2Len == 1:
                    return save2[0], space
                # if still ambiguous attempt, to disambiguate by rank too
                elif save2Len > 1:
                    if index < 2:
                        raise MoveError("you need to disambiguate your " + unit_string(unit) + "s by rank too!")
                    try:
                        rank = parse_y_char(string[2])
                        for piece in save2:
                            if piece.y == rank:
                                return piece, space
                    except ValueError:
                        raise MoveError("no " + unit_string(unit) + " has that rank and file!")
            except ValueError:
                # if that didn't work, attempt to disambiguate by rank
                try: 
                    rank = parse_y_char(string[1])
                    for piece in save:
                        if piece.y == rank:
                            save2.append(piece)
                    save2Len = len(save2)
                    if save2Len < 1:
                        raise MoveError("no " + unit_string(unit) + " has that rank!")
                    elif save2Len == 1:
                        return save2[0], space
                    elif save2Len > 1:
                        raise MoveError("you need to disambiguate your " + unit_string(unit) + "s by file and rank!")
                except ValueError:
                    raise MoveError("you didn't disambiguate your " + unit_string(unit) + "s correctly!")

    # takes a piece and space and converts it into adds, removes, and a string sans checking and mating
    def convert_move(self, piece, space):
        unit = piece.unit
        turn = self.get_turn()
        if turn == W:
            homeRank = 0
        else:
            homeRank = 7
        
        # KCastle
        if unit * turn == King and piece.x == 4 and piece.y == homeRank and space.x == 6:
            removes = [(unit, piece), (Rook * turn, self.b[7][homeRank])]
            adds = [(unit, space), (Rook * turn, self.b[5][homeRank])]
            return (adds, removes, "O-O")

        # QCastle
        elif unit * turn == King and piece.x == 4 and piece.y == homeRank and space.x == 2:
            removes = [(unit, piece), (Rook * turn, self.b[0][homeRank])]
            adds = [(unit, space), (Rook * turn, self.b[3][homeRank])]
            return (adds, removes, "O-O-O")

        capture = False
        enpassant = False
        promotion = No
        ambiguity = ""        
            
        # remember if it's a capture
        if space.unit != No:
            capture = True
            captured = space.unit

        # detect enpassant by pawn moving diagonal but it not being capture
        if not capture and unit * turn == Pawn and space.x != piece.x:
            enpassant = True
            lostPawn = self.b[space.x][piece.y]
            
        # if it's a promotion, get the piece that it's promoting to, defaulting to queen
        elif unit * turn == Pawn and (space.y == 0 or space.y == 7):
            promotion = self.get_promotion() * turn

        # decode ambiguity for string
        elif unit * turn != Pawn:
            save = []
            for possible in space.canMoveTo:
                if possible.unit == piece.unit and possible != piece:
                    save.append(possible)
            # if something else in the same rank, specify file
            for possible in save:
                if possible.y == piece.y:
                    ambiguity = x_char(piece.x)
                    break
            # if something else in the same file, specify rank
            for possible in save:    
                if possible.x == piece.x:
                    ambiguity += y_char(piece.y)
                    break
            # if no pieces in same rank or file, specify file only
            if len(save) > 0 and len(ambiguity) == 0:
                ambiguity = x_char(piece.x)
        
        # calculate adds and removes
        if capture:
            removes = [(unit, piece), (captured, space)]
        elif enpassant:
            removes = [(unit, piece), (-unit, lostPawn)]
        else:
            removes = [(unit, piece)]
        
        if promotion:
            adds = [(promotion, space)]
        else:
            adds = [(unit, space)]
        
        # build the string
        string = ""
        unit = abs(unit)
        if unit == Pawn and (capture or enpassant):
            string = x_char(piece.x)
        else:
            if unit != Pawn and promotion == No:
                string = unit_char(unit)
            string += ambiguity
        if capture or enpassant:
            string += "x"
        string += space.coord_string()
        if promotion != No:
            string += "=" + unit_char(promotion)
        elif enpassant:
            string += "e.p."
        return adds, removes, string
    
    # takes a move and attempts to execute, raising MoveError if it puts self in check
    # if successful, updates logs, checks for stalemates and mates, and returns the game state
    def execute(self, piece, space):
        # disallow move if it isn't explicitly allowed, which prevents putting self in check
        allowed = False
        for (legalPiece, legalSpace) in self.legalMoves:
            if legalPiece == piece and legalSpace == space:
                allowed = True
                break
        if not allowed:
            if self.is_check():
                raise MoveError("You're in check!")
            raise MoveError("This would put yourself in check!")
    
        # convert to adds and removes
        adds, removes, string = game.convert_move(piece, space)

        # actually move around the pieces        
        self.enact(adds, removes)

        # reextract if it was a capture, and save for stalemating
        if len(removes) > len(adds):
            self.lastCapture = self.count

        # log adds and removes so moves can be calculated
        self.count += 1
        self.adds.append(adds)
        self.removes.append(removes)

        # recalculate moves and see the game state
        state = self.update()

        # modify string if it's a check or mate
        if abs(state) == Wins:
            string += "#"
        elif abs(state) == Checks:
            string += "+"        
        self.log.append(string)

        return state
            
    # reverts a move, returning game state raising MoveError if can't undo (nothing to undo)
    def undo(self):
        if self.count == 0:
            raise MoveError("there are no more moves to undo!")
        
        # pop a turn off of all the histories
        adds = self.adds.pop()
        removes = self.removes.pop()
        string = self.log.pop()
        
        # add and remove pieces in reverse
        self.enact(removes, adds)
        
        # regress the turn counter, refind the index of last capture if necessary
        self.count -= 1
        if self.lastCapture >= self.count:
            for index in range(self.count - 1, -1, -1):
                if len(self.removes[index]) > len(self.adds[index]):
                    if team_of_unit(self.removes[index][0][0]) != team_of_unit(self.removes[index][1][0]):
                        self.lastCapture = index
                        break
            if self.lastCapture >= self.count:
                self.lastCapture = -1
        
        # update moves to what it was earlier
        return game.update()
    
    # calculates moves, returning the state of the game    
    def update(self):        
        # calculate all moves possible
        game.update_moves()

        # marks if puts enemy in check
        check = False
        if self.is_check():
            check = True

        # marks if enemy has no legal moves (either stalemate or checkmate)
        noMoves = False
        if len(self.legalMoves) == 0:
            noMoves = True        
        
        # draw if only kings left
        stalemate = True
        for unitIndex in [Queen, Rook, Knight, Bishop, Pawn]:
            if len(self.white[unitIndex]) > 0 or len(self.black[unitIndex]) > 0:
                stalemate = False
                break
        
        # draw if 100 moves since last capture
        if self.count - self.lastCapture > 100:
            stalemate = True
            
        # draw if threefold repetition. slightly inaccurate, as it only checks last three board states
        if self.count >= 8 and self.count - self.lastCapture > 8 and self.is_unproductive(self.count - 1) and self.is_unproductive(self.count - 2) and self.is_unproductive(self.count - 5) and self.is_unproductive(self.count - 6): 
            stalemate = True

        if stalemate:
            return Stalemate
        elif check and noMoves:
            return Wins * -self.get_turn()
        elif check:
            return Checks * -self.get_turn()
        elif noMoves:
            return Stalemate
        else:
            return Ok

    def get_turn(self):
        if self.count % 2:
            return B
        else:
            return W
    def get_army(self, team = 0):
        if team == 0:
            team = self.get_turn()
        if team == W:
            return self.white
        elif team == B:
            return self.black
    def is_check(self, team = 0):
        if team == 0:
            team = self.get_turn()
        if team == W:
            return len(self.white[King][0].threatenedBy) > 0
        elif team == B:
            return len(self.black[King][0].threatenedBy) > 0
            
    # returns True if at specified history index piece is returning to where it was right before without capturing
    def is_unproductive(self, index):
        if index < 2:
            return False
        if len(self.removes[index]) > 1 or len(self.removes[index - 2]) > 1:
            return False
        add = self.adds[index][0]
        remove = self.removes[index][0]
        prevAdd = self.adds[index - 2][0]
        prevRemove = self.removes[index - 2][0]
        if add[1] == prevRemove[1] and prevAdd[1] == remove[1] and add[0] == prevAdd[0]:
            return True
        return False
    
    # just looking at board state, counts the number of enemy pieces threatening it. used for checking
    def hypothetical_threat(self, piece):
        threats = 0
        if piece.unit == No:
            return False
        team = piece.get_team()
        enemy = team * -1
        for space in piece.nKnight:
            if space.unit == Knight * enemy:
                threats += 1
        for arr in piece.nHoriz:
            for space in arr:
                if space.unit == Rook * enemy or space.unit == Queen * enemy:
                    threats += 1
                    break
                elif space.unit != No:
                    break
            if len(arr) > 0 and arr[0].unit == King * enemy:
                threats += 1
        for arr in piece.nDiag:
            for space in arr:
                if space.unit == Bishop * enemy or space.unit == Queen * enemy:
                    threats += 1
                    break
                elif space.unit != No:
                    break
            if len(arr) > 0 and arr[0].unit == King * enemy:
                threats += 1
        if team == W:
            if len(piece.nDiag[0]) > 0 and piece.nDiag[0][0].unit == BPawn:
                threats += 1                
            if len(piece.nDiag[3]) > 0 and piece.nDiag[3][0].unit == BPawn:
                threats += 1
        elif team == B:
            if len(piece.nDiag[1]) > 0 and piece.nDiag[1][0].unit == WPawn:
                threats += 1
            if len(piece.nDiag[2]) > 0 and piece.nDiag[2][0].unit == WPawn:
                threats += 1
        return threats
    
    # possible container for UI interaction for getting promotion
    def get_promotion(self):
        return self.promotion
        
game = Game()
game.fill_board()
state = game.update()

while True:
    game.print_board()
    if game.count > 0:
        line = "Previous: "
        line += str(int((game.count + 1)/ 2))
        if game.get_turn() == W:
            line += "... "
        else:
            line += ". "
        line += game.log[game.count - 1]
        print line
    input = raw_input(" Command: ")
    if input == "quit" or input == "exit" or input == "q":
        exit()
    elif input == "help":
        print "Input: algebraic notation, 'undo', 'resign', 'list', 'history', 'moves', 'quit'"
    elif input == "reset":
        game = Game()
        game.fill_board()
        game.update_moves()
    elif input == "moves":
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
    elif input == "log" or input == "history":        
        line = ""
        for turn in range(game.count):            
            if turn % 2 == 0:
                line = str(int(turn / 2) + 1) + ". " + game.log[turn]
            else:
                print line + " " + game.log[turn]
                line = ""
        if game.count % 2:
            print line
    elif input == "list":
        length = len(game.legalMoves)
        for index in range(length):
            piece, space = game.legalMoves[index]
            print str(index + 1) + ": " + unit_string(piece.unit) + " at " + piece.coord_string() + " to " + space.coord_string()
        numStr = raw_input("which move number? ")
        try:
            num = int(numStr)
            if num > 0 and num <= length:
                piece, space = game.legalMoves[num - 1]
                state = game.execute(piece, space)
        except ValueError:
            print "that's not a number!"
    elif input == "resign":
        state = game.get_turn() * Wins * -1
    elif input == "undo":
        try:
            state = game.undo()
        except MoveError, (instance):
            print instance.parameter
    else:
        try:
            piece, space = game.parse_move(input)            
            state = game.execute(piece, space)
        except MoveError, (instance):
            print instance.parameter
    
    
    if state == WWins:
        print "White wins! 'quit' or 'reset'"
    elif state == BWins:
        print "Black wins! 'quit' or 'reset'"
    elif state == Stalemate:
        print "Stalemate. 'quit' or 'reset'"