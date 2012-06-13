""" 
chess.py

Peter Hung
060612-
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
    letters = ["K", "Q", "R", "N", "B", "P"]
    return letters[abs(unit) - 1]
def unit_string(unit):
    strings = ["King", "Queen", "Rook", "Knight", "Bishop", "Pawn"]
    return strings[abs(unit) - 1]
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
    def __init__(self, game, x, y):
        self.game = game
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
            self.nKnight.append(self.game.b[x][y])
    def set_neighbors(self):
        # print "space " + str(self.x) + " " + str(self.y)
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
                self.b[i][j] = Space(self, i, j)
        for i in range(8):
            for j in range(8):
                self.b[i][j].set_neighbors()
        
        # set up the history, turn count, and everything
        self.white = [[], [], [], [], [], [], []]
        self.black = [[], [], [], [], [], [], []]
        self.count = 0
        self.removes = []
        self.adds = []
        self.log = []
               
        # TODO: no progress counter
        
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
                line += self.b[j][i].unit_draw()
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
        self.update_castle(self.white[King][0])
        self.update_castle(self.black[King][0])
        self.update_enpassant()
        # TODO: enpassant checking
        
        # TODO: draw if only kings left
        # TODO: draw if 100 cycles gone without capturing
        # TODO: win if mate
        
    # if the castles are legal for passed king, add to list of allowed moves
    def update_castle(self, king):
        team = king.get_team()
        KCastle = False
        QCastle = False
        # if king is in original space, move on
        if team == W and king.x == 4 and king.y == 0:
            KRook = self.b[0][0]
            QRook = self.b[7][0]
        elif team == B and king.x == 4 and king.y == 7:
            KRook = self.b[0][7]
            QRook = self.b[7][7]
        else:
            return
            
        # ensure that the rook unmoved can see king. that means intervening spaces empty
        for piece in king.protectedBy:
            if piece == KRook and abs(piece.unit) == Rook:
                KCastle = True
            if piece == QRook and abs(piece.unit) == Rook:
                QCastle = True
                
        if KCastle == False and QCastle == False:        
            return
            
        # look into history to see if king or rooks have been moved
        for ls in self.removes:
            for unit, space in ls:
                if KCastle and space == KRook:
                    KCastle = False
                elif QCastle and space == QRook:
                    QCastle = False
                elif space == king:
                    return
                elif KCastle == False and QCastle == False:        
                    return
                    
        # check if any of three spaces are threatened
        if KCastle:
            for space in [king, self.b[3][king.y], self.b[2][king.y]]:
                for threat in space.threatenedBy:
                    if threat.get_team() == -team:
                        KCastle = False
                        break
        if QCastle:
            for space in [king, self.b[5][king.y], self.b[6][king.y]]:
                for threat in space.threatenedBy:
                    if threat.get_team() == -team:
                        QCastle = False
                        break
        
        # finally, if all passed, then add as legal move
        if KCastle:
            king.mark_move(self.b[2][king.y])
        if QCastle:
            king.mark_move(self.b[6][king.y])

    # if enpassant is legal, add to list of allowed moves
    def update_enpassant(self):
        if self.count == 0:
            return
        prevRemove = self.removes[self.count - 1]
        prevAdd = self.adds[self.count - 1]
        if len(prevRemove) != 1:
            return
        unit, piece = prevRemove[0]
        dest, space = prevAdd[0]
        if unit == WPawn and piece.y == 1 and space.y == 3:
            file = space.x            
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
   
    # takes a string and attempts to parse it. returns the piece and space
    # raises MoveError if string can't be parsed or move isn't found to be legal
    def parse_move(self, s):
        length = len(s)
        if length < 2:
            raise MoveError("algebraic notation needs at least two characters!")
        turn = self.whose_turn()
        army = self.black
        if turn == W:
            army = self.white

        # queenside castle
        if length >= 5 and (s[0:5] == "O-O-O" or s[0:5] == "0-0-0"):
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
        if length >= 3 and (s[0:3] == "O-O" or s[0:3] == "0-0"):
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
        index = len(s) - 1
        while index >= 0:
            index -= 1
            try:
                space = self.parse_coord(s[index:(index + 2)])
                break
            except ValueError:
                if index == 0:
                    raise MoveError("couldn't find a coordinate!")                                            

        # if the only coordinate is the first one, assume piece is a pawn moving straight 
        if index == 0:
            unit = Pawn
            for piece in space.canMoveTo:
                if piece.unit == Pawn * turn and piece.x == space.x:                    
                    return piece, space # TODO: this is going to break when it's an en passant
            raise MoveError("no pawn can move straight there!")
        # otherwise, attempt to parse piece identity
        try:
            unit = parse_id_char(s[0])
            if unit == Pawn:
                col = parse_x_char(s[0])
        except ValueError:
            raise MoveError("the first letter doesn't represent a piece!")

            # if it's pawn capturing, then ambiguity already defined
        if unit == Pawn:
            for piece in space.canMoveTo:
                if piece.unit == unit * turn and piece.x == col:
                    return piece, space
            raise MoveError("no pawn in specified column can capture there!")
        
        # if it's some other piece
        else:
            save = []
            for piece in space.canMoveTo:
                if piece.unit == unit * turn:
                    save.append(piece)
            count = len(save)
            if count < 1:
                raise MoveError("no " + unit_string(unit) + " can move there!")
            elif count == 1:                    
                return save[0], space
            # if it's ambiguous
            elif count > 1:
                save2 = []
                if index < 2:
                    raise MoveError("you need to disambiguate!")
                try:
                    # attempt to disambiguate by file
                    file = parse_x_char(s[1])
                    for piece in save:
                        if piece.x == file:
                            save2.append(piece)
                    count2 = len(save2)
                    if count2 < 1:
                        raise MoveError("no piece has that file!")
                    elif count2 == 1:
                        return save2[0], space
                    # if still ambiguous attempt, to disambiguate by rank too
                    elif count2 > 1:
                        if index < 2:
                            raise MoveError("you need to disambiguate by rank too!")
                        try:
                            rank = parse_y_char(s[2])
                            for piece in save2:
                                if piece.y == rank:
                                    return piece, space
                        except ValueError:
                            raise MoveError("no piece has that rank and file!")                    
                except ValueError:
                    try: 
                        rank = parse_y_char(s[1])
                        for piece in save:
                            if piece.y == rank:
                                save2.append(piece)
                        count2 = len(save2)
                        if count2 < 1:
                            raise MoveError("no piece has that rank!")
                        elif count2 == 1:
                            return save2[0], space
                        elif count2 > 1:
                            raise MoveError("you need to disambiguate by file and rank!")
                    except ValueError:
                        raise MoveError("you didn't disambiguate the move correctly!")
        
    def execute_move(self, piece, space):
        # TODO: promotion
        unit = piece.unit
        capture = False
        check = False
        mate = False
        enpassant = False
        promotion = No
        kCastle = False
        qCastle = False
        ambiguity = ""
        turn = self.whose_turn()
        if turn == W:
            army = self.white
            enemy = self.black
            homeRank = 0
        else:
            army = self.black
            enemy = self.white
            homeRank = 7
        # remember if it's a capture
        if space.unit != No:
            capture = True
            captured = space.unit
        
        # KCastle
        if unit * turn == King and piece.x == 4 and piece.y == homeRank and space.x == 6:
            rook = self.b[7][homeRank]
            rookDestination = self.b[5][homeRank]
            self.put(unit, space)
            self.remove(piece)
            self.put(Rook * turn, rookDestination)
            self.remove(rook)            
            # save to history
            self.removes.append([(unit, piece), (Rook * turn, rook)])
            self.adds.append([(unit, space), (Rook * turn, rookDestination)])
            kCastle = True

        # QCastle
        elif unit * turn == King and piece.x == 4 and piece.y == homeRank and space.x == 2:
            rook = self.b[0][homeRank]
            rookDestination = self.b[3][homeRank]
            self.put(unit, space)
            self.remove(piece)
            self.put(Rook * turn, rookDestination)
            self.remove(rook)        
            # save to history
            self.removes.append([(unit, piece), (Rook * turn, rook)])
            self.adds.append([(unit, space), (Rook * turn, rookDestination)])
            qCastle = True
            
        else:
            # detect enpassant by pawn moving diagonal but it not being capture
            if not capture and unit == Pawn and space.x != piece.x:
                enpassant = True
                lostPawn = self.b[space.x][piece.y]

            # decode ambiguity for later
            save = []
            for possible in space.canMoveTo:
                if possible.unit == piece.unit and possible != piece:
                    print possible.coord_string()
                    save.append(possible)
            saveLen = len(save)
            if saveLen == 1:
                if save[0].x == piece.x:
                    ambiguity = y_char(piece.y)
                else:
                    ambiguity = x_char(piece.x)
            elif saveLen > 1:      
                for possible in save:                
                    if possible.y == piece.y:
                        ambiguity = x_char(piece.x)
                        break
                for possible in save:    
                    if possible.x == piece.x:
                        ambiguity += y_char(piece.y)
                        break
            
            # actually move the piece
            if capture:
                self.remove(space)
            elif enpassant:
                self.remove(lostPawn)
            self.put(unit, space)
            self.remove(piece)
            
            # if puts self in check, disallow it
            if self.hypothetical_threat(army[King][0]):
                self.remove(space)
                self.put(unit, piece)
                if capture:
                    self.put(captured, space)
                elif enpassant:
                    self.put(-unit, lostPawn)
                raise MoveError("This would put yourself in check!")
            
            # save the history
            if capture:
                self.removes.append([(unit, piece), (captured, space)])
            elif enpassant:
                self.removes.append([(unit, piece), (-unit, lostPawn)])
            else:
                self.removes.append([(unit, piece)])
            self.adds.append([(unit, space)])
                
        if self.hypothetical_threat(enemy[King][0]):
            print "check!"
            check = True
        # TODO: if mate
        
        # build the string and save it
        string = self.move_string(piece, space, capture, check, mate, kCastle, qCastle, promotion, ambiguity, enpassant)
        self.log.append(string)
        print string

        # progress the turn counter
        self.count += 1
        return True
    def undo_move(self):
        if self.count == 0:
            raise MoveError("there are no more moves to undo!")
        # regress the turn counter
        self.count -= 1
        # remove the moved pieces
        for unit, loc in self.adds.pop():
            self.remove(loc)
        # add back all the pieces that were removed
        for unit, loc in self.removes.pop():
            self.put(unit, loc)
        self.log.pop()
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
    def move_string(self, piece, space, capture = False, check = False, mate = False, kscastle = False, qscastle = False, promotion = No, ambiguity = "", enpassant = False):
        string = ""
        unit = abs(space.unit)
        # if castles, just start with that
        if kscastle:
            string = "0-0"
        elif qscastle:
            string = "0-0-0"
        
        # if pawn capturing or enpassanting, need letter
        elif unit == Pawn and (capture or enpassant):
            string = x_char(piece.x)
        # any other piece takes letter
        else:            
            if unit != Pawn:
                string = unit_char(unit)
                
            # add preparsed disambiguation
            string += ambiguity
        
        # if capture, notate it so
        if capture or enpassant:
            string += "x"
        
        # add the coordinate
        if not kscastle and not qscastle:
            string += space.coord_string()
        
        # if it's a promotion, add the piece identity
        if promotion != No:
            string += "=" + unit_char(promotion)
        elif enpassant:
            string += "e.p."
        
        # if mate or check, add appropriate symbol
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
    
    # without recalculating everything, checks if the piece is threatened enemy pieces
    def hypothetical_threat(self, piece):
        if piece.unit == No:
            return False
        team = piece.get_team()
        enemy = team * -1
        for space in piece.nKnight:
            if space.unit == Knight * enemy:
                return True
        for arr in piece.nHoriz:
            for space in arr:
                if space.unit == Rook * enemy or space.unit == Queen * enemy:
                    return True
                    break
                elif space.unit != No:
                    break
            if len(arr) > 0 and arr[0].unit == King * enemy:
                return True        
        for arr in piece.nDiag:
            for space in arr:
                if space.unit == Bishop * enemy or space.unit == Queen * enemy:
                    return True
                    break
                elif space.unit != No:
                    break
            if len(arr) > 0 and arr[0].unit == King * enemy:
                return True
        if team == W:
            if len(piece.nDiag[0]) > 0 and piece.nDiag[0][0].unit == BPawn:
                return True
            if len(piece.nDiag[3]) > 0 and piece.nDiag[3][0].unit == BPawn:
                return True
        elif team == B:
            if len(piece.nDiag[1]) > 0 and piece.nDiag[1][0].unit == WPawn:
                return True
            if len(piece.nDiag[2]) > 0 and piece.nDiag[2][0].unit == WPawn:
                return True
        return False
        
        
game = Game()
game.fill_board()

""" 
# disambiguity checking
game.put(WKnight, game.b[0][0])
game.put(WKnight, game.b[0][2])
game.put(WKnight, game.b[4][0])
game.put(BKing, game.b[7][7])
game.put(WKing, game.b[7][0])
"""


while True:
    game.print_board()
    game.update_moves()
    string = raw_input("Command: ")
    if string == "quit" or string == "exit" or string == "q":
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
                line = unit_string(piece.unit) + " at " + piece.coord_string() + " can move to "
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
            piece, space = game.parse_move(string)
            game.execute_move(piece, space)
        except MoveError, (instance):
            print instance.parameter
