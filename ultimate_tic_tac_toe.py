import numpy as np
import random
import math
from sortedcontainers import SortedDict
import json

with open('macro_winstates.json') as f:
    large_board_winstates = json.load(f, object_pairs_hook=SortedDict)

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

    def update(self, result, strategy):
        self.visits += 1

        # normal wins/losses
        if strategy == 1:
            val = 1 if result == self.state.current_player else \
            -1 if result == self.state.other_player else 0.5

        # "wants to win", avoids positions where only his opponent can win
        elif strategy == 2:
            val = 1 if result == self.state.current_player else \
            -1 if result == self.state.other_player else \
            -2 if result == self.state.other_player | 4 else 0.5

        # "doesn't want to lose", prefers positions where only he can win/draw
        elif strategy == 3:
            val = 2 if result == self.state.current_player | 4 else \
            1 if result == self.state.current_player else \
            -1 if result == self.state.other_player else 0.5

        # combined 2,3:
        elif strategy == 4:
            val = 2 if result == self.state.current_player | 4 else \
            1 if result == self.state.current_player else \
            -1 if result == self.state.other_player else \
            -2 if result == self.state.other_player | 4 else 0.5
            
        self.wins += val

    def __str__(self):
        return f"{self.visits}, {self.wins}"

class UltimateTicTacToe:
    def __init__(self):
        # Initialize the 3x3 large board with empty values
        self.board = np.zeros((3, 3), dtype=np.int8)
        # Initialize the current player (X=1,Y=2, X starts first)
        self.current_player = 1
        self.other_player = 2
        # Initialize the small boards
        self.small_boards = np.zeros((3, 3, 3, 3), dtype=np.int8)
        # Initialize the winning_state as 7 (can be p1 win,p2 win,draw)
        self.winning_state = 7
        self.grid_move = None #(y, x), None if every move possible

    def setAvailable(self,n):
        self.grid_move=n
    def getAvailable(self):
        return self.grid_move
    def resetBoard(self):
        self.board = np.zeros((3, 3), dtype=np.int8)
        self.small_boards = np.zeros((3, 3, 3, 3), dtype=np.int8)
        self.current_player = 1
        self.other_player = 2
        self.winning_state = 7
        self.grid_move = None
    #Don't touch this ever.
    def print_board(self,spacing=5):
        colors = {'X': '\033[91m', 'O': '\033[94m', 'reset': '\033[0m'}
        print("╔"+(("═"*spacing+"╤")*2+("═"*spacing+"╦"))*2+("═"*spacing+"╤")*2+"═"*spacing+"╗")
        for large_row in range(3):
            for small_row in range(3):
                row_str = "║"
                for large_col in range(3):
                    for small_col in range(3):
                        player = self.small_boards[large_row, large_col, small_row, small_col]
                        player = 'X' if player == 1 else 'O' if player == 2 else '=' if player == 4 else ' '
                        if player in colors:
                            if self.check_small_board_win(large_row, large_col):
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

    def hash_board(self,board):
        rot1 = np.rot90(np.rot90(board, axes=(2,3)))
        rot2 = np.rot90(np.rot90(rot1, axes=(2,3)))
        rot3 = np.rot90(np.rot90(rot2, axes=(2,3)))
        flip = np.transpose(board, axes=(1,0,3,2))
        flip_rot1 = np.rot90(np.rot90(flip, axes=(2,3)))
        flip_rot2 = np.rot90(np.rot90(flip_rot1, axes=(2,3)))
        flip_rot3 = np.rot90(np.rot90(flip_rot2, axes=(2,3)))
    
        board_hashes = map(__matrix_to_hash, [board, rot1, rot2, rot3, flip, flip_rot1, flip_rot2, flip_rot3])

        subgame = self.__available_grid_move
        s_board = np.zeros((3, 3), dtype=np.int8)
        if subgame == 9:
            s_board_hashes = [self.__matrix_to_hash(s_board)] * 8
        else:
            s_board[subgame] = 1
            s_rot1 = np.rot90(s_board)
            s_rot2 = np.rot90(s_rot1)
            s_rot3 = np.rot90(s_rot2)
            s_flip = np.transpose(s_board)
            s_flip_rot1 = np.rot90(s_flip)
            s_flip_rot2 = np.rot90(s_flip_rot1)
            s_flip_rot3 = np.rot90(s_flip_rot2)
    
            s_board_hashes = map(self.__matrix_to_hash, [s_board, s_rot1, s_rot2, s_rot3, s_flip, s_flip_rot1, s_flip_rot2, s_flip_rot3])
    
        combined_hashes = map(lambda x: x[0] + x[1], zip(board_hashes, s_board_hashes))
        
        return max(combined_hashes)

    def hash_large_board(self):
        rot1 = np.rot90(self.board)
        rot2 = np.rot90(rot1)
        rot3 = np.rot90(rot2)
        flip = np.transpose(self.board)
        flip_rot1 = np.rot90(flip)
        flip_rot2 = np.rot90(flip_rot1)
        flip_rot3 = np.rot90(flip_rot2)
    
        best = max([
            (self.__matrix_to_hash(rot1), rot1, 1),
            (self.__matrix_to_hash(rot2), rot2, 2),
            (self.__matrix_to_hash(rot3), rot3, 3),
            (self.__matrix_to_hash(flip), flip, 4),
            (self.__matrix_to_hash(flip_rot1), flip_rot1, 5),
            (self.__matrix_to_hash(flip_rot2), flip_rot2, 6),
            (self.__matrix_to_hash(flip_rot3), flip_rot3, 7)
        ], key=lambda x: x[0])
    
        board_hash = self.__matrix_to_hash(self.board)
        
        if best[0] > board_hash:
            return best
        else:
            return board_hash, self.board, 0

    def __matrix_to_hash(self,matrix):
        return ''.join(map(str, matrix.ravel()))

    #Bolj ali manj zaradi print win
    def switch_player(self):
        self.current_player = 2 if self.current_player == 1 else 1
        self.other_player = 2 if self.other_player == 1 else 1
    def make_move(self, large_row, large_col, small_row, small_col):
        # Make the move on the small board
        self.small_boards[large_row, large_col, small_row, small_col] = self.current_player
        
        # Check if the small board is won after the move
        if self.check_small_board_win(large_row, large_col):
            self.small_boards[large_row, large_col] = self.current_player
            # Mark the large board as won by the current player
            self.board[large_row, large_col] = self.current_player
            # Check if the large board is won after the move
            h = self.hash_large_board()[0]
            if h not in large_board_winstates:
                print(self.board, self.small_boards)
            self.winning_state = large_board_winstates[h]
        elif self.check_small_board_full(large_row, large_col):
            self.small_boards[large_row, large_col] = 4
            self.board[large_row, large_col] = 4
            self.winning_state = large_board_winstates[self.hash_large_board()[0]]
            

        # prepare to move the grid to the quadrant this was played
        # small_row -> large_row, small_col -> large_col
        if self.check_small_board_full(small_row, small_col):
            self.setAvailable(None)
        else:
            self.setAvailable((small_row, small_col))

        # Switch to the other player
        self.switch_player()

    def check_small_board_win(self, row, col):
        board = self.small_boards[row, col]
        # Check rows, columns, and diagonals for a win
        for i in range(3):
            if board[i][0] == board[i][1] == board[i][2] != 0:
                return True
            if board[0][i] == board[1][i] == board[2][i] != 0:
                return True
        if board[0][0] == board[1][1] == board[2][2] != 0:
            return True
        if board[0][2] == board[1][1] == board[2][0] != 0:
            return True
        return False

    def check_small_board_full(self, row, col):
        return np.all(self.small_boards[row, col] != 0)

    def check_draw(self):
        # Check if the game is a draw
        return self.winning_state == 4
    
    def check_end(self):
        # Check if the game is a draw
        return self.winning_state == 1 or self.winning_state == 2 or self.winning_state == 4
    
    def get_available_moves(self):
        if self.check_end():
            return []
        
        def gen(a):
            while True:
                yield a

        subgame = self.getAvailable()
        if subgame is None:
            valid = np.where(self.small_boards == 0)
            return list(zip(*valid))
        else:
            valid = np.where(self.small_boards[subgame] == 0)
            return list(zip(gen(subgame[0]), gen(subgame[1]), *valid))

    def simulate_random_playout(self):
        while not self.check_end():
            available_moves = self.get_available_moves()
            if not available_moves:
                #print("no more available moves")
                break
            move = random.choice(available_moves)
            self.make_move(*move)
        winner = self.winning_state
        return winner

    def mcts(self, simulations, strategy):
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
                node.update(result, strategy)
                node = node.parent

        #print(sorted(root.children, key=lambda c: c.visits)[-1])
        return sorted(root.children, key=lambda c: c.visits)[-1].move

    def copy(self):
        new_game = UltimateTicTacToe()
        new_game.board = self.board.copy()
        new_game.small_boards = self.small_boards.copy()
        new_game.current_player = self.current_player
        new_game.winning_state = self.winning_state
        new_game.grid_move = self.grid_move
        return new_game


def play_monte(game, simulations=5000, strategy=1,print_ = True):
        current_grid = game.getAvailable()
        #print(f"Current small grid move: {current_grid}")

        move = game.mcts(simulations, strategy)
        large_row,large_col,small_row,small_col= move
        game.make_move(large_row, large_col, small_row, small_col)
        if print_:
            game.print_board()

def play_normal(game):
    current_grid = game.getAvailable()
    print(f"Current small grid move: {current_grid}")
    if not current_grid or not game.board[current_grid[0]][current_grid[1]]:
        while True:
            large_row = input("Enter the row number of the large board (0-2): ")
            large_col = input("Enter the column number of the large board (0-2): ")
            try:
                large_row = int(large_row)
                large_col = int(large_col)
                if not (large_col >= 0 and large_col <= 2 and large_row >= 0 and large_row <= 2):
                    print("Please provide a number from 0 to 2")
                    continue
                if game.board[large_row, large_col] != 0:
                    print("Large grid already won, change it.")
                    current_grid = None
                    continue
                break
            except:
                    if type(large_row) is str and "q" in large_row or type(large_col) is str and "q" in large_col:
                        quit()
                    print("Please provide valid input (a number from 0 to 2)")
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
                if game.small_boards[large_row, large_col, small_row, small_col] != 0:
                    print("This location is already full, select another.")
                    continue
                break
            except:
                if type(small_row) is str and small_row == "q" in small_row or type(
                        small_col) is str and "q" in small_col:
                    quit()
                print("Please provide valid input (a number from 0 to 2)")
                continue

        game.make_move(large_row, large_col, small_row, small_col)
        game.print_board()


if __name__ == "__main__":
    game = UltimateTicTacToe()
    #game.unhash("O X OOOOOXX X XOOO X XO OOOX   XOOOOX  O  OOO OOOXXOOO  XOOOOOOXOOOOOOOOXO OOOOOO1",0)
    num_of_games = 1
    while True:
        num_of_games = int(input('Number of games'))
        p1_monte = input('Use AI for p1? (y/n) ')
        if p1_monte == 'q':
            quit()
        if p1_monte in ['y', 'n']:
            break
    if p1_monte == 'y':
        while True:
            p1_monte_strat_in = input('What AI strategy for p1? (1/2/3/4) ')
            if p1_monte_strat_in == 'q':
                quit()
            try:
                p1_monte_strat = int(p1_monte_strat_in)
                if p1_monte_strat < 1 or p1_monte_strat > 4:
                    continue
                break
            except:
                print("Please provide a valid number")
                break
        while True:
            p1_monte_iter_in = input('Iteration count for p1 AI? (default 5000) ')
            if p1_monte_iter_in == 'q':
                quit()
            if p1_monte_iter_in == '':
                p1_monte_iter = 5000
                break
            try:
                p1_monte_iter = int(p1_monte_iter_in)
                break
            except:
                print("Please provide a valid number")
                continue

    while True:
        p2_monte = input('Use AI for p2? (y/n) ')
        if p2_monte == 'q':
            quit()
        if p2_monte in ['y', 'n']:
            break
    if p2_monte == 'y':
        while True:
            p2_monte_strat_in = input('What AI strategy for p2? (1/2/3/4) ')
            if p2_monte_strat_in == 'q':
                quit()
            try:
                p2_monte_strat = int(p2_monte_strat_in)
                if p2_monte_strat < 1 or p2_monte_strat > 4:
                    continue
                break
            except:
                print("Please provide a valid number")
                break
        while True:
            p2_monte_iter_in = input('Iteration count for p2 AI? (default 5000) ')
            if p2_monte_iter_in == 'q':
                quit()
            if p2_monte_iter_in == '':
                p2_monte_iter = 5000
                break
            try:
                p2_monte_iter = int(p2_monte_iter_in)
                break
            except:
                print("Please provide a valid number")
                continue

    results = [0,0,0] #p1, tie, p2
    for game_num in range(num_of_games):
        #game.print_board()
        game.resetBoard()
        print("Game ",game_num+1)
        if not game.check_end():
            while True:
                if p1_monte == 'y':
                    play_monte(game,p1_monte_iter,p1_monte_strat,print_=False)
                else:
                    play_normal(game)

                if game.check_draw():
                    print("It's a draw!")
                    results[1] += 1
                    break
                elif game.check_end():
                    game.switch_player()
                    if game.current_player==1:
                        results[0]+=1
                    else:
                        results[2]+=1
                    print(f"Player {game.current_player} wins!")
                    break

                if p2_monte == 'y':
                    play_monte(game,p2_monte_iter,p2_monte_strat,print_=False)
                else:
                    play_normal(game)

                if game.check_draw():
                    print("It's a draw!")
                    results[1]+=1
                    break
                elif game.check_end():
                    game.switch_player()
                    print(f"Player {game.current_player} wins!")
                    if game.current_player==1:
                        results[0]+=1
                    else:
                        results[2]+=1
                    break
            print(f"{p2_monte_strat}&{results[0]} & {results[1]} & {results[2]} & {p2_monte_iter}")
    print(results)
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