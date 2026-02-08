from typing import Tuple, Optional, Set, Dict, List
from collections import deque
import random
import time
from mazegen.maze_display import MazeDisplay, Cell
import sys
import os


class MazeGenerator:
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

    def generate_backtracking(self,
                              entry: Tuple[int, int],
                              display: Optional[MazeDisplay] = None,
                              delay: float = 0.05) -> List[List[Cell]]:
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
                current = self.grid[y][x]
                neighbor = self.grid[next_y][next_x]

                if next_y < y:
                    current.north = False
                    neighbor.south = False
                elif next_y > y:
                    current.south = False
                    neighbor.north = False
                elif next_x > x:
                    current.east = False
                    neighbor.west = False
                elif next_x < x:
                    current.west = False
                    neighbor.east = False

                neighbor.visited = True
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

    def _remove_wall(self, x1: int, y1: int, x2: int, y2: int) -> None:
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

    def generate_prims(self,
                       start: Tuple[int, int],
                       display: Optional[MazeDisplay] = None,
                       delay: float = 0.02) -> List[List[Cell]]:

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
                    from mazegen.maze_display import MazeDisplay
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
        for y in range(self.height):
            for x in range(self.width):
                self.grid[y][x].visited = False

    def solve_bfs(self,
                  entry: Tuple[int, int],
                  exit: Tuple[int, int],
                  display: Optional[MazeDisplay] = None,
                  delay: float = 0.05) -> str:
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
        for y in range(self.height):
            for x in range(self.width):
                if (x, y) in self.pattern_cells:
                    continue

                if self.random.random() < chance:
                    cell = self.grid[y][x]
                    direction = self.random.choice(["N", "E", "S", "W"])

                    if direction == "N" and y > 0:
                        if (x, y-1) not in self.pattern_cells:
                            cell.north = False
                            self.grid[y-1][x].south = False
                    elif direction == "S" and y < self.height - 1:
                        if (x, y+1) not in self.pattern_cells:
                            cell.south = False
                            self.grid[y+1][x].north = False
                    elif direction == "E" and x < self.width - 1:
                        if (x+1, y) not in self.pattern_cells:
                            cell.east = False
                            self.grid[y][x+1].west = False
                    elif direction == "W" and x > 0:
                        if (x-1, y) not in self.pattern_cells:
                            cell.west = False
                            self.grid[y][x-1].east = False
