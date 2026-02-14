from typing import Tuple, Optional, Set, Dict, List
from collections import deque
import random
import time
from mazegen.maze_display import MazeDisplay, Cell
import sys
import os


class MazeGenerator:
    """Initialize maze generator with dimensions and optional seed."""
    def __init__(self,
                 width: int,
                 height: int,
                 seed: Optional[int] = None) -> None:
        self.width: int = width
        self.height: int = height
        self.pattern_cells: Set[Tuple[int, int]] = set()
        self.random = random.Random(seed)

        self.grid: List[List[Cell]] = []
        for y in range(self.height):
            row: List[Cell] = []
            for x in range(self.width):
                row.append(Cell())
            self.grid.append(row)

    def add_42_pattern(self) -> bool:
        """Add '42' pattern to the center of the maze grid."""
        pattern = [
            "# # ###",
            "# #   #",
            "### ###",
            "  # #  ",
            "  # ###"
        ]

        pattern_height = len(pattern)
        pattern_width = len(pattern[0])

        if self.width < pattern_width + 2 or self.height < pattern_height + 2:
            print("Warning: Maze too small for '42' pattern. \n")
            answer = input("Continuing without it? [Yes/No]: ")
            if answer.lower() == "yes":
                os.system("clear")
            elif answer.lower() == "no":
                sys.exit()
            else:
                print("Incorrect input.")
                sys.exit()
            return False

        start_x = (self.width - pattern_width) // 2
        start_y = (self.height - pattern_height) // 2

        self.pattern_cells = set()

        for row_num, row in enumerate(pattern):
            for col_num, char in enumerate(row):
                if char == '#':
                    maze_x = start_x + col_num
                    maze_y = start_y + row_num

                    cell = self.grid[maze_y][maze_x]
                    cell.north = True
                    cell.east = True
                    cell.south = True
                    cell.west = True
                    cell.visited = True

                    self.pattern_cells.add((maze_x, maze_y))

        return True

    def _remove_wall(self, x1: int, y1: int, x2: int, y2: int) -> None:
        """Remove wall between two adjacent cells."""
        cell1 = self.grid[y1][x1]
        cell2 = self.grid[y2][x2]

        if y2 < y1:
            cell1.north = False
            cell2.south = False
        elif y2 > y1:
            cell1.south = False
            cell2.north = False
        elif x2 > x1:
            cell1.east = False
            cell2.west = False
        elif x2 < x1:
            cell1.west = False
            cell2.east = False

    def generate_backtracking(self,
                              entry: Tuple[int, int],
                              display: Optional[MazeDisplay] = None,
                              delay: float = 0.05) -> List[List[Cell]]:
        """Generate maze using recursive backtracking (DFS) algorithm."""
        entry_x, entry_y = entry
        start_cell = self.grid[entry_y][entry_x]
        start_cell.visited = True

        stack: List[Tuple[int, int]] = [(entry_x, entry_y)]

        while stack:
            x, y = stack[-1]
            neighbors: List[Tuple[int, int]] = []

            if y > 0 and not self.grid[y-1][x].visited:
                if (x, y-1) not in self.pattern_cells:
                    neighbors.append((x, y-1))

            if x < self.width - 1 and not self.grid[y][x+1].visited:
                if (x+1, y) not in self.pattern_cells:
                    neighbors.append((x+1, y))

            if y < self.height - 1 and not self.grid[y+1][x].visited:
                if (x, y+1) not in self.pattern_cells:
                    neighbors.append((x, y+1))

            if x > 0 and not self.grid[y][x-1].visited:
                if (x-1, y) not in self.pattern_cells:
                    neighbors.append((x-1, y))

            if neighbors:
                next_x, next_y = self.random.choice(neighbors)

                self._remove_wall(x, y, next_x, next_y)

                self.grid[next_y][next_x].visited = True
                stack.append((next_x, next_y))

                if display is not None:
                    display.clear_screen()
                    display.display_ascii(self.grid, entry, entry,
                                          self.pattern_cells,
                                          highlight=(next_x, next_y),
                                          show_generation=True)
                    time.sleep(delay)
            else:
                stack.pop()
        return self.grid

    def _get_neighbors(self, x: int, y: int) -> List[Tuple[int, int]]:
        """Get valid neighboring cells for a given position."""
        neighbors: List[Tuple[int, int]] = []

        if y > 0 and (x, y-1) not in self.pattern_cells:
            neighbors.append((x, y-1))
        if x < self.width - 1 and (x+1, y) not in self.pattern_cells:
            neighbors.append((x+1, y))
        if y < self.height - 1 and (x, y+1) not in self.pattern_cells:
            neighbors.append((x, y+1))
        if x > 0 and (x-1, y) not in self.pattern_cells:
            neighbors.append((x-1, y))

        return neighbors

    def generate_prims(self,
                       start: Tuple[int, int],
                       display: Optional[MazeDisplay] = None,
                       delay: float = 0.02) -> List[List[Cell]]:
        """Generate maze using Prim's algorithm."""

        start_x, start_y = start
        visited = set()
        frontier: List[Tuple[int, int]] = []

        self.grid[start_y][start_x].visited = True
        visited.add((start_x, start_y))

        for neighbor in self._get_neighbors(start_x, start_y):
            if neighbor not in frontier:
                frontier.append(neighbor)

        while frontier:
            current_x, current_y = self.random.choice(frontier)
            frontier.remove((current_x, current_y))

            neighbors = self._get_neighbors(current_x, current_y)
            visited_neighbors = [n for n in neighbors if n in visited]

            if visited_neighbors:
                neighbor_x, neighbor_y = self.random.choice(visited_neighbors)

                self._remove_wall(current_x, current_y, neighbor_x, neighbor_y)

                self.grid[current_y][current_x].visited = True
                visited.add((current_x, current_y))

                for nx, ny in neighbors:
                    if (nx, ny) not in visited and (nx, ny) not in frontier:
                        frontier.append((nx, ny))

                if display is not None:
                    MazeDisplay.clear_screen()
                    display.display_ascii(
                        self.grid,
                        start,
                        start,
                        self.pattern_cells,
                        highlight=(current_x, current_y),
                        show_generation=True
                    )
                    time.sleep(delay)
        return self.grid

    def reset_visited(self) -> None:
        """Reset visited flag for all cells in the grid."""
        for y in range(self.height):
            for x in range(self.width):
                self.grid[y][x].visited = False

    def solve_bfs(self,
                  entry: Tuple[int, int],
                  exit: Tuple[int, int],
                  display: Optional[MazeDisplay] = None,
                  delay: float = 0.05) -> str:
        """Find shortest path from entry to exit using BFS."""
        queue: deque[Tuple[int, int]] = deque()
        queue.append(entry)

        visited: Set[Tuple[int, int]] = set()
        visited.add(entry)
        parent: Dict[Tuple[int, int], Tuple[Tuple[int, int], str]] = {}

        while queue:
            x, y = queue.popleft()
            cell = self.grid[y][x]

            if display is not None:
                display.clear_screen()
                display.display_ascii(self.grid,
                                      entry,
                                      exit,
                                      self.pattern_cells,
                                      highlight=(x, y),
                                      show_generation=False,
                                      visited_cells=visited)
                time.sleep(delay)

            if (x, y) == exit:
                break
            if y > 0 and not cell.north and (x, y-1) not in visited:
                queue.append((x, y-1))
                visited.add((x, y-1))
                parent[(x, y-1)] = ((x, y), "N")
            if (x < self.width - 1 and
                not cell.east and
               (x+1, y) not in visited):
                queue.append((x+1, y))
                visited.add((x+1, y))
                parent[(x+1, y)] = ((x, y), "E")
            if (y < self.height - 1 and
                not cell.south and
               (x, y+1) not in visited):
                queue.append((x, y+1))
                visited.add((x, y+1))
                parent[(x, y+1)] = ((x, y), "S")
            if x > 0 and not cell.west and (x-1, y) not in visited:
                queue.append((x-1, y))
                visited.add((x-1, y))
                parent[(x-1, y)] = ((x, y), "W")

        path: List[str] = []
        current = exit
        while current != entry:
            if current not in parent:
                return ""
            current, direction = parent[current]
            path.append(direction)
        path.reverse()
        return "".join(path)

    def write_maze_hex(self,
                       filename: str,
                       entry: Tuple[int, int],
                       exit: Tuple[int, int],
                       path: str) -> None:
        """Write maze to file in hexadecimal format with path."""
        with open(filename, "w") as f:
            for y in range(self.height):
                row: List[str] = []
                for x in range(self.width):
                    cell = self.grid[y][x]
                    value: int = 0
                    if cell.north:
                        value += 1
                    if cell.east:
                        value += 2
                    if cell.south:
                        value += 4
                    if cell.west:
                        value += 8
                    row.append(format(value, "X"))
                f.write("".join(row) + "\n")
            f.write(f"\n{entry[0]},{entry[1]}\n")
            f.write(f"{exit[0]},{exit[1]}\n")
            f.write(f"{path}\n")

    def break_walls(self, chance: float = 0.1) -> None:
        """Randomly break walls to create imperfect maze."""
        for y in range(self.height):
            for x in range(self.width):
                if (x, y) in self.pattern_cells:
                    continue

                if self.random.random() < chance:
                    cell = self.grid[y][x]
                    direction = self.random.choice(["N", "E", "S", "W"])

                    if direction == "N" and y > 0:
                        if (x, y-1) not in self.pattern_cells:
                            if not self._large_open_area(x, y, x, y-1):
                                cell.north = False
                                self.grid[y-1][x].south = False

                    elif direction == "S" and y < self.height - 1:
                        if (x, y+1) not in self.pattern_cells:
                            if not self._large_open_area(x, y, x, y+1):
                                cell.south = False
                                self.grid[y+1][x].north = False

                    elif direction == "E" and x < self.width - 1:
                        if (x+1, y) not in self.pattern_cells:
                            if not self._large_open_area(x, y, x+1, y):
                                cell.east = False
                                self.grid[y][x+1].west = False

                    elif direction == "W" and x > 0:
                        if (x-1, y) not in self.pattern_cells:
                            if not self._large_open_area(x, y, x-1, y):
                                cell.west = False
                                self.grid[y][x-1].east = False

    def _large_open_area(self, x1: int, y1: int, x2: int, y2: int) -> bool:
        """
        Check if removing the wall between (x1,y1) and (x2,y2) would create
        a 3x3 or larger open area.
        """
        for check_x, check_y in [(x1, y1), (x2, y2)]:
            min_start_x = max(0, check_x - 2)
            max_start_x = min(self.width - 2, check_x + 1)
            min_start_y = max(0, check_y - 2)
            max_start_y = min(self.height - 2, check_y + 1)

            for start_x in range(min_start_x, max_start_x):
                for start_y in range(min_start_y, max_start_y):
                    if self._is_area_open(start_x, start_y, 3, 3,
                                          x1, y1, x2, y2):
                        return True

        return False

    def _is_area_open(self,
                      start_x: int,
                      start_y: int,
                      width: int,
                      height: int,
                      removed_x1: int,
                      removed_y1: int,
                      removed_x2: int,
                      removed_y2: int) -> bool:
        """
        Check if a rectangular area would be
        completely open (no internal walls).
        Simulates removing the wall between
        (removed_x1, removed_y1) and (removed_x2, removed_y2).
        """
        for y in range(start_y, start_y + height):
            for x in range(start_x, start_x + width):
                if (x, y) in self.pattern_cells:
                    return False

                cell = self.grid[y][x]

                if x < start_x + width - 1:
                    has_east_wall = cell.east

                    if ((x == removed_x1 and y == removed_y1 and
                         x + 1 == removed_x2 and y == removed_y2) or
                        (x == removed_x2 and y == removed_y2 and
                         x + 1 == removed_x1 and y == removed_y1)):
                        has_east_wall = False

                    if has_east_wall:
                        return False

                if y < start_y + height - 1:
                    has_south_wall = cell.south

                    if ((x == removed_x1 and y == removed_y1 and
                         x == removed_x2 and y + 1 == removed_y2) or
                        (x == removed_x2 and y == removed_y2 and
                         x == removed_x1 and y + 1 == removed_y1)):
                        has_south_wall = False

                    if has_south_wall:
                        return False

        return True
