import sys
import os
from config_validation import read_config, validation
from mazegen import MazeGenerator
from mazegen.maze_display import MazeDisplay
from typing import Tuple, Optional


def clear_screen() -> None:
    """Clear the terminal screen."""
    print("\033[2J\033[H", end="")
    os.system("clear")


def set_color(color: str) -> str:
    """Return ANSI escape code for the specified color."""
    colors = {
        'reset': "\033[0m",
        'red': "\033[91m",
        'green': "\033[92m",
        'yellow': "\033[93m",
        'blue': "\033[94m",
        'magenta': "\033[95m",
        'cyan': "\033[96m",
        'white': "\033[97m",
        'gray': "\033[90m"
    }
    return colors.get(color.lower(), colors['reset'])


def display_menu() -> None:
    """Display the interactive maze control menu."""
    print("\n" + "="*50)
    print(" "*16 + "\033[43m MAZE CONTROL MENU \033[0m")
    print("="*50)
    print("  1. Re-generate maze")
    print("  2. Show/Hide solution path")
    print("  3. Change wall colors")
    print("  4. Change '42' pattern color")
    print("  5. Change maze generation algorithms")
    print("  q. Quit")
    print("="*50)


def get_user_choice() -> str:
    """Get and return user's menu choice as a string."""
    choice = input("\nEnter your choice: ").strip().lower()
    return choice


def choose_algorithm(current: str) -> str:
    """Prompt user to select a maze generation algorithm."""
    print(f"\nCurrent algorithm: {current.upper()}")
    print("\nAvailable algorithms:")
    print("  1. Backtracking (DFS) - Long winding corridors")
    print("  2. Prim's Algorithm - Branching tree-like structure")

    choice = input("\nChoose algorithm (1-2): ").strip()

    if choice == '1':
        return 'backtracking'
    elif choice == '2':
        return 'prims'
    else:
        print("Invalid choice. Keeping current algorithm.")
        return current


def choose_color(current: str) -> str:
    """Prompt user to select a color from available options."""
    print(f"\nCurrent color: {current.upper()}")
    print("Available colors:")
    print(f"{set_color('red')}  1. Red")
    print(f"{set_color('green')}  2. Green")
    print(f"{set_color('yellow')}  3. Yellow")
    print(f"{set_color('blue')}  4. Blue")
    print(f"{set_color('magenta')}  5. Magenta")
    print(f"{set_color('cyan')}  6. Cyan{set_color('reset')}")
    print("  7. White")

    color_map = {
        '1': 'red',
        '2': 'green',
        '3': 'yellow',
        '4': 'blue',
        '5': 'magenta',
        '6': 'cyan',
        '7': 'white'
    }

    choice = input("Choose color (1-7): ").strip()
    return color_map.get(choice, current)


def main() -> None:
    """Main program entry point - generate, solve,
    and display maze with interactive menu."""
    if len(sys.argv) != 2:
        print("Usage: python3 a_maze_ing.py <config_file>")
        sys.exit(1)

    config_file: str = sys.argv[1]

    try:
        config = read_config(config_file)
        validation(config)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

    width: int = config["WIDTH"]
    height: int = config["HEIGHT"]
    entry: Tuple[int, int] = config["ENTRY"]
    exit_: Tuple[int, int] = config["EXIT"]
    output: str = config["OUTPUT_FILE"]
    perfect: bool = config["PERFECT"]
    seed: Optional[int] = config.get("SEED")

    show_path: bool = False
    animation_speed: float = 0.0001
    pattern_color: str = "yellow"
    wall_color: str = "white"
    algorithm: str = "backtracking"

    display = MazeDisplay(width, height)
    display.set_pattern_color(pattern_color)

    clear_screen()
    print("Generating maze...\n")

    maze = MazeGenerator(width, height, seed=seed)
    maze.add_42_pattern()
    maze.generate_backtracking(entry, display=display, delay=animation_speed)
    maze.reset_visited()

    if not perfect:
        maze.break_walls(chance=0.1)

    print("\nSolving maze...\n")
    path = maze.solve_bfs(entry, exit_, display=display, delay=animation_speed)

    maze.write_maze_hex(output, entry, exit_, path)

    clear_screen()
    print("Maze generation and solving complete!\n")
    display.display_ascii(maze.grid, entry, exit_,
                          maze.pattern_cells, path=path, show_generation=False)

    while True:
        display_menu()
        choice = get_user_choice()

        if choice == '1':
            clear_screen()
            print("Regenerating maze...\n")

            maze = MazeGenerator(width, height, seed=seed)
            maze.add_42_pattern()

            if algorithm == 'backtracking':
                maze.generate_backtracking(entry, display=display,
                                           delay=animation_speed)
            elif algorithm == 'prims':
                maze.generate_prims(entry, display=display,
                                    delay=animation_speed)

            maze.reset_visited()

            if not perfect:
                maze.break_walls(chance=0.1)

            print("\nSolving maze...\n")
            path = maze.solve_bfs(entry, exit_, display=display,
                                  delay=animation_speed)
            maze.write_maze_hex(output, entry, exit_, path)

            clear_screen()
            print("Maze regenerated and solved!\n")
            display.display_ascii(maze.grid, entry, exit_, maze.pattern_cells,
                                  path if show_path else None,
                                  show_generation=False)

        elif choice == '2':
            show_path = not show_path
            clear_screen()
            if show_path:
                print("Solution path: SHOWN\n")
            else:
                print("Solution path: HIDDEN\n")
            display.display_ascii(maze.grid, entry, exit_, maze.pattern_cells,
                                  path if show_path else None,
                                  show_generation=False)

        elif choice == '3':
            new_color = choose_color(wall_color)
            wall_color = new_color

            ansi_map = {
                'red': display.RED,
                'green': display.GREEN,
                'yellow': display.YELLOW,
                'blue': display.BLUE,
                'magenta': display.MAGENTA,
                'cyan': display.CYAN,
                'white': display.WHITE
            }

            display.set_color('wall', ansi_map.get(wall_color, display.WHITE))

            clear_screen()
            print(f"Wall color changed to: {wall_color.upper()}\n")
            display.display_ascii(maze.grid, entry, exit_, maze.pattern_cells,
                                  path if show_path else None,
                                  show_generation=False)

        elif choice == '4':
            print("\nChange '42' pattern color")
            new_color = choose_color(pattern_color)
            pattern_color = new_color
            display.set_pattern_color(pattern_color)

            clear_screen()
            print(f"Pattern color changed to: {pattern_color.upper()}\n")
            display.display_ascii(maze.grid, entry, exit_, maze.pattern_cells,
                                  path if show_path else None,
                                  show_generation=False)

        elif choice == '5':
            new_algorithm = choose_algorithm(algorithm)

            if new_algorithm != algorithm:
                algorithm = new_algorithm

                clear_screen()
                print(f"Regenerating maze with {algorithm.upper()}"
                      " algorithm...\n")

                maze = MazeGenerator(width, height)
                maze.add_42_pattern()

                if algorithm == 'backtracking':
                    maze.generate_backtracking(entry, display=display,
                                               delay=animation_speed)
                elif algorithm == 'prims':
                    maze.generate_prims(entry, display=display,
                                        delay=animation_speed)

                maze.reset_visited()

                if not perfect:
                    maze.break_walls(chance=0.1)

                print("\nSolving maze...\n")
                path = maze.solve_bfs(entry, exit_, display=display,
                                      delay=animation_speed)
                maze.write_maze_hex(output, entry, exit_, path)

                clear_screen()
                print(f"Maze regenerated with {algorithm.upper()}!\n")
                display.display_ascii(maze.grid, entry, exit_,
                                      maze.pattern_cells, path,
                                      show_generation=False)
            else:
                clear_screen()
                print("Algorithm unchanged.\n")
                display.display_ascii(maze.grid, entry, exit_,
                                      maze.pattern_cells,
                                      path if show_path else None,
                                      show_generation=False)

        elif choice == 'q':
            clear_screen()
            print("Saving final maze to file...")
            maze.write_maze_hex(output, entry, exit_, path)
            print(f"Maze saved to: {output}")
            print("\nGoodbye!")
            sys.exit(0)

        else:
            print("\nInvalid choice! Please try again.")
            input("Press Enter to continue...")


if __name__ == "__main__":
    main()
