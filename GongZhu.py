import pygame
from GongZhuEngine import *

pygame.init()
bounds = (1024, 1024)
window = pygame.display.set_mode(bounds)
pygame.display.set_caption("Gong Zhu")

# cardBack = pygame.transform.scale(cardBack, (int(238*0.8), int(332*0.8)))
engine = GongZhuEngine()
engine.developer_mode = True
# deck = Deck()
# deck.shuffle()
# card = Card(3, Suits(2))
# print(f"Cardback dims: {cardBack.get_size()}")
# print(f"Normal card: {deck.cards.pop().image.get_size()}")

#!Make a button in the bottom right to show collection and put an arrow in the center to indicate current player

"""
Cardback dims: (960, 720) It looks like the transparent space is still being included in the pixel measurements, either get a new 
image or use the middle with rectangle control points
Normal card: (500, 726)
scaled to 0.2: (100, 145)
"""


hand_cards = pygame.sprite.Group()
board_cards = pygame.sprite.Group()
collection_cards = pygame.sprite.Group()
# active_card = pygame.sprite.GroupSingle()
bidding_end_button_rect = pygame.Rect(0, 0 , 200, 60)
bidding_end_button_rect.center = (bounds[0]/2, bounds[1]/2)
show_collection_button_rect = pygame.Rect(10, 10, 120, 60)
show_score_button_rect = pygame.Rect(0, 0 , 120, 60)
show_score_button_rect.topright = (bounds[0] - 10, 10)
show_game_button_rect = pygame.Rect(10, 10, 120, 60)
next_round_rect = pygame.Rect(0,0, 300, 100)
turn_indicator = Image('Images/Arrow.png')
increment =  50
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
    font = pygame.font.SysFont('arial', 20, True)
    text = font.render("Select cards to sell or click End", True, (0,0,0))
    window.blit(text, (400,400))
    if bidding_end_button_rect.collidepoint(pygame.mouse.get_pos()):
        pygame.draw.rect(window, "gray", bidding_end_button_rect)
        if pygame.mouse.get_pressed()[0]:
            engine.state = GameState.PLAYING
            print(engine.sells)    
    else:
        pygame.draw.rect(window, "white", bidding_end_button_rect)
    text = font.render("End", True, (0,0,0))
    text_rect = text.get_rect()
    text_rect.center = bidding_end_button_rect.center
    window.blit(text, text_rect)
    render_sell_info(window)
    
def render_sell_info(window):
    font = pygame.font.SysFont('arial', 20, True)
    # spades_text = font.render(f"Spades: {engine.sells[3]}", True, "white")
    # hearts_text = font.render(f"Hearts: {engine.sells[2]}", True, "white")
    # diamonds_text = font.render(f"Diamonds: {engine.sells[1]}", True, "white")
    # clubs_text = font.render(f"Clubs: {engine.sells[0]}", True, "white")
    suit_names = [None, None, None, None]
    suit_rects = [None, None, None, None]
    for i in range(4):
        if engine.sells[i]: suit_names[i] = font.render(f"{Suits(i).name}S | SOLD", True, "white")
        else: suit_names[i] = font.render(f"{Suits(i).name}S", True, "gray")
    for i in range(4):
        if engine.sells[i] and engine.suit_played[i]:
            suit_names[i] = font.render(f"{Suits(i).name}S | SOLD | PLAYED", True, "white")
        if not engine.sells[i] and engine.state == GameState.PLAYING: 
            suit_names[i] = font.render(f"{Suits(i).name}S | UNSOLD", True, "gray")
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

    font = pygame.font.SysFont('arial', 18, True)
    #Show collection Button
    if show_collection_button_rect.collidepoint(pygame.mouse.get_pos()):
        pygame.draw.rect(window, "gray", show_collection_button_rect)
        if pygame.mouse.get_pressed()[0]:
            render_collection(window)

    else:
        pygame.draw.rect(window, "white", show_collection_button_rect)
    text = font.render("See Collections", True, (0,0,0))
    window.blit(text, (show_collection_button_rect.topleft))

    flag = False
    #Show Score Button
    if show_score_button_rect.collidepoint(pygame.mouse.get_pos()):
        pygame.draw.rect(window, "gray", show_score_button_rect)
        if pygame.mouse.get_pressed()[0]:
            render_scoring(window, False)  
            flag = True
    else:
        pygame.draw.rect(window, "white", show_score_button_rect)
    text = font.render("See Scores", True, (0,0,0))
    window.blit(text, (show_score_button_rect.topleft))

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
    hand_cards.remove(card)
    board_cards.add(card)

def render_scoring(window, normal = True):
    window.fill((0,81,44))
    color = (255,255,255)
    gap = 10
    font = pygame.font.SysFont('arial', 20, True)
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
        button_text = font.render("Next Round", True, (0,0,0))
        button_text_rect = button_text.get_rect()
        next_round_rect.midtop = (player_rect[1].bottomright[0], player_rect[1].bottomright[1] + 3 * gap)
        button_text_rect.center = next_round_rect.center

        if next_round_rect.collidepoint(pygame.mouse.get_pos()):
            pygame.draw.rect(window, "gray", next_round_rect)
            if pygame.mouse.get_pressed()[0]:
                engine.state = GameState.STARTING
                
        else:
            pygame.draw.rect(window, "white", next_round_rect)
        
        window.blit(button_text, button_text_rect)
    
    return (player_rect[1].bottomright[0], player_rect[1].bottomright[1] + 5 * gap)

def render_game_over(window):
    window.fill((0,81,44))
    bottom_coords = render_scoring(window, False)
    font = pygame.font.SysFont('arial', 36, True)
    font2 = pygame.font.SysFont('arial', 20, True)
    text = font.render(f"The loser is {engine.loser.name}", True, "white")
    text_rect= text.get_rect()
    text_rect.midtop = bottom_coords
    window.blit(text, text_rect)

    exit_button = pygame.Rect(0,0, 200, 40)
    exit_button.midtop = (text_rect.center[0], text_rect.center[1] + 50)

    if exit_button.collidepoint(pygame.mouse.get_pos()):
        pygame.draw.rect(window, "gray", exit_button)
        if pygame.mouse.get_pressed()[0]:
            pygame.QUIT()
    else:
        pygame.draw.rect(window, "white", exit_button)
    ex = font2.render("Exit", True, (0,0,0))
    ex_rect = ex.get_rect()
    ex_rect.center = exit_button.center
    window.blit(ex, ex_rect)

#!Come to think of it, this is not how the visibility will actually work. It will be false for the other players until they play the card.
def set_visibility():
    for card in hand_cards:
        if card in engine.players[engine.current_player].hand: card.switch_visibility(True)
        else: card.switch_visibility(False)

run = True
while run:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False

        if engine.state == GameState.STARTING:
            for card in collection_cards: card.kill()
            engine.deal_new_round()
            render_round_start(window)
        
        if engine.state == GameState.BIDDING:
            render_bidding(window)
            selected = GZCard.selected[0]
            if selected != None:
                engine.sell_card(selected)
                selected.switch_visibility(True, True)
            GZCard.selected[0] = None
                #!Will eventually need to reveal this card if I make this a playable game
        
        if engine.state == GameState.PLAYING:
            render_playing(window)
            selected = GZCard.selected[0]
            active_player = engine.players[engine.current_player]
            if selected != None and selected in active_player.hand and engine.check_card(selected):
                shift_cards(selected) #need to run this before any changes to hands
                move_to_board(selected)
                engine.play_card(selected)
                set_visibility()
                if engine.board_size == 4:                    
                    board_cards.draw(window)
                    pygame.display.update()
                    pygame.time.wait(500)
                    for c in engine.board:     
                        board_cards.remove(c) 
                        if(c.scoreable): collection_cards.add(c)
                    engine.collect()                
                    set_visibility()
            GZCard.selected[0] = None
        
        if all(len(p.hand) == 0 for p in engine.players) and engine.state != GameState.WAITING:
            engine.current_player = engine.find_pig()
            engine.state = GameState.SCORING
        
        if engine.state == GameState.SCORING:
            engine.score_game()

        
        if engine.state == GameState.WAITING:
            render_scoring(window)
            #need to reset hands after this otherwise it will keep adding the round score
        
        engine.check_loser()

        if engine.state == GameState.ENDED:
            render_game_over(window)

        pygame.display.update()
        hand_cards.update()