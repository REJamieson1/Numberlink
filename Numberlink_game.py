import pygame
from collections import defaultdict
from collections import deque
import random as rand
import math

#Root number of nodes in game
size = 11


def BFS_path(graph, dot_1):
    '''
    BFS that finds all reachable nodes and the shortest paths
    '''
    E = set()
    E.add(dot_1)
    queue = deque([[dot_1]])
    paths = {}

    while queue:

        path = queue.popleft()
        vector = path[-1]

        more_nodes = graph[vector]
        rand.shuffle(more_nodes)
        for adj_node in more_nodes:
            if adj_node not in E:
                new_path = list(path)
                new_path.append(adj_node)
                paths[adj_node] = new_path
                E.add(adj_node)
                queue.append(new_path)

    return E, paths


def remove_node(graph, node):
    '''
    Takes in a graph and a node and removes all instences of the node'''
    for neighbor in graph.get(node, []):
        graph[neighbor].remove(node)
        
    if node in graph:
        del graph[node]


pygame.font.init()
screen = pygame.display.set_mode((600, 600))
running = True
G = defaultdict(list)
open_nodes = defaultdict(list)
all_nodes = set()

for x in range(size):
    for y in range(size):
        all_nodes.add((x,y))

#generating graph
for node in all_nodes:
    if (node[0]+1, node[1]) in all_nodes:
        G[node].append((node[0]+1, node[1]))
        open_nodes[node].append((node[0]+1, node[1]))
    if (node[0], node[1]+1) in all_nodes:
        G[node].append((node[0], node[1]+1))
        open_nodes[node].append((node[0], node[1]+1))
    if (node[0]-1, node[1]) in all_nodes:
        G[node].append((node[0]-1, node[1]))
        open_nodes[node].append((node[0]-1, node[1]))
    if (node[0], node[1]-1) in all_nodes:
        G[node].append((node[0], node[1]-1))
        open_nodes[node].append((node[0], node[1]-1))

dots = set()
game_paths = []
blanks = []
solves = 0

#main
while open_nodes:
    #find first node
    dot_1 = rand.sample(set(open_nodes.keys()), 1)[0]
    reaches, path_options = BFS_path(open_nodes, dot_1)

    #Find and solve holes
    if not path_options:
        fix_hole = False

        for adj_node in G[dot_1]:
            if adj_node in dots:

                for i, gp in enumerate(game_paths):
                    if gp[0] == adj_node:
                        game_paths[i] = [dot_1] + gp
                        dots.add(dot_1)
                        remove_node(open_nodes, dot_1)
                        dots.remove(adj_node)
                    elif gp[-1] == adj_node:
                        game_paths[i] = gp + [dot_1]
                        dots.add(dot_1)
                        remove_node(open_nodes, dot_1)
                        dots.remove(adj_node)
                fix_hole = True
                break

        if fix_hole:
            continue

        blanks.append(dot_1)
        remove_node(open_nodes, dot_1)
        continue

    #Choose second node
    dot_2 = rand.choices(list(path_options.keys()), weights=[len(path)**2 for path in sorted(path_options.values())] , k=1)[-1]
    path = path_options[dot_2]

    if len(path) == 2 and solves > 60:
        solves += 1
        continue

    #Solidify
    for node in path:
        remove_node(open_nodes, node)
    game_paths.append(path)
    dots.add(dot_1)
    dots.add(dot_2)
    

def find_coord(node, size):
    '''
    Finds the center coordinate of a node
    '''
    return (((node[0]+1) * (600/size)) - 600/(size * 2), ((node[1]+1) * (600/size)) - 600/(size * 2))


def find_rect_coords(node, size):
    '''
    Finds position and size of a square for a node
    '''
    return pygame.Rect((node[0]*600/size) + (600/size/4.242), (node[1]*600/size) + (600/size/4.242), 350/size, 350/size)


def coord_to_node(coord, size):
    '''
    Finds the node from the coordinate
    '''
    return (math.floor(coord[0]/600 * size), math.floor(coord[1]/600 * size))


def graph_colors(paths):
    '''
    Initializes a dictionary of pairs and colors
    '''
    color_graph = {}
    incrementor = int(254/(len(paths)))

    for i, path in enumerate(paths):
        color = [255, 255 - i * incrementor, i * incrementor]
        rand.shuffle(color)
        color_graph[str(path[0])] = (tuple(color), i)
        color_graph[str(path[-1])] = (tuple(color), i)
    
    return color_graph


def graph_dots(paths, size, color_graph):
    '''
    Displays dots with numbers
    '''
    for i, path in enumerate(paths):
        pygame.draw.circle(screen, color_graph[str(path[0])][0], (find_coord(path[0], size)), int(.35*600/size))
        screen.blit(font.render(str(len(paths) - i), True, (0,0,0)), find_coord(path[0], size))
        pygame.draw.circle(screen, color_graph[str(path[-1])][0], (find_coord(path[-1], size)), int(.35*600/size))
        screen.blit(font.render(str(len(paths) - i), True, (0,0,0)), find_coord(path[-1], size))


def graph_paint(node, current_color, size):
    '''
    Displays square with color
    '''
    pygame.draw.rect(screen, current_color[0], find_rect_coords(node, size))


def graph_blanks(blanks, size):
    '''
    Shows holes
    '''
    for blank in blanks:
        pygame.draw.rect(screen, (255, 255, 255), find_rect_coords(blank, size))


color_graph = graph_colors(game_paths)
current_color = None
paint = {}
font = pygame.font.Font('freesansbold.ttf', int((600/size)/3))
end_font = pygame.font.Font('freesansbold.ttf', 100)
game = True

#Game loop
while running:
    if game:
        screen.fill((0,0,0))
        
        for i in range(1, size):
            pygame.draw.line(screen, (255, 255, 255), (int(i*600/size), 0), (int(i*600/size), 600), width=int(5/size)+1)
            pygame.draw.line(screen, (255, 255, 255), (0, int(i*600/size)), (600, int(i*600/size)), width=int(5/size)+1)
        
        graph_dots(game_paths, size, color_graph)
        graph_blanks(blanks, size)

        for s, c in paint.items():
            if c:
                graph_paint(eval(s), c, size)
        
        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                pygame.quit()
            #User drawing
            if len(paint.keys()) + len(dots) < size**2:
                if event.type == pygame.MOUSEBUTTONDOWN:
                    mouse = pygame.mouse.get_pos()
                    mouse = coord_to_node(mouse, size)
                    if str(mouse) in set(color_graph.keys()):
                        if current_color != color_graph[str(mouse)]:
                            current_color = color_graph[str(mouse)]
                        else:
                            current_color = None

                    elif current_color:
                        if str(mouse) in paint:
                            del paint[str(mouse)]
                        else:
                            paint[str(mouse)] = current_color
            else:
                game = False
    #Game over
    else:
        screen.blit(end_font.render('You Win!', True, (0,0,255)), (100,150))
        screen.blit(end_font.render('You Win!', True, (255,0,0)), (105,155))
        screen.blit(end_font.render('You Win!', True, (0,0,255)), (100,350))
        screen.blit(end_font.render('You Win!', True, (255,0,0)), (105,355))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                pygame.quit()

        pygame.display.flip()
