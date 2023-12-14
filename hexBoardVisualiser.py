import matplotlib.pyplot as plt
import numpy as np

def visualize_board_with_borders_and_indices(board_string):
    # Define a mapping from characters to colors
    color_map = {'B': 'blue', 'R': 'red', '0': 'white'}

    # Split the board string into rows and create a 2D array
    board = [row.split() for row in board_string.strip().split('\n')]
    num_rows = len(board)
    num_cols = len(board[0])

    # Create a numeric array for the board
    numeric_board = np.zeros((num_rows, num_cols, 3))
    for i, row in enumerate(board):
        for j, cell in enumerate(row):
            # Map the character to a color
            color = color_map[cell]
            numeric_board[i, j] = plt.cm.colors.to_rgb(color)

    # Plotting the board with borders and indices
    fig, ax = plt.subplots(figsize=(num_cols, num_rows))
    ax.imshow(numeric_board)

    # Adding borders and indices
    for i in range(num_rows):
        for j in range(num_cols):
            rect = plt.Rectangle((j-0.5, i-0.5), 1, 1, fill=False, edgecolor='black', lw=1)
            ax.add_patch(rect)
            # Adding indices
            ax.text(j, i, f'{i},{j}', ha='center', va='center', color='black')

    ax.axis('off')
    plt.show()

# Board data as a multi-line string
board_data = """
B 0 0 B B B B B B 0 B
B B B B 0 B B 0 B 0 B
B 0 0 B B B 0 B 0 B B
R B B R B B R R B B B
B R B R B B R R R B R
B B R B B B R R B B R
B B B B B R R R R R B
R R R B B R B R R R R
R R R B B R R B R R R
B R R R R R R R R R R
R R R R R R R R R R R
"""

# Run the function with the board data
visualize_board_with_borders_and_indices(board_data)
