import pygame
from time import sleep
import sys
import pyperclip

pygame.init()
pygame.display.set_caption("my title")

map = pygame.image.load("static/img/overlay.jpg")#sys.argv[1])

screen = pygame.display.set_mode((640,480))

color = (255, 255, 255)

i = 0
running = True
while running:
	screen.fill(color)
	#pygame.draw.rect(screen, (255, 0, 0), pygame.Rect(i, i, 40, 30))

	screen.blit(map, (0, 0))

	i += 1

	for event in pygame.event.get():
		if event.type == pygame.QUIT:
			running = False
		elif event.type == pygame.MOUSEBUTTONDOWN:
			pos = pygame.mouse.get_pos()
			clip = str(list(pos))
			print(clip)
			pyperclip.copy(clip)

	pygame.display.flip()
	sleep(0.05)
