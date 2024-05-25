import numpy as np
import random
import math


class MCTSNode:
    def __init__(self, state, move=None, parent=None):
        self.state = state
        self.move = move
        self.parent = parent
        self.children = []
        self.visits = 0
        self.wins = 0
        self.untried_moves = state.get_available_moves()

    def uct_select_child(self):
        return sorted(self.children, key=lambda c: c.wins / c.visits + math.sqrt(2 * math.log(self.visits) / c.visits))[-1]

    def add_child(self, move, state):
        child = MCTSNode(state, move, self)
        self.untried_moves.remove(move)
        self.children.append(child)
        return child

    def update(self, result):
        self.visits += 1
        self.wins += result

    def __str__(self):
        return f"{self.visits}, {self.wins}"

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
        self.__available_grid_move = 9 #0-8 za polja, 9 katerokoli polje

    def setAvailable(self,n):
        self.__available_grid_move=n
    def getAvailable(self):
        return self.__available_grid_move
    #Don't touch this ever.
    def print_board(self,spacing=5):
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

    #Hash je string vrednosti polj + state (0-9), TO JE ZA SETTANJE STATES
    def unhash(self,hash,rotation=0):
        board = [] #To je 9x9, treba je dati v small boards
        for i in range(0,len(hash)-1):
            board.append(hash[i])
        board = np.reshape(board,(9,9))
        sub_arrays_dict={}
        for idx in range(9):
            row, col = divmod(idx, 3)
            sub_arrays_dict[(row, col)] = board[row * 3:(row + 1) * 3, col * 3:(col + 1) * 3]
        #Check won conditions to format the big board
        for row in range(3):
            for col in range(3):
                win, player = self.check_small_board_win(sub_arrays_dict[(row,col)],True)
                if win:
                    self.board[row][col] = player
                    sub_arrays_dict[(row,col)][:] = player

        self.small_boards = sub_arrays_dict

        #self.board=

    def __get_canonical(self,matrix):
        matrices = []
        #preveri rotacije (4x)
        for i in range(4):
            matrices.append(self.__matrix_to_hash(np.rot90(matrix,i)))
        #preveri flip+rotacije (4x)
        for i in range(4):
            matrices.append(self.__matrix_to_hash(np.rot90(np.transpose(matrix),i)))

        #Vrne canocical hash in index preobrazbe
        return min(matrices),matrices.index(min(matrices))

    def __matrix_to_hash(self,matrix):
        return ''.join(matrix.flatten())
    #TO-DO Hash the board to canonical. Returns the rotation index as well (0-7)
    def hash_board(self):
        #za iskanje kanonicne oblike rabimo 8x prevrtet/izoblikovat board. naj bo po vrstnem redu '_', 'O', 'X'
        #Tako kot je v ascii formatu ( oz. ord(symbol) )
        array_row = [[] for _ in range(9)]
        for k, v in self.small_boards.items():
            for row in range(3):
                array_row[int(k[0])*3+row].extend(v[row])
        array_row= np.array(array_row)
        canonical, can_index = self.__get_canonical(array_row)
        print(f"Board hash: \"{canonical}\"\nRotation: {can_index}")

        #Add available game_state position (0-9)
        full_hash = {"hash":canonical,"game_state":self.getAvailable(),"rotation":can_index}
        return full_hash

    #Bolj ali manj zaradi print win
    def switch_player(self):
        self.current_player = 'O' if self.current_player == 'X' else 'X'
    def make_move(self, large_row, large_col, small_row, small_col):
        # Check if the specified large board is already won or full
        if self.winner or self.board[large_row][large_col] != ' ':
            print("Invalid move! Large board already won or full.")
            return False

        # Check if the specified small board is already won or full
        if self.small_boards[(large_row, large_col)][small_row][small_col] != ' ':
            print(large_row, large_col)
            print("Invalid move! Small board already won or full.")
            return False

        # Make the move on the small board
        self.small_boards[(large_row, large_col)][small_row][small_col] = self.current_player
        self.setAvailable(small_row * 3 + small_col)
        # Check if the small board is won after the move
        if self.check_small_board_win(self.small_boards[(large_row, large_col)]):
            # Mark the large board as won by the current player
            for i in range(0,3):
                for j in range(0,3): 
                    self.small_boards[(large_row, large_col)][i][j] = self.current_player  
            self.board[large_row][large_col] = self.current_player
            # Check if the large board is won after the move
            if self.check_large_board_win():
                self.setAvailable(9)

        # Switch to the other player
        self.current_player = 'O' if self.current_player == 'X' else 'X'
        return True

    def check_small_board_win(self, board,player=None):
        # Check rows, columns, and diagonals for a win
        for i in range(3):
            if board[i][0] == board[i][1] == board[i][2] != ' ':
                return True if not player else (True, board[i][0])
            if board[0][i] == board[1][i] == board[2][i] != ' ':
                return True if not player else (True, board[0][i])
        if board[0][0] == board[1][1] == board[2][2] != ' ':
            return True if not player else (True, board[0][0])
        if board[0][2] == board[1][1] == board[2][0] != ' ':
            return True if not player else (True, board[0][2])
        return False if not player else (False, '')

    def check_large_board_win(self):
        # Check rows, columns, and diagonals for a win
        for i in range(3):
            if self.board[i][0] == self.board[i][1] == self.board[i][2] != ' ':
                self.winner = self.board[i][0]
                return True
            if self.board[0][i] == self.board[1][i] == self.board[2][i] != ' ':
                self.winner = self.board[0][i]
                return True
        if self.board[0][0] == self.board[1][1] == self.board[2][2] != ' ':
            self.winner = self.board[0][0]
            return True
        if self.board[0][2] == self.board[1][1] == self.board[2][0] != ' ':
            self.winner = self.board[0][2]
            return True
        return False

    def check_draw(self):
        # Check if the game is a draw (all small boards are full)
        for key in self.small_boards:
            for row in self.small_boards[key]:
                if ' ' in row:
                    return False
        return True

    def get_available_moves(self):
        available_moves = []
        if self.getAvailable() == 9:
            for large_row in range(3):
                for large_col in range(3):
                    if self.board[large_row][large_col] == ' ':
                        for small_row in range(3):
                            for small_col in range(3):
                                if self.small_boards[(large_row, large_col)][small_row][small_col] == ' ':
                                    available_moves.append((large_row, large_col, small_row, small_col))
        else:
            large_row, large_col = divmod(self.getAvailable(), 3)
            if self.board[large_row][large_col] == ' ':
                for small_row in range(3):
                    for small_col in range(3):
                        if self.small_boards[(large_row, large_col)][small_row][small_col] == ' ':
                            available_moves.append((large_row, large_col, small_row, small_col))
        return available_moves

    def simulate_random_playout(self):
        current_player = self.current_player
        available_moves = self.get_available_moves()
        if not available_moves:
            return 0.5  # Draw
        move = random.choice(available_moves)
        self.make_move(*move)
        while not self.winner and not self.check_draw():
            available_moves = self.get_available_moves()
            if not available_moves:
                #print("no more available moves")
                break
            move = random.choice(available_moves)
            self.make_move(*move)
        winner = self.winner
        self.__init__()  # Reset the board
        if winner == 'X':
            return 1
        elif winner == 'O':
            return 0
        else:
            return 0.5

    def mcts(self, simulations):
        root = MCTSNode(self)
        for _ in range(simulations):
            node = root
            state = self.copy()

            # Selection
            while node.untried_moves == [] and node.children != []:
                node = node.uct_select_child()
                state.make_move(*node.move)

            # Expansion
            if node.untried_moves != []:
                move = random.choice(node.untried_moves)
                state.make_move(*move)
                node = node.add_child(move, state)

            # Simulation
            result = state.simulate_random_playout()
            # Backpropagation
            while node is not None:
                node.update(result)
                node = node.parent

        print(sorted(root.children, key=lambda c: c.visits)[-1])
        return sorted(root.children, key=lambda c: c.visits)[-1].move

    def copy(self):
        new_game = UltimateTicTacToe()
        new_game.board = [row[:] for row in self.board]
        new_game.small_boards = {k: [row[:] for row in v] for k, v in self.small_boards.items()}
        new_game.current_player = self.current_player
        new_game.winner = self.winner
        new_game.__available_grid_move = self.__available_grid_move
        return new_game


def play_monte(game, simulations=1000):
    current_grid = None
    while not game.winner and not game.check_draw():
        print(f"Available grid to move: {game.getAvailable()}")
        if not current_grid or not game.board[current_grid[0]][current_grid[1]]:
            while True:
                large_row = input("Enter the row number of the large board (0-2): ")
                large_col = input("Enter the column number of the large board (0-2): ")
                game.setAvailable(9)
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
                #game.switch_player()
                print(f"Player {game.current_player} wins!")
                break
            elif game.check_draw():
                print("It's a draw!")
                break
            if game.board[small_row][small_col] ==" ":
                current_grid = [small_row, small_col]
            else:
                game.setAvailable(9)
                current_grid = None
            print(f"Current small grid move: {current_grid}")

        # Monte Carlo Tree Search
        if not game.winner and not game.check_draw() and game.current_player=="O":
            move = game.mcts(simulations)
            print(f"Monte Carlo suggests move: {move}")
            large_row,large_col,small_row,small_col= move
            if(not current_grid):
                current_grid = [large_row,large_col]
            print(move)
            if game.make_move(current_grid[0],current_grid[1],small_row,small_col):
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
                    game.setAvailable(9)
                    current_grid = None
            game.hash_board()
def play_normal(game):
    current_grid = None
    while not game.winner and not game.check_draw():
        print(f"Available grid to move: {game.getAvailable()}")
        if not current_grid or not game.board[current_grid[0]][current_grid[1]]:
            while True:
                large_row = input("Enter the row number of the large board (0-2): ")
                large_col = input("Enter the column number of the large board (0-2): ")
                game.setAvailable(9)
                try:
                    large_row = int(large_row)
                    large_col = int(large_col)
                    if not (large_col >= 0 and large_col <= 2 and large_row >= 0 and large_row <= 2):
                        print("Please provide a number from 0 to 2")
                        continue
                    break
                except:
                    if type(large_row) is str and "q" in large_row or type(large_col) is str and "q" in large_col:
                        quit()
                    print("Please provide valid input (a number from 0 to 2)")
                    continue

            current_grid = [large_row, large_col]
        if game.board[current_grid[0]][current_grid[1]] != " ":
            print("Large grid already won, change it.")
            current_grid = None
            continue

        while True:
            small_row = input("Enter the row number of the small board (0-2): ")
            small_col = input("Enter the column number of the small board (0-2): ")
            try:
                small_row = int(small_row)
                small_col = int(small_col)

                if not (small_col >= 0 and small_col <= 2 and small_row >= 0 and small_row <= 2):
                    print("Please provide a number from 0 to 2")
                    continue
                break
            except:
                if type(small_row) is str and small_row == "q" in small_row or type(
                        small_col) is str and "q" in small_col:
                    quit()
                print("Please provide valid input (a number from 0 to 2)")
                continue

        if game.make_move(current_grid[0], current_grid[1], small_row, small_col):
            game.print_board()
            if game.winner:
                game.switch_player()
                print(f"Player {game.current_player} wins!")
                break
            elif game.check_draw():
                print("It's a draw!")
                break
            if game.board[small_row][small_col] == " ":
                current_grid = [small_row, small_col]
            else:
                game.setAvailable(9)
                current_grid = None
            print(f"Current small grid move: {current_grid}")


if __name__ == "__main__":
    game = UltimateTicTacToe()
    #game.unhash("O X OOOOOXX X XOOO X XO OOOX   XOOOOX  O  OOO OOOXXOOO  XOOOOOOXOOOOOOOOXO OOOOOO1",0)
    play_monte(game,5000)
    #play_normal(game)
    '''game.print_board()
    while not game.winner and not game.check_draw():
        if game.current_player == 'X':
            large_row = int(input("Enter the row number of the large board (0-2): "))
            large_col = int(input("Enter the column number of the large board (0-2): "))
            small_row = int(input("Enter the row number of the small board (0-2): "))
            small_col = int(input("Enter the column number of the small board (0-2): "))
            if not game.make_move(large_row, large_col, small_row, small_col):
                print("Invalid move! Try again.")
        else:
            move = game.mcts(1000)
            game.make_move(*move)
        game.print_board()
        if game.winner:
            print(f"Player {game.current_player} wins!")
            break
        elif game.check_draw():
            print("It's a draw!")
            break
game = UltimateTicTacToe()
#game.unhash("OOOOOOOOOXO  OX OOOOX  XOO OXOX O XOOO X XO OXOOOO XX  OXO    XOO O  XX XX  XX XO1",0)
#game.print_board()
#game.hash_board()
#game.unhash("O X OOOOOXX X XOOO X XO OOOX   XOOOOX  O  OOO OOOXXOOO  XOOOOOOXOOOOOOOOXO OOOOOO1",0)
game.print_board()
game.hash_board()

current_grid = None
while not game.winner and not game.check_draw():
    print(f"Available grid to move: {game.getAvailable()}")
    if not current_grid or not game.board[current_grid[0]][current_grid[1]]:
        while True:
            large_row = input("Enter the row number of the large board (0-2): ")
            large_col = input("Enter the column number of the large board (0-2): ")
            game.setAvailable(9)
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
            game.switch_player()
            print(f"Player {game.current_player} wins!")
            break
        elif game.check_draw():
            print("It's a draw!")
            break
        if game.board[small_row][small_col] ==" ":
            current_grid = [small_row, small_col]
        else:
            game.setAvailable(9)
            current_grid = None
        print(f"Current small grid move: {current_grid}")'''