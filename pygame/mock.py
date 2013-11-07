import time, os, sys, serial, eztext
import pygame
from pygame.locals import *

# change this flag to
use_serial=False
is_fullscreen=False

scene=[0]
catalog={}
inputLVL=-1
LVL=0

#########################################################################
# fade in an overlay
#########################################################################
def fade_in_overlay(step,name,folder,path,(x,y),scene=scene,catalog=catalog,fullscreen=False):
	alpha=step
	while alpha<=255:
		if alpha!=step:	
			remove_overlay(name,update=False)
		add_faded_overlay(alpha,name,folder,path,(x,y),scene,catalog,fullscreen)
		alpha+=step
	remove_overlay(name,update=False)
	add_overlay(name,folder,path,(x,y),scene,catalog,fullscreen)
	
	
##########################################################################
# fade out an overlay
##########################################################################

def fade_out_overlay(step,name,folder,path,(x,y),scene=scene,catalog=catalog,fullscreen=False):
	alpha=255-step
	
	while alpha>=step:
		remove_overlay(name,update=False)
		add_faded_overlay(alpha,name,folder,path,(x,y),scene,catalog,fullscreen)
		alpha-=step
	remove_overlay(name)


		
#######################################################################
# adds transparent overlay
###################################################################
def add_faded_overlay(alpha,name,folder,path,(x,y),scene=scene,catalog=catalog,fullscreen=False):
	overlay = pygame.image.load(os.path.join(folder,path))
	if fullscreen==True:
		overlay = pygame.transform.scale(overlay,screen.get_size())
	overlay.set_alpha(alpha)
	overlay=overlay.convert()
	# add overlay to scene list and catalog
	scene.append((overlay,x,y))
	catalog[name]=len(scene)-1
	#re draw the scene
	redraw_scene(scene)

#################################################################
# function to read input level from podium
################################################################
def get_inputLVL(s):
	char=ord(s.read())
	while 1:
		if (char==255):		
			char=ord(s.read())
			if (char==255):
				low=ord(s.read())
				high=ord(s.read())
				value= (low+256*high)/353
				low=ord(s.read())
				high=ord(s.read())
				if high==0:
					return value
		else:
			char=ord(s.read())


#############################################################
# function to redraw entire scene
#############################################################
def redraw_scene(scene=scene):
	for surface in scene:
		screen.blit(surface[0], surface[0].get_rect().move(surface[1],surface[2]))
	pygame.display.update()


##########################################################
# function to update background
##########################################################
def update_background(path,folder='backgrounds',scene=scene):
	#load image from path
	tmp_img = pygame.image.load(os.path.join(folder,path))	
	background = pygame.transform.scale(tmp_img,screen.get_size())
	#add surface to scene list and catalog
	scene[0]=(background,0,0)
	#re draw the scene
	redraw_scene(scene)


##########################################################
# function to fade in a new background
##########################################################
def fade_in_background(step,path,folder='backgrounds',scene=scene):
	fade_in_overlay(15,'tmp',folder,path,(0,0),scene=scene,catalog=catalog,fullscreen=True)
	remove_overlay('tmp',update=False)
	update_background(path,folder,scene=scene)

###########################################################
# function to add overlay to the scene
##############################################################
def add_overlay(name,folder,path,(x,y),scene=scene,catalog=catalog,fullscreen=False):
	overlay = pygame.image.load(os.path.join(folder,path))
	if fullscreen==True:
		overlay = pygame.transform.scale(overlay,screen.get_size())
	# add overlay to scene list and catalog
	scene.append((overlay,x,y))
	catalog[name]=len(scene)-1
	#re draw the scene
	redraw_scene(scene)


##########################################################
# removes overlay with a given name
#########################################################
def remove_overlay(name,scene=scene,catalog=catalog, update=True):
	#get index and remove from scene list
	index=catalog[name]
	scene.pop(index)
	#remove from catalog
	del catalog[name]
	#update indexes of new catalog
	for surface in catalog:
		if catalog[surface]>index:
			catalog[surface]=catalog[surface]-1
	#re draw the scene
	if update==True:
		redraw_scene(scene)

##################################################################
# function that draws a text input line, and returns inputed text
###################################################################
def input_box(x,y,maxlength,prompt):
	# make text box "surface thing"
	txtbx = eztext.Input(x=x,y=y,maxlength=maxlength, color=(0,0,0), prompt=prompt)
	# for the remainder of the time..
	while state=='EVENT1':
			#clear and redraw screen.
			screen.fill((0,0,0))
			redraw_scene()
			#check for keyboard events
			events = pygame.event.get()
			# exit if necessary
			for event in events:
				if event.type == KEYDOWN:
					if pygame.key.get_pressed()[K_ESCAPE]:
						pygame.quit()
						sys.exit()
					
					elif pygame.key.get_pressed()[K_RETURN]: 
						return txtbx.value
			# update text box
			txtbx.update(events)
			txtbx.draw(screen)
			pygame.display.update()


##########################################################################
# get Multiple Choice input
#####################################################################
def get_MC_input():

	while 1:
		for event in pygame.event.get():
			
			if event.type == QUIT:
				pygame.quit()
				sys.exit()
			
			elif event.type == KEYDOWN:
				if pygame.key.get_pressed()[K_a]:
					return 'a'
				elif pygame.key.get_pressed()[K_b]:
					return 'b'
				elif pygame.key.get_pressed()[K_b]:
					return 'c'
				elif pygame.key.get_pressed()[K_b]:
					return 'd'



# initialize serial port if need
if use_serial==True:	
	s=serial.Serial('/dev/ttyUSB0',115200)	

# initialise the display window
screen = pygame.display.set_mode([0,0])
pygame.init()

#make full screen if needed
if is_fullscreen==True:
	pygame.display.toggle_fullscreen()

#draw background
update_background('start.png')

# create the pygame clock
clock = pygame.time.Clock()

#define strating state
state='GET VALUE'
event=1

while 1:
	
	# make sure the program is runnign at 30 fps
	clock.tick(30)
	
	for event in pygame.event.get():
		#print "here"
		if event.type == QUIT:
			pygame.quit()
			sys.exit()
		
		elif event.type == KEYDOWN:
			if pygame.key.get_pressed()[K_RETURN]:
				if state=='INTRO':
					state='EVENT1'
				else:
					state='EVENT'+str(event)
			
			elif pygame.key.get_pressed()[K_ESCAPE]:
				pygame.quit()
				sys.exit()
	
	if state=='GET VALUE':
		# perpetual loop that waits to get input lvl from podium
		if use_serial==True:
			inputLVL=get_inputLVL(s)
		else:
			inputLVL=LVL
		if inputLVL!=-1:
			state=str(inputLVL)
			print "input level is at " +str(inputLVL)
		
	elif state=='0':
		print scene
		fade_in_background(15,'UCIC_FINAL.003.png',folder=state)
		time.sleep(15)
		fade_in_background(15,'UCIC_FINAL.004.png',folder=state)
		time.sleep(2)
		fade_in_background(30,'UCIC_FINAL.005.png',folder=state)
		time.sleep(5)
		fade_in_background(15,'UCIC_FINAL.006.png',folder=state)
		time.sleep(2)
		fade_in_background(15,'UCIC_FINAL.007.png',folder=state)
		time.sleep(2)
		fade_in_background(30,'UCIC_FINAL.008.png',folder=state)
		time.sleep(3)
		fade_in_background(15,'UCIC_FINAL.009.png',folder=state)
		time.sleep(1)
		fade_in_background(30,'UCIC_FINAL.010.png',folder=state)
		time.sleep(3)
		fade_in_background(15,'UCIC_FINAL.011.png',folder=state)
		time.sleep(1)
		fade_in_background(15,'UCIC_FINAL.012.png',folder=state)
		time.sleep(1)
		fade_in_background(15,'UCIC_FINAL.013.png',folder=state)
		time.sleep(1)
		fade_in_background(15,'UCIC_FINAL.014.png',folder=state)
		time.sleep(1)
		fade_in_background(15,'UCIC_FINAL.015.png',folder=state)
		time.sleep(1)
		fade_in_background(15,'UCIC_FINAL.016.png',folder=state)
		time.sleep(1)
		fade_in_background(15,'UCIC_FINAL.017.png',folder=state)
		time.sleep(3)
		
		print scene
		
		
		fade_in_overlay(15,'splash','EVENT1','splash.png',(100,100))
		time.sleep(1)
		fade_out_overlay(15,'splash','EVENT1','splash.png',(100,100))
		time.sleep(1)
		add_overlay('splash','EVENT1','splash.png',(100,100))
		add_overlay('dot','EVENT1','test2.png',(100,100))
		time.sleep(1)
		remove_overlay('splash')
		remove_overlay('dot')
		time.sleep(1)
		update_background('test1.jpg')
		time.sleep(1)
		text_input=input_box(200,200,80,'TEST:')
		

	elif state=='1':
		screen.fill((255,255,255))
		update_background('test1.jpg')
		pygame.display.update()
		
		time.sleep(2)
		# fade if splash image
		#for alpha in xrange(255):
	
	elif state=='2':
		print "state=2"		
	
	
	#screen.blit(pygame.image.load(os.path.join('backgrounds','test2.png')),background.get_rect())
	
	

	# fetch the camera image
	
	#surface=pygame.transform.scale(image,(640,480))
	#surface2=pygame.transform.scale(image,(320,240))
	#surface.set_alpha(128)
	#surface2.set_alpha(128)
	
	# make it a player
	#player = surface.convert()
	#player2 = surface2.convert()
	
	#position = player.get_rect()
	#position = position.move(1, 1)     #move player
	#position1=position.move(200,200)	#shrink player
	# blank out the screen
	#surface.fill([0,0,0])
	#surface2.fill([0,0,0])
	
	# copy the camera image to the screen at position of the player
	#screen.blit(player, position)         #draw the player
	#screen.blit(player2, position1)         #draw the player
	
	# update the screen to show the latest screen image
	
