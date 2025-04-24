import pygame


class Tile(object):
    def __init__(self, filename, *flags):
        self.filename = filename
        self.image = pygame.image.load(f"images\\{filename}.png")
        self.flags = flags[0]


class Tilemap(object):
    def __init__(self, filename, surf, level):
        self.filename = filename
        self.surf = surf
        self.hint_text = None
        self.textures = {}
        self.map_width = 0
        self.map_height = 0
        self.tilemap = self.tilemapFromFile(filename, f"mapline{level}", f"maphint{level}")

    def tilemapFromFile(self, filename, keyword1, keyword2=None):
        fp = open(filename, 'r')
        lines = fp.readlines()
        fp.close()
        map_string = ""
        max_line = 0
        for line in lines:
            line = line.strip()
            if line == "":
                continue
            if line[0] == '#':
                continue
            keyword, keyvalue = line.split("=")
            if keyword == keyword1:
                map_string += keyvalue.replace('"', '')
                map_string += "\n"
                self.map_height += 1
                max_line = max(max_line, len(keyvalue) // 2 - 1)
            elif keyword == keyword2:
                self.hint_text = keyvalue.replace('"', '')
            elif keyword == "loadTexture":
                texture_key, texture_filename, *texture_flags = keyvalue.split(",")
                self.textures[texture_key.strip()] = Tile(texture_filename.strip(), texture_flags)
        self.map_width = max_line
        local_tilemap = self.tilemapFromString(map_string.strip())
        return local_tilemap

    def tilemapFromString(self, tile_map_string):
        local_tilemap = []
        for rows in range(self.map_height):
            local_tilemap.append(["  "] * self.map_width)
        tile_map_string = tile_map_string.strip()
        lines = tile_map_string.split("\n")
        row = 0
        for line in lines:
            for column in range(0, self.map_width):
                local_tilemap[row][column] = line[column * 2: column * 2 + 2]
            row += 1
        return local_tilemap

    def renderTilemap(self):
        map_origin_x = self.surf.get_width() // 2 - self.map_width * 16
        map_origin_y = self.surf.get_height() // 2 - self.map_height * 16
        on_mirror = False
        for row in range(self.map_height):
            for column in range(self.map_width):
                cell_contents = self.tilemap[row][column]
                if cell_contents != "  ":
                    if cell_contents in self.textures:
                        cell = self.textures[cell_contents]
                        self.surf.blit(cell.image, (column * 32 + map_origin_x, row * 32 + map_origin_y))
                        if spawn_entities:
                            if "SpawnPlayer" in cell.flags:
                                entity_list.append(PlayerChar("Player", win, column * 32 + map_origin_x,
                                                              row * 32 + map_origin_y))
                                if "Mirror" in cell.flags:
                                    on_mirror = True
                            if "SpawnReflection" in cell.flags:
                                if on_mirror:
                                    entity_list.append(ReflectionChar("Reflection", win, column * 32 + map_origin_x,
                                                                      row * 32 + map_origin_y, True))
                                else:
                                    entity_list.append(ReflectionChar("Reflection", win, column * 32 + map_origin_x,
                                                                      row * 32 + map_origin_y))
                            if "SpawnBox" in cell.flags:
                                entity_list.append(MovableObject("Box", win, column * 32 + map_origin_x,
                                                                 row * 32 + map_origin_y))

    def buttonPress(self):
        for row in range(self.map_height):
            for column in range(self.map_width):
                cell_contents = self.tilemap[row][column]
                if cell_contents != "  ":
                    if cell_contents in self.textures:
                        if cell_contents == "G1":
                            self.tilemap[row][column] = "G5"
                        elif cell_contents == "G2":
                            self.tilemap[row][column] = "G6"
                        elif cell_contents == "G3":
                            self.tilemap[row][column] = "G7"
                        elif cell_contents == "G4":
                            self.tilemap[row][column] = "G8"
                        elif cell_contents == "G5":
                            self.tilemap[row][column] = "G1"
                        elif cell_contents == "G6":
                            self.tilemap[row][column] = "G2"
                        elif cell_contents == "G7":
                            self.tilemap[row][column] = "G3"
                        elif cell_contents == "G8":
                            self.tilemap[row][column] = "G4"

    def typeDisplay(self):
        hint_font = pygame.font.Font("font\\Dosis-Regular.ttf", 24)
        hint_text = hint_font.render(self.hint_text, False, (255, 255, 255))
        win.blit(hint_text, (win.get_width() // 2 - hint_text.get_width() // 2,
                             win.get_height() // 2 + self.map_height * 16))

    def checkTilemapCollision(self, x, y):
        collide_list = []
        for row in range(self.map_height):
            for column in range(self.map_width):
                cell_contents = self.tilemap[row][column]
                if cell_contents != "  ":
                    if cell_contents in self.textures:
                        cell = self.textures[cell_contents]
                        tile_x_min = column * 32 + self.surf.get_width() // 2 - self.map_width * 16
                        tile_x_max = tile_x_min + 31
                        tile_y_min = row * 32 + self.surf.get_height() // 2 - self.map_height * 16
                        tile_y_max = tile_y_min + 31
                        if tile_x_max > x and tile_x_min < x + 32:
                            if tile_y_max > y and tile_y_min < y + 32:
                                if cell not in collide_list:
                                    collide_list.append(cell)
        return collide_list

    def checkWinCondition(self):
        goal_number = 0
        for row in range(self.map_height):
            for column in range(self.map_width):
                cell_contents = self.tilemap[row][column]
                if cell_contents == "GL":
                    goal_number += 1
        return goal_number


class MovableObject(object):
    def __init__(self, filename, surf, x, y, facing="South"):
        self.filename = filename
        self.image = pygame.image.load(f"images\\{filename}.png")
        self.surf = surf
        self.x = x
        self.y = y
        self.facing = facing
        self.moves = [(x, y, facing)]

    def move(self, dx, dy):
        new_x = self.x + dx
        new_y = self.y + dy
        self.x = new_x
        self.y = new_y
        self.moves.append((self.x, self.y, self.facing))

    def wait(self):
        self.moves.append((self.x, self.y, self.facing))

    def undo(self):
        if len(self.moves) > 1:
            del self.moves[len(self.moves) - 1]
            self.x, self.y, self.facing = self.moves[len(self.moves) - 1]

    def restart(self):
        self.x, self.y, self.facing = self.moves[0]
        self.moves = [(self.x, self.y, self.facing)]

    def checkForWallMirrors(self, tile_map):
        map_origin_x = tile_map.surf.get_width() // 2 - tile_map.map_width * 16
        map_origin_y = tile_map.surf.get_height() // 2 - tile_map.map_height * 16
        entity_cell_x = (self.x - map_origin_x) // 32
        entity_cell_y = (self.y - map_origin_y) // 32
        for row in range(entity_cell_y, tile_map.map_height):
            cell_contents = tile_map.tilemap[row][entity_cell_x]
            if cell_contents != "  ":
                if cell_contents in tile_map.textures:
                    cell = tile_map.textures[cell_contents]
                    if "Wall" in cell.flags:
                        if cell_contents == "MS":
                            return "South"
                        else:
                            break
        for row in range(entity_cell_y, -1, -1):
            cell_contents = tile_map.tilemap[row][entity_cell_x]
            if cell_contents != "  ":
                if cell_contents in tile_map.textures:
                    cell = tile_map.textures[cell_contents]
                    if "Wall" in cell.flags:
                        if cell_contents == "MN":
                            return "North"
                        else:
                            break
        for column in range(entity_cell_x, tile_map.map_width):
            cell_contents = tile_map.tilemap[entity_cell_y][column]
            if cell_contents != "  ":
                if cell_contents in tile_map.textures:
                    cell = tile_map.textures[cell_contents]
                    if "Wall" in cell.flags:
                        if cell_contents == "ME":
                            return "East"
                        else:
                            break
        for column in range(entity_cell_x, -1, -1):
            cell_contents = tile_map.tilemap[entity_cell_y][column]
            if cell_contents != "  ":
                if cell_contents in tile_map.textures:
                    cell = tile_map.textures[cell_contents]
                    if "Wall" in cell.flags:
                        if cell_contents == "MW":
                            return "West"
                        else:
                            break
        return None

    def render(self):
        self.surf.blit(self.image, (self.x, self.y))


class PlayerChar(MovableObject):
    def move(self, dx, dy):
        new_x = self.x + dx
        new_y = self.y + dy
        if new_x < self.x:
            self.facing = "West"
        if new_y < self.y:
            self.facing = "North"
        if new_x > self.x:
            self.facing = "East"
        if new_y > self.y:
            self.facing = "South"
        self.x = new_x
        self.y = new_y
        self.moves.append((self.x, self.y, self.facing))

    def render(self):
        if self.facing == "South":
            self.surf.blit(self.image, (self.x, self.y), (0, 0, 32, 32))
        elif self.facing == "North":
            self.surf.blit(self.image, (self.x, self.y), (0, 64, 32, 32))
        elif self.facing == "West":
            temp_img = pygame.transform.flip(self.image, True, False)
            self.surf.blit(temp_img, (self.x, self.y), (temp_img.get_width() - 32, 96, 32, 32))
        elif self.facing == "East":
            self.surf.blit(self.image, (self.x, self.y), (0, 96, 32, 32))


class ReflectionChar(PlayerChar):
    def __init__(self, filename, surf, x, y, active=False, facing="South"):
        super().__init__(filename, surf, x, y, facing)
        self.active = active
        self.flip = "None"

    def render(self):
        if self.active:
            if self.facing == "South":
                self.surf.blit(self.image, (self.x, self.y), (0, 0, 32, 32))
            elif self.facing == "North":
                self.surf.blit(self.image, (self.x, self.y), (0, 64, 32, 32))
            elif self.facing == "West":
                temp_img = pygame.transform.flip(self.image, True, False)
                self.surf.blit(temp_img, (self.x, self.y), (temp_img.get_width() - 32, 96, 32, 32))
            elif self.facing == "East":
                self.surf.blit(self.image, (self.x, self.y), (0, 96, 32, 32))
        else:
            self.surf.blit(self.image, (self.x, self.y), (0, 32, 32, 32))


pygame.init()
win = pygame.display.set_mode((1780, 980))
clock = pygame.time.Clock()
playing = True
in_game = False
main_menu = True
done = False
minutes = 0
seconds = 0
music_intro = pygame.mixer.Sound("audio\\music_intro.wav")
music_loop = pygame.mixer.Sound("audio\\music_loop.wav")
finish = pygame.mixer.Sound("audio\\goal.ogg")
press = pygame.mixer.Sound("audio\\button_press.wav")
unpress = pygame.mixer.Sound("audio\\button_unpress.wav")
awaken = pygame.mixer.Sound("audio\\on_mirror.ogg")
sleep = pygame.mixer.Sound("audio\\off_mirror.wav")
push = pygame.mixer.Sound("audio\\box_move.ogg")
fall = pygame.mixer.Sound("audio\\fall.wav")
push.set_volume(0.25)
press.set_volume(2)
unpress.set_volume(2)
font = pygame.font.Font("font\\Dosis-Regular.ttf", 36)
title_font = pygame.font.Font("font\\Dosis-Bold.ttf", 148)
entity_list = []
levels = ["01", "02", "03", "04", "05", "06", "07", "08", "09"]
level_names = ["Simple spiral", "Locked away", "Magic spiral", "Broken ground", "A straight shot",
               "Going separate ways", "Hall of mirrors", "In umbra speculi", "Backed against a wall"]
level_number = 0
tilemap = Tilemap("levels.txt", win, levels[level_number])
menu_map = Tilemap("menu.txt", win, "00")
timer = font.render("Time elapsed: 0:00.000", False, (255, 255, 255))
button_pressed = False
spawn_entities = True
reflection_active = False
wall_reflection = False
box_blocked = False
box_block_count = 0
num_pressed = 0
alive = True
win_count = 0
wait_time = 120
win_state = False
display_hint = True

while playing:
    if main_menu:
        clock.tick(60)
        play_color = (0, 0, 0)
        quit_color = (0, 0, 0)
        event = pygame.event.poll()
        keys = pygame.key.get_pressed()
        mouse_x, mouse_y = pygame.mouse.get_pos()
        if keys[pygame.K_ESCAPE] or event.type == pygame.QUIT:
            playing = False
            break
        if win.get_width() // 2 - 200 < mouse_x < win.get_width() // 2 + 200 and\
                win.get_height() // 2 - 100 < mouse_y < win.get_height() // 2:
            play_color = (127, 127, 127)
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                main_menu = False
                in_game = True
        if win.get_width() // 2 - 200 < mouse_x < win.get_width() // 2 + 200 and\
                win.get_height() // 2 + 150 < mouse_y < win.get_height() // 2 + 250:
            quit_color = (127, 127, 127)
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                playing = False
                break
        win.fill((34, 32, 52))
        menu_map.renderTilemap()
        title = title_font.render("The Mirror Temple", False, (179, 226, 236))
        subtitle = font.render("(Title WIP)", False, (179, 226, 236))
        play = font.render("Play", False, (255, 255, 255))
        esc = font.render("Quit", False, (255, 255, 255))
        win.blit(title, (win.get_width() // 2 - title.get_width() // 2, 60))
        win.blit(subtitle, (win.get_width() // 2 - title.get_width() // 2 + 50, title.get_height() + 30))
        pygame.draw.rect(win, play_color, (win.get_width() // 2 - 192, win.get_height() // 2 - 80, 384, 96))
        win.blit(play, (win.get_width() // 2 - play.get_width() // 2,
                        win.get_height() // 2 - play.get_height() // 2 - 36))
        pygame.draw.rect(win, quit_color, (win.get_width() // 2 - 192, win.get_height() // 2 + 144, 384, 96))
        win.blit(esc, (win.get_width() // 2 - esc.get_width() // 2,
                       win.get_height() // 2 - esc.get_height() // 2 + 192))
        pygame.display.flip()
    elif in_game:
        music_intro.play()
        while not done:
            seconds += clock.tick(60) / 1000
            if not pygame.mixer.get_busy():
                music_loop.play(-1)
            if seconds >= 60:
                seconds -= 60
                minutes += 1
            seconds_str, ms_str = str(float(round(seconds, 3))).split(".")
            if len(seconds_str) != 2:
                new_seconds_str = f"0{seconds_str}"
            else:
                new_seconds_str = seconds_str
            if len(ms_str) == 2:
                new_ms_str = f"{ms_str}0"
            elif len(ms_str) == 1:
                new_ms_str = f"{ms_str}00"
            elif len(ms_str) == 0:
                new_ms_str = f"{ms_str}000"
            else:
                new_ms_str = ms_str
            for entity in entity_list:
                if entity.filename == "Reflection":
                    if entity.active:
                        reflection_active = True
                    for tile in tilemap.checkTilemapCollision(entity.x, entity.y):
                        if "Death" in tile.flags:
                            alive = False
                            fall.play()
                            entity.x = -100
                            entity.y = -100
                        if "Button" in tile.flags and entity.active:
                            num_pressed += 1
                if entity.filename == "Player":
                    mirror_check = entity.checkForWallMirrors(tilemap)
                    for tile in tilemap.checkTilemapCollision(entity.x, entity.y):
                        if "Mirror" in tile.flags:
                            for other in entity_list:
                                if other.filename == "Reflection":
                                    other.facing = entity.facing
                                    if not other.active and not box_blocked:
                                        awaken.play()
                                    other.active = True
                                    other.flip = "None"
                                    reflection_active = True
                        elif mirror_check is not None:
                            for other in entity_list:
                                if other.filename == "Box":
                                    box_block_check = other.checkForWallMirrors(tilemap)
                                    if mirror_check == "West" and box_block_check == "West":
                                        if entity.x > other.x and entity.y == other.y:
                                            box_block_count += 1
                                            for third in entity_list:
                                                if third.filename == "Reflection":
                                                    third.flip = "None"
                                                    if third.active:
                                                        sleep.play()
                                                    third.active = False
                                                    reflection_active = False
                                    elif mirror_check == "East" and box_block_check == "East":
                                        if entity.x < other.x and entity.y == other.y:
                                            box_block_count += 1
                                            for third in entity_list:
                                                if third.filename == "Reflection":
                                                    third.flip = "None"
                                                    if third.active:
                                                        sleep.play()
                                                    third.active = False
                                                    reflection_active = False
                                    elif mirror_check == "North" and box_block_check == "North":
                                        if entity.y > other.y and entity.x == other.x:
                                            box_block_count += 1
                                            for third in entity_list:
                                                if third.filename == "Reflection":
                                                    third.flip = "None"
                                                    if third.active:
                                                        sleep.play()
                                                    third.active = False
                                                    reflection_active = False
                                    elif mirror_check == "South" and box_block_check == "South":
                                        if entity.y < other.y and entity.x == other.x:
                                            box_block_count += 1
                                            for third in entity_list:
                                                if third.filename == "Reflection":
                                                    third.flip = "None"
                                                    if third.active:
                                                        sleep.play()
                                                    third.active = False
                                                    reflection_active = False
                                elif other.filename == "Reflection":
                                    if not box_blocked:
                                        if mirror_check == "West" or mirror_check == "East":
                                            other.flip = "Horizontal"
                                            if entity.facing == "South" or entity.facing == "North":
                                                other.facing = entity.facing
                                            elif entity.facing == "East":
                                                other.facing = "West"
                                            elif entity.facing == "West":
                                                other.facing = "East"
                                        elif mirror_check == "North" or mirror_check == "South":
                                            other.flip = "Vertical"
                                            if entity.facing == "East" or entity.facing == "West":
                                                other.facing = entity.facing
                                            elif entity.facing == "North":
                                                other.facing = "South"
                                            elif entity.facing == "South":
                                                other.facing = "North"
                                        if not other.active and box_block_count == 0:
                                            awaken.play()
                                        other.active = True
                                        reflection_active = True
                        else:
                            for other in entity_list:
                                if other.filename == "Reflection":
                                    other.facing = entity.facing
                                    other.flip = "None"
                                    if other.active:
                                        sleep.play()
                                    other.active = False
                                    reflection_active = False
                        if "Button" in tile.flags:
                            num_pressed += 1
                        if "Death" in tile.flags:
                            alive = False
                            fall.play()
                            entity.x = -100
                            entity.y = -100
                if entity.filename == "Box":
                    for tile in tilemap.checkTilemapCollision(entity.x, entity.y):
                        if "Button" in tile.flags:
                            num_pressed += 1
                        if "Death" in tile.flags:
                            fall.play()
                            entity.x = -100
                            entity.y = -100
            if box_block_count >= 1:
                box_blocked = True
            else:
                box_blocked = False
            event = pygame.event.poll()
            keys = pygame.key.get_pressed()
            i = 1
            if keys[pygame.K_ESCAPE] or event.type == pygame.QUIT:
                playing = False
                break
            if not win_state:
                if event.type == pygame.KEYDOWN:
                    for entity in entity_list:
                        if entity.filename == "Player":
                            if alive:
                                if event.key == pygame.K_w or event.key == pygame.K_UP:
                                    entity.move(0, -32)
                                    for other in entity_list:
                                        if other.filename == "Reflection":
                                            if not other.active:
                                                other.wait()
                                if event.key == pygame.K_d or event.key == pygame.K_RIGHT:
                                    entity.move(32, 0)
                                    for other in entity_list:
                                        if other.filename == "Reflection":
                                            if not other.active:
                                                other.wait()
                                if event.key == pygame.K_s or event.key == pygame.K_DOWN:
                                    entity.move(0, 32)
                                    for other in entity_list:
                                        if other.filename == "Reflection":
                                            if not other.active:
                                                other.wait()
                                if event.key == pygame.K_a or event.key == pygame.K_LEFT:
                                    entity.move(-32, 0)
                                    for other in entity_list:
                                        if other.filename == "Reflection":
                                            if not other.active:
                                                other.wait()
                                if event.key == pygame.K_SPACE:
                                    entity.wait()
                            if event.key == pygame.K_z:
                                alive = True
                                for every_entity in entity_list:
                                    every_entity.undo()
                            if event.key == pygame.K_r:
                                alive = True
                                for every_entity in entity_list:
                                    every_entity.restart()
                            if event.key == pygame.K_h:
                                if display_hint:
                                    display_hint = False
                                else:
                                    display_hint = True
                        elif entity.filename == "Box":
                            wait_flag = 0
                            for other in entity_list:
                                if other.filename == "Player":
                                    if alive:
                                        if event.key == pygame.K_w or event.key == pygame.K_UP:
                                            if other.x == entity.x and other.y == entity.y:
                                                entity.move(0, -32)
                                                push.play()
                                            else:
                                                wait_flag += 1
                                        if event.key == pygame.K_d or event.key == pygame.K_RIGHT:
                                            if other.x == entity.x and other.y == entity.y:
                                                entity.move(32, 0)
                                                push.play()
                                            else:
                                                wait_flag += 1
                                        if event.key == pygame.K_s or event.key == pygame.K_DOWN:
                                            if other.x == entity.x and other.y == entity.y:
                                                entity.move(0, 32)
                                                push.play()
                                            else:
                                                wait_flag += 1
                                        if event.key == pygame.K_a or event.key == pygame.K_LEFT:
                                            if other.x == entity.x and other.y == entity.y:
                                                entity.move(-32, 0)
                                                push.play()
                                            else:
                                                wait_flag += 1
                                    for tile in tilemap.checkTilemapCollision(entity.x, entity.y):
                                        if "Wall" in tile.flags:
                                            other.undo()
                            if event.key == pygame.K_SPACE or wait_flag > 0:
                                wait_flag = 0
                                entity.wait()
                        for tile in tilemap.checkTilemapCollision(entity.x, entity.y):
                            if reflection_active:
                                for other in entity_list:
                                    if other.filename == "Reflection":
                                        if entity.filename == "Player":
                                            if alive:
                                                if event.key == pygame.K_w or event.key == pygame.K_UP:
                                                    if other.flip == "Vertical":
                                                        other.move(0, 32)
                                                    else:
                                                        other.move(0, -32)
                                                if event.key == pygame.K_d or event.key == pygame.K_RIGHT:
                                                    if other.flip == "Horizontal":
                                                        other.move(-32, 0)
                                                    else:
                                                        other.move(32, 0)
                                                if event.key == pygame.K_s or event.key == pygame.K_DOWN:
                                                    if other.flip == "Vertical":
                                                        other.move(0, -32)
                                                    else:
                                                        other.move(0, 32)
                                                if event.key == pygame.K_a or event.key == pygame.K_LEFT:
                                                    if other.flip == "Horizontal":
                                                        other.move(32, 0)
                                                    else:
                                                        other.move(-32, 0)
                                            if event.key == pygame.K_SPACE:
                                                other.wait()
                            else:
                                if entity.filename == "Reflection":
                                    entity.active = False
                            for other in entity_list:
                                if entity.filename == "Player" and other.filename == "Reflection":
                                    for other_tile in tilemap.checkTilemapCollision(other.x, other.y):
                                        if "Wall" not in tile.flags and "Wall" in other_tile.flags:
                                            other.undo()
                                            other.wait()
                                        elif "Wall" in tile.flags:
                                            other.undo()
                            if "Wall" in tile.flags:
                                for other in entity_list:
                                    if entity.filename == "Player" and other.filename == "Box":
                                        other.undo()
                                entity.undo()
                            if "Win" in tile.flags:
                                win_count += 1
            if num_pressed >= 1:
                if not button_pressed:
                    tilemap.buttonPress()
                    press.play()
                    button_pressed = True
            else:
                if button_pressed:
                    tilemap.buttonPress()
                    unpress.play()
                    button_pressed = False
            win.fill((34, 32, 52))
            level_title = font.render(f"Level {levels[level_number]} - {level_names[level_number]}", False,
                                      (255, 255, 255))
            timer_base = font.render("Time elapsed: 0:00.000", False, (255, 255, 255)).get_width()
            timer = font.render(f"Time elapsed: {minutes}:{new_seconds_str}.{new_ms_str}", False, (255, 255, 255))
            win.blit(level_title, (20, 20))
            win.blit(timer, (win.get_width() - timer_base - 20, 20))
            tilemap.renderTilemap()
            spawn_entities = False
            if display_hint:
                tilemap.typeDisplay()
            for entity in entity_list:
                entity.render()
            if win_count == tilemap.checkWinCondition():
                finish.play()
                wait_time -= 1
                win_state = True
                if wait_time <= 0:
                    win_count = 0
                    level_number += 1
                    win.fill((34, 32, 52))
                    wait_time = 120
                    win_state = False
                    entity_list = []
                    button_pressed = False
                    spawn_entities = True
                    if level_number < len(levels):
                        tilemap = Tilemap("levels.txt", win, levels[level_number])
                    else:
                        done = True
                        in_game = False
            else:
                win_count = 0
            reflection_active = False
            num_pressed = 0
            box_block_count = 0
            pygame.display.flip()
    else:
        playing = False

pygame.quit()
