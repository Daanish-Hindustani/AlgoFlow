import random

def __init__():
        #Makes a 6X7 board
        board = []
        for i in range(6):
            sub_board = []
            for j in range(7):
                sub_board.append("_")
            board.append(sub_board)
        return board 
    
#Prints the whole board
def print_board(board):
        for row in board:
            print(row)

#condtions to check move
def make_move(x, y, board):
      #check if move is open
      if board[x][y] != "_":
        print("invalid move square alredy taken")
        return False
      #checks x bounds
      elif x>6 and x<0:
         print("invalid move out of bound")
         return False
      #checks y bounds
      elif y>5 and y<0:
         print("invalid move out of bounds")
         return False
      #if all check correct it makes move
      else:
          board[x][y] = "X"
          return True

def horizontal_winner(board):
    #goes through all horizontal values till 4 in a row values are same
    for row in board:
        count = 1
        for col in range(1, len(row)):
            #if the value is same as previous one
            if row[col] == row[col-1] and row[col] != "_":
                count += 1
                if count == 4:
                    return True
            else:
                count = 1
    return False

# Used to check if you win vertically
def vertical_winner(board):
    #goes through all vertical values till 4 in a row values are same
    for col in range(len(board[0])):
        count = 1
        for row in range(1, len(board)):
            if board[row][col] == board[row - 1][col] and board[row][col] != "_":
                count += 1
                if count == 4:
                    return True
            else:
                count = 1
    return False

def diagonal_winner(board):
    #This function will go through all the points 
    #it will then progress through the diagnoal points and check to see if they are 4 in a row
    for row in range(len(board) - 3):
        for col in range(len(board[0]) - 3):
            if (board[row][col] != "_" and
                board[row + 1][col + 1] == board[row][col] and
                board[row + 2][col + 2] == board[row][col] and
                board[row + 3][col + 3] == board[row][col]):
                return True

    #this is done for the right up 
    for row in range(3, len(board)):
        for col in range(len(board[0]) - 3):
            if (board[row][col] != "_" and
                board[row - 1][col + 1] == board[row][col] and
                board[row - 2][col + 2] == board[row][col] and
                board[row - 3][col + 3] == board[row][col]):
                return True

    return False



#combines all winning functions to one
def winner(board):
    if horizontal_winner(board) or vertical_winner(board) or diagonal_winner(board):
        return True
    else:
        return False
    
#random move for robot
def random_move(board):
    movex = 0
    movey = 0
    while board[movex][movey] != "_":
        movex = random.randint(0,6)
        movey = random.randint(0,5)
    
    board[movex][movey] = "O"

#main function
#The x and y are inverted and the axis starts at zero 
def main():
    board = __init__()
    print_board(board)
    print("x-axis and y-axis are inverted, and all values start from 0")
    while(winner(board) != True):
        usr_X_input = int(input("what is your Row move: "))
        usr_Y_input = int(input("what is your Col move: "))
        while(make_move(usr_X_input, usr_Y_input, board) is not True):
            usr_X_input = int(input("what is your Row move: "))
            usr_Y_input = int(input("what is your Col move: "))
            make_move(usr_X_input, usr_Y_input, board)

        print_board(board)
        if(winner(board) == True):
            print("you win")
            return
        
        print("Robot turn")

        random_move(board)
        print_board(board)
        if(winner(board) == True):
            print("Robot win")
            return

if __name__ == "__main__":
    main()

