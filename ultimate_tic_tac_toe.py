class UltimateTicTacToe:
    def __init__(self):
        # Initialize the 3x3 large board with empty values
        self.board = [[' ' for _ in range(3)] for _ in range(3)]
        # Initialize the current player (X starts first)
        self.current_player = 'X'
        # Initialize the small boards as empty dictionaries
        self.small_boards = {(i, j): [[' ' for _ in range(3)] for _ in range(3)] for i in range(3) for j in range(3)}
        # Initialize the winner as None
        self.winner = None

    #Don't touch this ever.
    def print_board(self,spacing=3):
        colors = {'X': '\033[91m', 'O': '\033[94m', 'reset': '\033[0m'}
        print("╔"+(("═"*spacing+"╤")*2+("═"*spacing+"╦"))*2+("═"*spacing+"╤")*2+"═"*spacing+"╗")
        for large_row in range(3):
            for small_row in range(3):
                row_str = "║"
                for large_col in range(3):
                    for small_col in range(3):
                        player = self.small_boards[(large_row, large_col)][small_row][small_col]
                        if player in colors:
                            if self.check_small_board_win(self.small_boards[(large_row, large_col)]):
                                row_str += " "*((spacing-1)//2)+f"{colors[player]}{player}{colors['reset']}"+" "*(spacing//2)
                            else:
                                row_str += " "*((spacing-1)//2)+f"{colors[player]}{player}{colors['reset']}"+" "*(spacing//2)
                        else:
                            row_str += " "*((spacing-1)//2)+player+" "*(spacing//2)
                        row_str += ("│" if small_col % 3 != 2 else "║")
                row_str = row_str[:-1] + "║"
                print(row_str)
                if small_row != 2:
                    print('╟'+(("─"*spacing+"┼")*2+("─"*spacing+"╫"))*2+("─"*spacing+"┼")*2+"─"*spacing+"╢")
            if large_row != 2:
                print('╠'+(("═"*spacing+"╪")*2+("═"*spacing+"╬"))*2+("═"*spacing+"╪")*2+"═"*spacing+"╣")
        print('╚'+(("═"*spacing+"╧")*2+("═"*spacing+"╩"))*2+("═"*spacing+"╧")*2+"═"*spacing+"╝")

    def make_move(self, large_row, large_col, small_row, small_col):
        # Check if the specified large board is already won or full
        if self.winner or self.board[large_row][large_col] != ' ':
            print("Invalid move! Large board already won or full.")
            return False

        # Check if the specified small board is already won or full
        if self.small_boards[(large_row, large_col)][small_row][small_col] != ' ':
            print("Invalid move! Small board already won or full.")
            return False

        # Make the move on the small board
        self.small_boards[(large_row, large_col)][small_row][small_col] = self.current_player

        # Check if the small board is won after the move
        if self.check_small_board_win(self.small_boards[(large_row, large_col)]):
            # Mark the large board as won by the current player
            for i in range(0,3):
                for j in range(0,3): 
                    self.small_boards[(large_row, large_col)][i][j] = self.current_player  
            self.board[large_row][large_col] = self.current_player
            # Check if the large board is won after the move
            if self.check_large_board_win():
                self.winner = self.current_player

        # Switch to the other player
        self.current_player = 'O' if self.current_player == 'X' else 'X'
        return True

    def check_small_board_win(self, board):
        # Check rows, columns, and diagonals for a win
        for i in range(3):
            if board[i][0] == board[i][1] == board[i][2] != ' ':
                return True
            if board[0][i] == board[1][i] == board[2][i] != ' ':
                return True
        if board[0][0] == board[1][1] == board[2][2] != ' ':
            return True
        if board[0][2] == board[1][1] == board[2][0] != ' ':
            return True
        return False

    def check_large_board_win(self):
        # Check rows, columns, and diagonals for a win
        for i in range(3):
            if self.board[i][0] == self.board[i][1] == self.board[i][2] != ' ':
                return True
            if self.board[0][i] == self.board[1][i] == self.board[2][i] != ' ':
                return True
        if self.board[0][0] == self.board[1][1] == self.board[2][2] != ' ':
            return True
        if self.board[0][2] == self.board[1][1] == self.board[2][0] != ' ':
            return True
        return False

    def check_draw(self):
        # Check if the game is a draw (all small boards are full)
        for key in self.small_boards:
            for row in self.small_boards[key]:
                if ' ' in row:
                    return False
        return True


game = UltimateTicTacToe()
game.print_board()

current_grid = None
while not game.winner and not game.check_draw():
    if not current_grid or not game.board[current_grid[0]][current_grid[1]]:
    
        while True:
            large_row = input("Enter the row number of the large board (0-2): ")
            large_col = input("Enter the column number of the large board (0-2): ")
            try:
                large_row = int(large_row)
                large_col = int(large_col)
                if not(large_col>=0 and large_col<=2 and large_row>=0 and large_row<=2):
                    print("Please provide a number from 0 to 2")
                    continue
                break
            except:
                if type(large_row) is str and "q" in large_row or type(large_col) is str and "q" in large_col:
                    quit()
                print("Please provide valid input (a number from 0 to 2)")
                continue

        current_grid = [large_row,large_col]
    if game.board[current_grid[0]][current_grid[1]] !=" ":
        print("Large grid already won, change it.")
        current_grid = None
        continue

    while True:
        small_row = input("Enter the row number of the small board (0-2): ")
        small_col = input("Enter the column number of the small board (0-2): ")
        try:
            small_row = int(small_row)
            small_col = int(small_col)
            
            if not(small_col>=0 and small_col<=2 and small_row>=0 and small_row<=2):
                print("Please provide a number from 0 to 2")
                continue
            break
        except:
            if type(small_row) is str and small_row == "q" in small_row or type(small_col) is str and "q" in small_col:
                quit()
            print("Please provide valid input (a number from 0 to 2)")
            continue

    if game.make_move(current_grid[0],current_grid[1], small_row, small_col):
        game.print_board()
        if game.winner:
            print(f"Player {game.current_player} wins!")
            break
        elif game.check_draw():
            print("It's a draw!")
            break
        if game.board[small_row][small_col] ==" ":
            current_grid = [small_row, small_col]
        else:
            current_grid = None
        print(f"Current small grid move: {current_grid}")
