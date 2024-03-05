import pygame

font_type1 = 'Arial'
font_type2 = None
COLOR_INACTIVE = pygame.Color('lightskyblue3')
COLOR_ACTIVE = pygame.Color('dodgerblue2')

# Button Class
class NormalButton():
    def __init__(self, x, y, width, height, font_size, buttonText='Button', onclickFunction=None, onePress=False):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.font_size = font_size
        self.onclickFunction = onclickFunction
        self.onePress = onePress
        self.buttonText = buttonText

        self.fillColors = {
            'normal': '#ffffff',
            'hover': '#666666',
            'pressed': '#333333',
        }

        self.buttonSurface = pygame.Surface((self.width, self.height))
        self.buttonRect = pygame.Rect(self.x, self.y, self.width, self.height)

        font = pygame.font.SysFont(font_type1, font_size)
        self.buttonSurf = font.render(buttonText, True, (20, 20, 20))

        self.alreadyPressed = False

    def process(self):

        mousePos = pygame.mouse.get_pos()

        self.buttonSurface.fill(self.fillColors['normal'])
        
        if self.buttonRect.collidepoint(mousePos):
            self.buttonSurface.fill(self.fillColors['hover'])

            if pygame.mouse.get_pressed(num_buttons=3)[0]:
                self.buttonSurface.fill(self.fillColors['pressed'])

                if self.onePress:
                    self.onclickFunction()

                elif not self.alreadyPressed:
                    self.onclickFunction()
                    self.alreadyPressed = True

            else:
                self.alreadyPressed = False

        self.buttonSurface.blit(self.buttonSurf, [
            self.buttonRect.width/2 - self.buttonSurf.get_rect().width/2,
            self.buttonRect.height/2 - self.buttonSurf.get_rect().height/2
        ])


# Grouped Button Class
class GroupedButton():
    def __init__(self, x, y, width, height, font_size, buttonText='Button', onclickFunction=None, name2=None, pressedColor='#cb140b', onePress=False):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.font_size = font_size
        self.onclickFunction = onclickFunction
        self.onePress = onePress
        self.name = buttonText
        self.name2 = name2

        self.fillColors = {
            'normal': '#ffffff',
            'hover': '#666666',
            'pressed': pressedColor,
        }

        self.buttonSurface = pygame.Surface((self.width, self.height))
        self.buttonRect = pygame.Rect(self.x, self.y, self.width, self.height)

        font = pygame.font.SysFont(font_type1, font_size)
        self.buttonSurf = font.render(buttonText, True, (20, 20, 20))

        self.alreadyPressed = False

    def process(self, ):

        mousePos = pygame.mouse.get_pos()

        if(self.alreadyPressed):
            self.buttonSurface.fill(self.fillColors['pressed'])
        else:
            self.buttonSurface.fill(self.fillColors['normal'])

        if self.buttonRect.collidepoint(mousePos):
            self.buttonSurface.fill(self.fillColors['hover'])

            if pygame.mouse.get_pressed(num_buttons=3)[0]:
                self.buttonSurface.fill(self.fillColors['pressed'])

                if self.onePress:
                    self.onclickFunction()

                elif not self.alreadyPressed:
                    self.onclickFunction()
                    
        self.buttonSurface.blit(self.buttonSurf, [
            self.buttonRect.width/2 - self.buttonSurf.get_rect().width/2,
            self.buttonRect.height/2 - self.buttonSurf.get_rect().height/2
        ])

# Toggle Button Class
class ToggleButton():
    def __init__(self, x, y, width, height, font_size, buttonText='Button', onclickFunction=None, pressed='#333333'):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.font_size = font_size
        self.buttonText = buttonText
        self.delay_timer = 1
        self.onclickFunction = onclickFunction

        self.fillColors = {
            'normal': '#ffffff',
            'hover': '#666666',
            'pressed': pressed,
        }

        self.buttonSurface = pygame.Surface((self.width, self.height))
        self.buttonRect = pygame.Rect(self.x, self.y, self.width, self.height)

        font = pygame.font.SysFont(font_type1, font_size)
        self.buttonSurf = font.render(buttonText, True, (20, 20, 20))

        self.alreadyPressed = False

    def process(self):

        mousePos = pygame.mouse.get_pos()

        if self.alreadyPressed:
            self.buttonSurface.fill(self.fillColors['pressed'])
        else:
            self.buttonSurface.fill(self.fillColors['normal'])
        
        if self.buttonRect.collidepoint(mousePos):
            #self.buttonSurface.fill(self.fillColors['hover'])

            if pygame.mouse.get_pressed(num_buttons=3)[0]:
                if self.delay_timer > 0:
                    if not self.alreadyPressed:
                        self.alreadyPressed = True
                        if self.onclickFunction != None:
                            self.onclickFunction()
                    else:
                        self.alreadyPressed = False
                    self.delay_timer = self.delay_timer - 1
                    
            else:
                self.delay_timer = 1

        self.buttonSurface.blit(self.buttonSurf, [
            self.buttonRect.width/2 - self.buttonSurf.get_rect().width/2,
            self.buttonRect.height/2 - self.buttonSurf.get_rect().height/2
        ])


class InputBox:

    def __init__(self, x, y, w, h, font_size, name, alwaysActive=False, text=''):
        self.rect = pygame.Rect(x, y, w, h)
        self.color = COLOR_INACTIVE
        self.text = text
        self.font = pygame.font.SysFont(font_type2, font_size)
        self.txt_surface = self.font.render(text, True, self.color)
        self.alwaysActive = alwaysActive
        if alwaysActive:
            self.active = True
        else:
            self.active = False
        self.name = name
        self.name_text = self.font.render(name + ':', False, (250, 250, 250))

    def handle_event(self, event, input_boxes):
        if event.type == pygame.MOUSEBUTTONDOWN and not self.alwaysActive:
            # If the user clicked on the input_box rect.
            if self.rect.collidepoint(event.pos):
                # Toggle the active variable.
                self.active = True
                for box in input_boxes:
                    if box.alwaysActive:
                        box.active = False
            else:
                self.active = False
                for box in input_boxes:
                    if box.alwaysActive:
                        box.active = True
            # Change the current color of the input box.
            self.color = COLOR_ACTIVE if self.active else COLOR_INACTIVE
        if event.type == pygame.KEYDOWN:
            if self.active:
                if event.key == pygame.K_RETURN:
                    print(self.text)
                    self.text = ''
                elif event.key == pygame.K_BACKSPACE:
                    self.text = self.text[:-1]
                else:
                    self.text += event.unicode
                # Re-render the text.
                self.txt_surface = self.font.render(self.text, True, self.color)
    
    def clearText(self):
        self.text = ""
        self.txt_surface = self.font.render(self.text, True, self.color)

    def draw(self, screen):
        # Blit the text.
        screen.blit(self.txt_surface, (self.rect.x+(self.txt_surface.get_height()/6), self.rect.y+(self.txt_surface.get_height()/10)))
        # Blit the rect.
        pygame.draw.rect(screen, self.color, self.rect, 2)
        # Blit the text box name
        screen.blit(self.name_text, (self.rect.x, self.rect.y-(self.txt_surface.get_height())))


class OptionBox():

    def __init__(self, x, y, w, h, option_list, font_size=30, font='Arial', color='#ffffff', highlight_color='#333333', selected=0):
        self.color = color
        self.highlight_color = highlight_color
        self.rect = pygame.Rect(x, y, w, h)
        self.font = pygame.font.SysFont(font, font_size)
        self.option_list = option_list
        self.selected = selected
        self.draw_menu = False
        self.menu_active = False
        self.active_option = -1
        self.menu_size = 6
        self.start_index = 0

    def draw(self, surf):
        pygame.draw.rect(surf, self.highlight_color if self.menu_active else self.color, self.rect)
        pygame.draw.rect(surf, (0, 0, 0), self.rect, 2)
        msg = self.font.render(self.option_list[self.selected], 1, (0, 0, 0))
        surf.blit(msg, msg.get_rect(center = self.rect.center))

        if self.draw_menu:
            i = 0
            for index in range(self.start_index, self.start_index + self.menu_size):
                if index < len(self.option_list):
                    text = self.option_list[index]
                else:
                    text = ""
                rect = self.rect.copy()
                rect.y += (i+1) * self.rect.height
                pygame.draw.rect(surf, self.highlight_color if index == self.active_option else self.color, rect)
                msg = self.font.render(text, 1, (0, 0, 0))
                surf.blit(msg, msg.get_rect(center = rect.center))
                i = i + 1
            outer_rect = (self.rect.x, self.rect.y + self.rect.height, self.rect.width, self.rect.height * self.menu_size)
            pygame.draw.rect(surf, (0, 0, 0), outer_rect, 2)

    def update(self, event_list):
        mpos = pygame.mouse.get_pos()
        self.menu_active = self.rect.collidepoint(mpos)
        
        self.active_option = -1
        i = 0
        for index in range(self.start_index, self.start_index + self.menu_size):
        #for i in range(len(self.option_list)):
            rect = self.rect.copy()
            rect.y += (i+1) * self.rect.height
            if rect.collidepoint(mpos):
                if index >= len(self.option_list):
                    index = len(self.option_list)-1
                self.active_option = index
                break
            i = i + 1

        if not self.menu_active and self.active_option == -1:
            self.draw_menu = False

        for event in event_list:
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if self.menu_active:
                    self.draw_menu = not self.draw_menu
                elif self.draw_menu and self.active_option >= 0:
                    self.selected = self.active_option
                    self.draw_menu = False
                    return self.active_option
            if event.type == pygame.MOUSEWHEEL and self.draw_menu:
                #if event.y < 0 and self.start_index < len(self.option_list)-self.menu_size:
                if event.y < 0 and self.start_index < len(self.option_list)-1:
                    self.start_index = self.start_index + 1
                    #self.draw_menu = True
                elif event.y > 0 and self.start_index > 0:
                    self.start_index = self.start_index - 1
                    #self.draw_menu = True



        return -1
