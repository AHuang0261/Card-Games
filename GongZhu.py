import pygame
from GongZhuEngine import *


class Button:
    def __init__(self,x, y, image, secondary_image,scale = 1, topleft = False):
        width = image.get_width()
        height = image.get_height()
        self.image = pygame.transform.scale(image, (int(width * scale),int(height*scale)))
        self.secondary_image = pygame.transform.scale(secondary_image, (int(width * scale),int(height*scale)))
        self.rect = self.image.get_rect()
        if topleft: self.rect.topleft = (x,y)
        else: self.rect.center = (x,y)
        self.first_click_flag = True
        self.first_click_pos = (-100, -100)
        self.action_lock = True #prevent holding button from clicking
    
    #Draw the button to suface, changes to secondary image when hovering, returns false unless button is clicked with mousebutton1(by default)
    def draw(self, surface, mb = 0):
        if self.action_lock and not pygame.mouse.get_pressed()[mb]:
            self.action_lock = False
        pos = pygame.mouse.get_pos()
        #If this is the initial click position, set the initial click position and lock
        if self.first_click_flag and pygame.mouse.get_pressed()[mb]:
            self.first_click_pos = pos
            self.first_click_flag = False
        #If mouse is released after there was a click, release lock and set some out of bounds positino
        if not self.first_click_flag and not pygame.mouse.get_pressed()[mb]:
            self.first_click_flag = True
            self.first_click_pos = (-100, -100)

        if self.rect.collidepoint(pos):
            surface.blit(self.secondary_image, (self.rect.x, self.rect.y))
            if self.rect.collidepoint(self.first_click_pos) and not self.action_lock:
                return True
        else:
            surface.blit(self.image, (self.rect.x, self.rect.y))
        
        return False

pygame.init()
bounds = (1024, 1024)
window = pygame.display.set_mode(bounds)
pygame.display.set_caption("Gong Zhu")

engine = GongZhuEngine()

""" Dimensions
Cardback dims: (960, 720) It looks like the transparent space is still being included in the pixel measurements, either get a new 
image or use the middle with rectangle control points
Normal card: (500, 726)
scaled to 0.2: (100, 145)
# cardBack = pygame.transform.scale(cardBack, (int(238*0.8), int(332*0.8)))
# deck = Deck()
# deck.shuffle()
# card = Card(3, Suits(2))
# print(f"Cardback dims: {cardBack.get_size()}")
# print(f"Normal card: {deck.cards.pop().image.get_size()}")
"""

hand_cards = pygame.sprite.Group()
board_cards = pygame.sprite.Group()
collection_cards = pygame.sprite.Group()
# active_card = pygame.sprite.GroupSingle()

colors = {
    "background": (0,81,44),
    "button1": (33,33,33),
    "button2": (22,22,22),
    "text1": (255,215,0)
}

'''TODO
Finish Menu:  add images for instructions and credits, back to main menu at the end (maybe replace show collection) 
Add instructions and settings: Difficulty selector and delay between com turns and tricks
Implement AI
Strange visibility bug where when the next round starts, during the bidding phase, player 4s cards(player that got pig) were visible but hidden once play started they were hidden
Game loop requires some sort of event in order to run another iteration, I would prefer if it took in events but advanced with a tick system or smth.
For some reason the score and collection buttons are not working when there is an ai player. I think it might be how many things the system can do at once
'''

#Menu Buttons
button_dir = 'Images/Buttons/'
x_middle =bounds[0] / 2
y_middle = bounds[1] / 2
single_player_button = Button(x_middle, y_middle + 50, pygame.image.load(button_dir + 'Single_Player1.png'), pygame.image.load(button_dir + 'Single_Player2.png'))
multiplayer_button = Button(x_middle, y_middle + 150, pygame.image.load(button_dir + 'Multiplayer1.png'), pygame.image.load(button_dir + 'Multiplayer2.png'))
instructions_button = Button(x_middle, y_middle + 250, pygame.image.load(button_dir + 'Instructions1.png'), pygame.image.load(button_dir + 'Instructions2.png'))
credits_button = Button(x_middle, y_middle + 350, pygame.image.load(button_dir + 'Credits1.png'), pygame.image.load(button_dir + 'Credits2.png'))
settings_button = Button(25, bounds[1] - 50, pygame.image.load(button_dir + 'Settings_Gear.png'), pygame.image.load(button_dir + 'Settings_Gear.png'), scale=0.1)
#Game Buttons
bidding_end_button = Button(bounds[0]/2, bounds[1]/2, pygame.image.load(button_dir+'End_Bidding1.png'), pygame.image.load(button_dir+'End_Bidding2.png'))
show_collection_button = Button(10, 10, pygame.image.load(button_dir + 'Show_Collection1.png'), pygame.image.load(button_dir + 'Show_Collection2.png'), topleft=True)
show_score_button = Button(bounds[0] - 130,10, pygame.image.load(button_dir + 'Show_Score1.png'), pygame.image.load(button_dir + 'Show_Score2.png'), topleft=True)
next_round_button = Button(x_middle, y_middle + 80, pygame.image.load(button_dir + 'Next_Round1.png'), pygame.image.load(button_dir + 'Next_Round2.png'))

turn_indicator = Image('Images/Arrow.png')
increment =  50

def render_main_menu(window):
    window.blit(pygame.image.load("Images/GongZhu_Main_Menu.png"), (0,0))
    if single_player_button.draw(window):
        engine.state = GameState.STARTING
    if multiplayer_button.draw(window):
        print("multi")
        pass
        # print("Work in progress, please choose another option")
    if instructions_button.draw(window):
        print("instructions")
        pass
    if credits_button.draw(window):
        print("Created by Alexander Huang\n Image Attributions:")
        pass
    if settings_button.draw(window):
        print("Settings")
        pass

def render_round_start(window):
    window.fill((0,81,44))
    offset = 0
    for card in engine.players[0].hand:
        hand_cards.add(card)
        card.rect = card.image.get_rect(bottomleft = (160 + offset, bounds[1] - 15))
        offset += increment
    
    offset = 0
    for card in engine.players[1].hand:
        card.set_orientation(90)
        card.rect = card.image.get_rect(topleft = (15, offset + 160))
        hand_cards.add(card)
        offset += increment

    offset = 0
    for card in engine.players[2].hand:
        hand_cards.add(card)
        card.rect.move_ip(160 + offset, 15)
        offset += increment

    offset = 0
    for card in engine.players[3].hand:
        card.set_orientation(-90)
        card.rect = card.image.get_rect(topright = (bounds[0] - 15, offset + 160))
        hand_cards.add(card)
        offset += increment
        
    hand_cards.draw(window)

def render_bidding(window):
    font = pygame.font.Font('Baskervville-Regular.ttf', 20)
    text = font.render("Select cards to sell or click End", True, colors.get("text1"))
    window.blit(text, (400,400))
    
    render_sell_info(window)
    if bidding_end_button.draw(window):
        engine.state = GameState.PLAYING
        render_playing(window)
    
def render_sell_info(window):
    font = pygame.font.Font('Baskervville-Regular.ttf', 20)
    # spades_text = font.render(f"Spades: {engine.sells[3]}", True, "white")
    # hearts_text = font.render(f"Hearts: {engine.sells[2]}", True, "white")
    # diamonds_text = font.render(f"Diamonds: {engine.sells[1]}", True, "white")
    # clubs_text = font.render(f"Clubs: {engine.sells[0]}", True, "white")
    suit_names = [None, None, None, None]
    suit_rects = [None, None, None, None]
    for i in range(4):
        if engine.sells[i]: suit_names[i] = font.render(f"{Suits(i).name}S | SOLD", True, colors.get("text1"))
        else: suit_names[i] = font.render(f"{Suits(i).name}S", True, colors.get("text1"))
    for i in range(4):
        if engine.sells[i] and engine.suit_played[i]:
            suit_names[i] = font.render(f"{Suits(i).name}S | SOLD | PLAYED", True, colors.get("text1"))
        if not engine.sells[i] and engine.state == GameState.PLAYING: 
            suit_names[i] = font.render(f"{Suits(i).name}S | UNSOLD", True, colors.get("text1"))
    for i in range(4): suit_rects[i] = suit_names[i].get_rect()  
    suit_rects[0].topleft = (200,600)
    for i in range(1,4):
        suit_rects[i].topleft = (suit_rects[i-1].bottomleft[0], suit_rects[i-1].bottomleft[1])
    for i in range(4):
        window.blit(suit_names[i], suit_rects[i])
    pygame.display.update()

def render_playing(window):
    window.fill((0,81,44))
    hand_cards.draw(window)
    board_cards.draw(window)

    font = pygame.font.Font('Baskervville-Regular.ttf', 18)
    #Show collection Button
    if(show_collection_button.draw(window)):
        render_collection(window)
        if engine.developer_mode:
            engine.state = GameState.SCORING

    flag = False
    #Show Score Button
    if(show_score_button.draw(window)):
        render_scoring(window,False)
        flag = True
        

    #Turn indicator
    if not flag:
        turn_indicator.set_orientation(engine.current_player * -90 + 180)
        turn_indicator_rect = turn_indicator.image.get_rect()
        turn_indicator_rect.center = (bounds[0]/2, bounds[1]/2)
        window.blit(turn_indicator.image, turn_indicator_rect)
        render_sell_info(window)

def render_collection(window, selected = True):
    if selected: window.fill((0,84,44))    
    increment = 60
    buffer = 150
    for i in range(4):
        offset = 0
        for card in engine.players[i].collection:
            if i == 0: 
                card.rect.update((bounds[0] - buffer - offset, bounds[1] - buffer), (card.rect.width, card.rect.height))
                card.set_orientation(0)
            elif i == 1: 
                card.rect.update((buffer, bounds[1] - buffer - offset), (card.rect.width, card.rect.height))
                card.set_orientation(90)
            elif i == 2: 
                card.rect.update((buffer + offset, 15), (card.rect.width, card.rect.height))
                card.set_orientation(0)
            else: 
                card.rect.update((bounds[0] - buffer, 15 + offset), (card.rect.width, card.rect.height))
                card.set_orientation(-90)
            offset += increment
    collection_cards.draw(window)
    pygame.display.update()

def shift_cards(card):
    flag = False
    
    for c in engine.players[engine.current_player].hand:
        if flag:
            if engine.current_player == 0: c.rect.move_ip(-1 * increment, 0)
            if engine.current_player == 1: c.rect.move_ip(0, -1 * increment)
            if engine.current_player == 2: c.rect.move_ip(-1 * increment, 0)
            if engine.current_player == 3: c.rect.move_ip(0, -1 * increment)
        if c == card: flag = True

def move_to_board(card):
    if engine.current_player == 0: card.rect.update((462, 640), (card.rect.width, card.rect.height))
    if engine.current_player == 1: card.rect.update((240, 462), (card.rect.width, card.rect.height))
    if engine.current_player == 2: card.rect.update((462, 240), (card.rect.width, card.rect.height))
    if engine.current_player == 3: card.rect.update((640, 462), (card.rect.width, card.rect.height))
    card.switch_visibility(True)
    hand_cards.remove(card)
    board_cards.add(card)

def render_scoring(window, normal = True):
    window.fill((0,81,44))
    color = colors.get("text1")
    gap = 10
    font = pygame.font.Font('Baskervville-Regular.ttf', 20)
    center = (bounds[0]/2, bounds[1]/2)

    render_collection(window, False)

    player_text = [font.render(f"Player {x + 1}", True, color) for x in range(4)]
    player_rect = [t.get_rect() for t in player_text]
    score_text = [font.render(f"{p.score}", True, color) for p in engine.players]
    score_rect = [t.get_rect() for t in score_text]
    
    player_rect[1].bottomright = (center[0] - gap, center[1] - gap)
    score_rect[1].midtop = (player_rect[1].midbottom[0], player_rect[1].midbottom[1] + gap)
    #Setting positions
    for i in range(4):
        if i == 1: continue
        if i == 0:
            player_rect[i].bottomright = (player_rect[1].bottomleft[0] - gap, player_rect[1].bottomleft[1])
            
        else:
            player_rect[i].bottomleft = (player_rect[i-1].bottomright[0] + gap, player_rect[i-1].bottomright[1])
        
        score_rect[i].midtop = (player_rect[i].midbottom[0], player_rect[i].midbottom[1] + gap)
    #blitting
    for i in range(4):
        window.blit(player_text[i], player_rect[i])
        window.blit(score_text[i], score_rect[i])

    if normal:
        if next_round_button.draw(window):
            engine.state = GameState.STARTING
    
    return (player_rect[1].bottomright[0], player_rect[1].bottomright[1] + 5 * gap)

def render_game_over(window):
    window.fill((0,81,44))
    bottom_coords = render_scoring(window, False)
    font = pygame.font.Font('Baskervville-Regular.ttf', 36)
    font2 = pygame.font.Font('Baskervville-Regular.ttf', 20)
    text = font.render(f"The loser is {engine.loser.name}", True, colors.get("text1"))
    text_rect= text.get_rect()
    text_rect.midtop = bottom_coords
    window.blit(text, text_rect)

    exit_button = pygame.Rect(0,0, 200, 40)
    exit_button.midtop = (text_rect.center[0], text_rect.center[1] + 50)

    if exit_button.collidepoint(pygame.mouse.get_pos()):
        pygame.draw.rect(window, colors.get("button2"), exit_button)
        if pygame.mouse.get_pressed()[0]:
            pygame.QUIT()
    else:
        pygame.draw.rect(window, colors.get("button1"), exit_button)
    ex = font2.render("Exit", True, (0,0,0))
    ex_rect = ex.get_rect()
    ex_rect.center = exit_button.center
    window.blit(ex, ex_rect)

#!Come to think of it, this is not how the visibility will actually work. It will be false for the other players until they play the card.
def set_visibility():
    if engine.developer_mode: return
    if engine.com_mode == ComMode.MULTIPLAYER: return
    else:
        for i in range(4):
            for card in engine.players[i].hand: card.switch_visibility(i == 0) 
    
    # for card in hand_cards:
    #     if card in engine.players[engine.current_player].hand: card.switch_visibility(True)
    #     else: card.switch_visibility(False)

run = True
while run:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
        # print(engine.state)
        if engine.state == GameState.MAINMENU:
            render_main_menu(window)

        if engine.state == GameState.STARTING:
            for card in collection_cards: card.kill()
            engine.deal_new_round()
            render_round_start(window)
            set_visibility()

        
        if engine.state == GameState.BIDDING:
            render_bidding(window)
            selected = GZCard.selected[0]
            if selected != None:
                engine.sell_card(selected)
                selected.switch_visibility(True, True)
            GZCard.selected[0] = None
        
        if engine.state == GameState.PLAYING:
            if engine.is_leader: render_playing(window)
            active_player = engine.players[engine.current_player]
            delay = engine.com_select_card()
            selected = GZCard.selected[0]
            if selected != None and selected in active_player.hand and engine.check_card(selected):
                shift_cards(selected) #need to run this before any changes to hands
                move_to_board(selected)
                render_playing(window)
                engine.play_card(selected)
                pygame.time.wait(delay)
                if engine.board_size == 4:                    
                    # board_cards.draw(window)
                    pygame.display.update()
                    pygame.time.wait(500)
                    for c in engine.board:     
                        board_cards.remove(c) 
                        if(c.scoreable): collection_cards.add(c)
                    engine.collect()                
            GZCard.selected[0] = None
        
        if all(len(p.hand) == 0 for p in engine.players) and engine.state == GameState.PLAYING:
            engine.current_player = engine.find_pig()
            engine.state = GameState.SCORING
        
        if engine.state == GameState.SCORING:
            engine.score_game()

        
        if engine.state == GameState.WAITING:
            render_scoring(window)
            engine.played_cards = []
            #need to reset hands after this otherwise it will keep adding the round score
        
        engine.check_loser()

        if engine.state == GameState.ENDED:
            render_game_over(window)
            #!Add a play again button

        pygame.display.update()
        hand_cards.update()