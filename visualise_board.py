import matplotlib.pyplot as plt

def visualize_board_with_borders_and_indices(board_string):
    # Define a mapping from characters to colors
    color_map = {'B': 'blue', 'R': 'red', '0': 'white'}

    # Split the board string into rows
    board = [row.split() for row in board_string.strip().split('\n')]
    num_rows = len(board)
    num_cols = len(board[0])

    # Create the figure and axis for the plot
    fig, ax = plt.subplots(figsize=(num_cols, num_rows))
    
    # Plot each cell
    for i in range(num_rows):
        for j in range(num_cols):
            cell_color = color_map[board[i][j]]
            rect = plt.Rectangle((j, i), 1, 1, color=cell_color, edgecolor='black')
            ax.add_patch(rect)
            # Add indices
            ax.text(j + 0.5, i + 0.5, f'{i},{j}', ha='center', va='center', color='black')

    # Set the axis limits and turn off the axis
    ax.set_xlim(0, num_cols)
    ax.set_ylim(num_rows, 0)
    ax.axis('off')

    plt.show()

# Board data
board_data = """
0 0 0 0 R 0 0 0 0 0 0
0 0 0 0 0 0 0 0 0 0 0
0 0 R 0 0 0 0 0 0 0 0
0 0 0 0 0 0 0 0 0 0 0
0 0 0 0 0 0 0 0 R 0 R
R 0 0 0 R 0 R 0 0 0 0
0 0 0 0 R 0 0 0 0 0 0
0 0 0 0 R 0 0 0 0 0 0
0 0 0 0 0 0 R 0 0 0 0
0 0 0 0 0 0 0 0 0 0 B
B B B B B B B B B B R
"""

# Run the function with the board data
visualize_board_with_borders_and_indices(board_data)
