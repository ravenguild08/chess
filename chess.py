""" 
chess.py

Peter Hung
060612-
for shits and giggles
"""

import random
import unittest

# enums
BPawn, BBishop, BKnight, BRook, BQueen, BKing, No, WKing, WQueen, WRook, WKnight, WBishop, WPawn = range(-6, 7)
King, Queen, Rook, Knight, Bishop, Pawn = range(1, 7)
B, W = [-1, 1]
    
class Space():
    def __init__(self, board, x, y):
        self.board = board
        self.x = x
        self.y = y
        self.nHoriz = [[],[],[],[]]
        self.nDiag = [[],[],[],[]]
        self.nKnight = []
        self.piece = No
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
        if self.piece < 0:
            return B
        elif self.piece > 0:
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
        if self.piece == No:
            return list
        elif abs(self.piece) == King:
            for i in range(4):
                self.add_first_moves(self.nHoriz[i], list)
                self.add_first_moves(self.nDiag[i], list)
            # TODO: castle
        elif abs(self.piece) == Queen:
            for i in range(4):
                self.add_row_moves(self.nHoriz[i], list)
                self.add_row_moves(self.nDiag[i], list)
        elif abs(self.piece) == Rook:
            for i in range(4):
                self.add_row_moves(self.nHoriz[i], list)
        elif abs(self.piece) == Knight:
            team = self.get_team()
            for space in self.nKnight:                
                if team != space.get_team():
                    list.append(space)
        elif abs(self.piece) == Bishop:
            for i in range(4):
                self.add_row_moves(self.nDiag[i], list)
        elif self.piece == WPawn:
            if self.y == 7:
                # TODO: promote
                
                return []
            if self.board[self.x][self.y + 1].piece == No:
                list.append(self.board[self.x][self.y + 1])
                if self.y == 1 and self.board[self.x][3].piece == No:
                    list.append(self.board[self.x][3])
            if self.x < 7 and self.board[self.x + 1][self.y + 1].get_team() == B:
                list.append(self.board[self.x + 1][self.y + 1])
            if self.x > 0 and self.board[self.x - 1][self.y + 1].get_team() == B:
                list.append(self.board[self.x - 1][self.y + 1])
            # TODO: en pessant
            
        elif self.piece == BPawn:
            if self.y == 0:
                # TODO: promote
                
                return []
            if self.board[self.x][self.y - 1].piece == No:
                list.append(self.board[self.x][self.y - 1])
                if self.y == 6 and self.board[self.x][4].piece == No:
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
        return ['a','b','c','d','e','f','g','h'][self.x] + str(self.y + 1)
    def x_string(self):
        return ['a','b','c','d','e','f','g','h'][self.x]
    def y_string(self):
        return str(self.y + 1)
    def id_string(self):
        letters = ["K", "Q", "R", "N", "B", "P"]
        return letters[abs(self.piece) - 1]
    def piece_string(self):
        if self.piece == 0:
            return "  "
        elif self.piece < 0:
            return " " + self.id_string()
        else:
            return self.id_string() + " "
    def move_string(self, space):
        string = ""
        if space not in self.moves:
            return string
        # TODO: castle
        
        # if not pawn, need letter
        if abs(self.piece) != Pawn:
            string += self.id_string()
        # pawn capture takes file
        elif space.piece != No:
            string += self.x_string()

        # TODO: ambiguity; check if other pieces can go there

        # if capture
        if space.piece != No:
            string += "x"
        
        string += space.coord_string()
        
        # TODO: promotion
        
        # TODO: mate check
        
        return string
            
            
        
def init_board():
    board = {}
    for i in range(8):
        board[i] = {}
        for j in range(8):
            board[i][j] = Space(board, i, j)
    for i in range(8):
        for j in range(8):
            board[i][j].set_neighbors()
    return board
def fill_board(board):
    board[0][0].piece = WRook
    board[1][0].piece = WKnight
    board[2][0].piece = WBishop
    board[3][0].piece = WQueen
    board[4][0].piece = WKing
    board[5][0].piece = WBishop
    board[6][0].piece = WKnight
    board[7][0].piece = WRook
    board[0][7].piece = BRook
    board[1][7].piece = BKnight
    board[2][7].piece = BBishop
    board[3][7].piece = BQueen
    board[4][7].piece = BKing
    board[5][7].piece = BBishop
    board[6][7].piece = BKnight
    board[7][7].piece = BRook
    for i in range(8):
        board[i][1].piece = WPawn
        board[i][6].piece = BPawn
    return
def print_board(board):
    print " "
    print "     a  b  c  d  e  f  g  h  "
    print "   +--+--+--+--+--+--+--+--+ "
    for i in range(7, -1, -1):
        line = " " + str(i + 1) + " |"
        for j in range(8):
            line += board[j][i].piece_string()
            line += "|"
        line += " " + str(i + 1)
        print line
        print "   +--+--+--+--+--+--+--+--+"
    print "    a  b  c  d  e  f  g  h   "
    print " "
    return

board = init_board()
fill_board(board)

"""
random.seed()
for i in range(8):
    for j in range(8):
        if random.randint(0, 1):
            board[i][j].piece = random.randint(BPawn, WPawn)
"""

print_board(board)
for i in range(8):
    for j in range(8):
        p = board[i][j]
        if p.get_team() == W:
            for space in p.get_moves():
                print p.move_string(space)