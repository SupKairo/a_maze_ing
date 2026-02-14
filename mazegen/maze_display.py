from typing import Tuple, Optional, Set, List


class Cell:
    def __init__(self) -> None:
        """Initialize a cell with all walls closed."""
        self.north: bool = True
        self.east: bool = True
        self.south: bool = True
        self.west: bool = True
        self.visited: bool = False


class MazeDisplay:
    # ANSI color codes
    RESET = "\033[0m"

    # Foreground colors
    RED = "\033[91m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    BLUE = "\033[94m"
    MAGENTA = "\033[95m"
    CYAN = "\033[96m"
    WHITE = "\033[97m"
    GRAY = "\033[90m"

    # Background colors (normal)
    BG_RED = "\033[41m"
    BG_GREEN = "\033[42m"
    BG_YELLOW = "\033[43m"
    BG_BLUE = "\033[44m"
    BG_MAGENTA = "\033[45m"
    BG_CYAN = "\033[46m"
    BG_WHITE = "\033[47m"
    BG_GRAY = "\033[100m"

    # Background colors (bright)
    BG_BRIGHT_BLACK = "\033[100m"
    BG_BRIGHT_RED = "\033[101m"
    BG_BRIGHT_GREEN = "\033[102m"
    BG_BRIGHT_YELLOW = "\033[103m"
    BG_BRIGHT_BLUE = "\033[104m"
    BG_BRIGHT_MAGENTA = "\033[105m"
    BG_BRIGHT_CYAN = "\033[106m"
    BG_BRIGHT_WHITE = "\033[107m"

    def __init__(self, width: int, height: int) -> None:
        """Initialize display with maze dimensions and default colors."""
        self.width: int = width
        self.height: int = height

        self.colors = {
            'entry': self.BG_GREEN,
            'exit': self.BG_RED,
            'highlight': self.BG_BRIGHT_MAGENTA,
            'pattern': self.BG_BRIGHT_YELLOW,
            'path': self.YELLOW,
            'wall': self.WHITE,
            'unvisited': self.BG_GRAY,
            'search': self.CYAN
        }

    def set_color(self, element: str, color: str) -> None:
        """Set custom color for a display element."""
        if element in self.colors:
            self.colors[element] = color

    def set_pattern_color(self, color_name: str) -> None:
        """Set the '42' pattern background color by name."""
        color_map = {
            'cyan': self.BG_BRIGHT_CYAN,
            'yellow': self.BG_BRIGHT_YELLOW,
            'magenta': self.BG_BRIGHT_MAGENTA,
            'blue': self.BG_BRIGHT_BLUE,
            'red': self.BG_BRIGHT_RED,
            'green': self.BG_BRIGHT_GREEN,
            'white': self.BG_BRIGHT_WHITE,
            'black': self.BG_BRIGHT_BLACK,
            'gray': self.BG_GRAY
        }

        if color_name.lower() in color_map:
            self.colors['pattern'] = color_map[color_name.lower()]
        else:
            print(f"Warning: Unknown color '{color_name}'. Using default.")

    @staticmethod
    def clear_screen() -> None:
        """Clear terminal screen using ANSI escape codes."""
        print("\033[H", flush=True)

    def path_to_cells(self,
                      entry: Tuple[int, int],
                      path: str) -> Set[Tuple[int, int]]:
        """Convert path string to set of cell coordinates."""
        x, y = entry
        cells: Set[Tuple[int, int]] = {(x, y)}

        for move in path:
            if move == "N":
                y -= 1
            elif move == "S":
                y += 1
            elif move == "E":
                x += 1
            elif move == "W":
                x -= 1
            cells.add((x, y))

        return cells

    def display_ascii(self,
                      grid: List[List[Cell]],
                      entry: Tuple[int, int],
                      exit: Tuple[int, int],
                      pattern_cells: Set[Tuple[int, int]],
                      path: Optional[str] = None,
                      highlight: Optional[Tuple[int, int]] = None,
                      show_generation: bool = True,
                      visited_cells: Optional[Set[Tuple[int, int]]] = None
                      ) -> None:
        """Render maze grid as ASCII art with colors."""
        path_cells: Set[Tuple[int, int]] = set()
        if path:
            path_cells = self.path_to_cells(entry, path)

        for x in range(self.width):
            print(f"{self.colors['wall']}+---{self.RESET}", end="")
        print(f"{self.colors['wall']}+{self.RESET}")

        for y in range(self.height):
            for x in range(self.width):
                cell = grid[y][x]

                if cell.west:
                    print(f"{self.colors['wall']}|{self.RESET}", end="")
                else:
                    print(" ", end="")

                if (x, y) == entry:
                    print(f"{self.colors['entry']} S {self.RESET}", end="")
                elif (x, y) == exit:
                    print(f"{self.colors['exit']} E {self.RESET}", end="")
                elif highlight and (x, y) == highlight:
                    print(f"{self.colors['highlight']}   {self.RESET}", end="")
                elif (x, y) in pattern_cells:
                    print(f"{self.colors['pattern']}   {self.RESET}", end="")
                elif show_generation and not cell.visited:
                    print(f"{self.colors['unvisited']}   {self.RESET}", end="")
                elif visited_cells and (x, y) in visited_cells:
                    print(f"{self.colors['search']} * {self.RESET}", end="")
                elif path and (x, y) in path_cells:
                    print(f"{self.colors['path']} # {self.RESET}", end="")
                else:
                    print("   ", end="")

            print(f"{self.colors['wall']}|{self.RESET}")

            for x in range(self.width):
                cell = grid[y][x]
                if cell.south:
                    print(f"{self.colors['wall']}+---{self.RESET}", end="")
                else:
                    print(f"{self.colors['wall']}+{self.RESET}   ", end="")
            print(f"{self.colors['wall']}+{self.RESET}")
