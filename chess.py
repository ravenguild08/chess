class Piece():
    BPawn, BBishop, BKnight, BRook, BQueen, BKing, No, WKing, WQueen, WRook, WKnight, WBishop, WPawn = range(-6, 7)
B = -1
W = 1
    
class Space():
    def __init__(self, board, x, y):
        self.board = board
        self.x = x
        self.y = y
        self.nHoriz = [[],[],[],[]]
        self.nDiag = [[],[],[],[]]
        self.nKnight = []
        self.piece = Piece.No
    def add_iff_legal(self, x, y):
        if x >= 0 and x < 8 and y >= 0 and y < 8:
            self.nKnight.append(self.board[x][y])
    def set_neighbors(self):
        # print "space " + str(self.x) + " " + str(self.y)
        for n in range(self.y + 1, 8):
            self.nHoriz[0].append(self.board[self.x][n])
        for s in range(self.y - 1, -1, -1):
            self.nHoriz[1].append(self.board[self.x][s])        
        for e in range(self.x + 1, 8):
            self.nHoriz[2].append(self.board[e][self.y])
        for w in range(self.x - 1, -1, -1):
            self.nHoriz[3].append(self.board[w][self.y])
        # ne
        x = self.x + 1
        y = self.y + 1
        while x < 8 and y < 8:
            self.nDiag[0].append(self.board[x][y])
            x += 1
            y += 1
        # nw
        x = self.x - 1
        y = self.y + 1
        while x >= 0 and y < 8:
            self.nDiag[1].append(self.board[x][y])
            x -= 1
            y += 1
        # se
        x = self.x + 1
        y = self.y - 1
        while x < 8 and y >= 0:
            self.nDiag[2].append(self.board[x][y])
            x += 1
            y -= 1
        # sw
        x = self.x - 1
        y = self.y - 1
        while x >= 0 and y >= 0: 
            self.nDiag[3].append(self.board[x][y])
            x -= 1
            y -= 1
        self.add_iff_legal(self.x + 2, self.y + 1)
        self.add_iff_legal(self.x + 2, self.y - 1)
        self.add_iff_legal(self.x + 1, self.y + 2)
        self.add_iff_legal(self.x + 1, self.y - 2)
        self.add_iff_legal(self.x - 2, self.y + 1)
        self.add_iff_legal(self.x - 2, self.y - 1)
        self.add_iff_legal(self.x - 1, self.y + 2)
        self.add_iff_legal(self.x - 1, self.y - 2)
        return
    def add_first_moves(self, arr, list):
        if not arr:
            return list
        team = self.get_team()
        space = arr[0]
        spaceTeam = space.get_team()
        # clash with own piece
        if team == spaceTeam:
            return list
        # can capture other piece
        elif team == -spaceTeam:
            return list.append(space)
        # blank
        else:
            return list.append(space)
    def add_row_moves(self, arr, list):
        if not arr:
            return list
        team = self.get_team()
        for space in arr:
            spaceTeam = space.get_team()
            # clash with own piece
            if team == spaceTeam:
                return list
            # can capture other piece
            elif team == -spaceTeam:
                list.append(space)
                return list
            # otherwise, add to list and keep on going
            else:
                list.append(space)
        return list
            
    
    def coord_string(self):
        return ['a','b','c','d','e','f','g','h'][self.x] + str(self.y + 1)
    def to_string(self):
        letters = ["K", "Q", "R", "N", "B", "P"]
        if self.piece == 0:
            return "  "
        elif self.piece < 0:
            return " " + letters[abs(self.piece) - 1]
        else:
            return letters[abs(self.piece) - 1] + " "
        
    def get_team(self):
        if self.piece < 0:
            return B
        elif self.piece > 0:
            return W
        else:
            return 0
    
    # have to do check avoiding
    def get_moves(self):
        list = []
        if self.piece == Piece.No:
            return list
        elif abs(self.piece) == Piece.WKing:
            for i in range(4):
                self.add_first_moves(self.nHoriz[i], list)
                self.add_first_moves(self.nDiag[i], list)
            return list
        elif abs(self.piece) == Piece.WQueen:
            for i in range(4):
                self.add_row_moves(self.nHoriz[i], list)
                self.add_row_moves(self.nDiag[i], list)
            return list
        elif abs(self.piece) == Piece.WRook:
            return list
        elif abs(self.piece) == Piece.WKnight:
            return list
        elif abs(self.piece) == Piece.WBishop:
            return list
        elif self.piece == Piece.WPawn:
            return list
        elif self.piece == Piece.BPawn:
            return list
        return []
    
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
    board[0][0].piece = Piece.WRook
    board[1][0].piece = Piece.WKnight
    board[2][0].piece = Piece.WBishop
    board[3][0].piece = Piece.WQueen
    board[4][0].piece = Piece.WKing
    board[5][0].piece = Piece.WBishop
    board[6][0].piece = Piece.WKnight
    board[7][0].piece = Piece.WRook
    board[0][7].piece = Piece.BRook
    board[1][7].piece = Piece.BKnight
    board[2][7].piece = Piece.BBishop
    board[3][7].piece = Piece.BQueen
    board[4][7].piece = Piece.BKing
    board[5][7].piece = Piece.BBishop
    board[6][7].piece = Piece.BKnight
    board[7][7].piece = Piece.BRook
    for i in range(8):
        board[i][1].piece = Piece.WPawn
        board[i][6].piece = Piece.BPawn
    return

def print_board(board):
    print "+--+--+--+--+--+--+--+--+ "
    for i in range(7, -1, -1):
        line = "|"
        for j in range(8):
            line += board[j][i].to_string()
            line += "|"
        print line
        print "+--+--+--+--+--+--+--+--+"
    return

board = init_board()
fill_board(board)
board[3][4].piece = Piece.WKing
board[5][4].piece = Piece.WQueen
print_board(board)
for space in board[5][4].get_moves():
    print space.coord_string()


"""
s = board[3][1]
print s.coord_string() + " has these neighbors:"
for col in s.nHoriz:
    a = "horiz: "
    for space in col:
        a += space.coord_string() + " "
    print a
for col in s.nDiag:
    a = "diag: "
    for space in col:
        a += space.coord_string() + " "
    print a
a = "knight: "
for space in s.nKnight:
    a += space.coord_string() + " "
print a
"""