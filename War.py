import pygame
from Cards import *
from WarEngine import *

pygame.init()
bounds = (1024, 768)
window = pygame.display.set_mode(bounds)
pygame.display.set_caption("WarPy")

cardBack =pygame.image.load('Images/back_of_card.png')
cardBack = pygame.transform.scale(cardBack, (int(238*0.8), int(332*0.8)))
engine = WarEngine()

displacement = 50

def renderGame(window):
    window.fill((0,81,44))
    font = pygame.font.SysFont('arial', 60, True)
    window.blit(cardBack, (100, 200))
    window.blit(cardBack, (700, 200))
    text = font.render(str(len(engine.p1.hand)) + " cards", True, (0,0,0))
    window.blit(text, (100, 500))
    text = font.render(str(len(engine.p2.hand)) + " cards", True, (0,0,0))
    window.blit(text, (700, 500))

    if engine.game_state == GameState.PLAYING:
        text = font.render(engine.current_player.name + "'s turn", True, (0,0,0))
        window.blit(text,(400,200))
        i = 0
        for card in engine.p1_board:
            window.blit(card.image, (200 + displacement  * i , 200))
            i +=1
        i = 0
        for card in engine.p2_board:
            window.blit(card.image, (700 - displacement  * i , 200))
    
    if engine.game_state == GameState.ENDED:
        text = font.render("The winner is: " + str(engine.winner.name), True, (0,0,0))
        window.blit(text, (20,50))

run = True
while run:
    key = None
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
        if event.type == pygame.KEYDOWN:
            key = event.key
            engine.play(key)
            renderGame(window)
            engine.give_cards()
            pygame.display.update()
    
