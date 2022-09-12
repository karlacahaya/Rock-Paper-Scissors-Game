
import numpy as np
import pygame, sys,os,json,datetime,random, cv2, utils
from pygame.locals import *
from components import RockPaperScissor, Camera
from keras.models import load_model
pygame.init()



SCREEN = pygame.display.set_mode((0,0), FULLSCREEN)
s_width, s_height = SCREEN.get_size()
pygame.display.set_caption("Menu")
menuChange_sound = pygame.mixer.Sound(os.path.join("sound", 'menuChange.wav'))
menuConfirm_sound = pygame.mixer.Sound(os.path.join("sound", 'UiConfirm_alert.wav'))
BG = pygame.image.load("background/main_menu2.jpg")


class Button(): 
	def __init__(self, image, pos, text_input, font, base_color, hovering_color):
		self.image = image
		self.x_pos = pos[0]
		self.y_pos = pos[1]
		self.font = font
		self.base_color, self.hovering_color = base_color, hovering_color
		self.text_input = text_input
		self.text = self.font.render(self.text_input, True, self.base_color)
		if self.image is None:
			self.image = self.text
		self.rect = self.image.get_rect(center=(self.x_pos, self.y_pos))
		self.text_rect = self.text.get_rect(center=(self.x_pos, self.y_pos))
		
	def update(self, screen):
		if self.image is not None:
			screen.blit(self.image, self.rect)
		screen.blit(self.text, self.text_rect)

	def checkForInput(self, position):
		if position[0] in range(self.rect.left, self.rect.right) and position[1] in range(self.rect.top, self.rect.bottom):
			return True
		return False

	def changeColor(self, position):
		if position[0] in range(self.rect.left, self.rect.right) and position[1] in range(self.rect.top, self.rect.bottom):
			self.text = self.font.render(self.text_input, True, self.hovering_color)
		else:
			self.text = self.font.render(self.text_input, True, self.base_color)


class High_score:
    score= None
    font= None
    scores= None
    new_score = None
    new_name= None
    
    FILE_NAME_JSON = 'highscore.json'
    def __init__(self, new_name, new_score):
        self.score = 0
        self.font = pygame.font.SysFont("monospace", 15)
        self.new_score = int(new_score) 
        self.new_name = new_name 

        if not os.path.isfile(self.FILE_NAME_JSON):
            self.on_empty_file()
        else :
            self.record_score()
            
            
    def on_empty_file(self): # write new file json
        empty_score_file = open(self.FILE_NAME_JSON,"w")
        empty_score_file.write('[]')
        empty_score_file.close()

    def record_score(self):
        if not self.scores == None:
                new_json_score = { # Create a JSON-object with the score, name and a timestamp.
                    "name":self.new_name,
                    "score":self.new_score,
                    "time":str(datetime.datetime.now().time())
                    }
                self.scores.append(new_json_score) # Add the score to the list of scores.
                self.scores = self.sort_scores(self.scores) # Sort the scores.
                
                highscore_file = open(self.FILE_NAME_JSON, "r+")
                highscore_file.write(json.dumps(self.scores, indent=1)) # Save the list of scores to highscore.json
        else:
            self.load_existed_highscore() 
            self.record_score() 

    def sort_scores(self, json):        
        scores_dict = dict() # Create a dictionary object.
        sorted_list = list() # Create a list object.

        for obj in json:
            scores_dict[obj["score"]]=obj # Add every score to a dictionary with its score as key. Key collisions ensue...

        for key in sorted(scores_dict.keys(), reverse=True): # Read the sorted dictionary in reverse order (highest score first)...
            sorted_list.append(scores_dict[key]) 

        return sorted_list 

    def load_existed_highscore(self):
        with open(self.FILE_NAME_JSON) as highscore_file:
           self.scores = json.load(highscore_file)
           self.scores = self.scores
        for i in self.scores:
            print(i['score'], " ",i['name'])

def get_font(size): # Returns Press-Start-2P in the desired size
    return pygame.font.Font("font/Pixeboy-z8XGD.ttf", size) 

def text_format(message, textFont, textSize, textColor):
        newFont=pygame.font.Font(textFont, textSize)
        newText=newFont.render(message, 0, textColor)
        return newText
        

def rpsGame(totalScore):
    # --- Init
    camera = Camera()
    rps = RockPaperScissor(totalScore)
    global score
    rps.setCImg(1)
    model = load_model("rock-paper-scissors-model.h5")

    while rps.carryOn:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                rps.quit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    rps.startTimer(3)
                if event.key == pygame.K_ESCAPE:
                    camera.quit()
                    show_scores(END_GAME = True)

        # --- opencv pImg
        frame_roi = camera.get_frame()
        rps.setPImg(frame_roi)

        if rps.duration == 0 and rps.timer_started:

            # --- cImg
            c_num = random.randint(0, 2)
            rps.setCImg(c_num)

            # model predicts
            x = camera.save_current_frame(frame_roi)
            y = model.predict(x)
            print("[MODEL] Max Probability: " + str(np.max(y)))
            p_num = np.argmax(y, axis=1)[0]
            print("[GAME] Player: " + utils.gestureText[int(np.argmax(y, axis=1))])
            print("[GAME] Computer: {}".format(utils.gestureText[c_num]))
            rps.decideWinner(c_num, p_num)
            
            rps.stopTimer()

        # --- Drawing background code
        rps.draw_ui()

        # --- updating Timer
        rps.updateTimer()
        score = rps.updateScores()
        
    camera.quit()
    rps.quit()

    
def show_scores(END_GAME=False):
    pygame.display.set_caption('Highestscore Board')
    textS = ''
    
    color_default = 'blue'
    color_active = pygame.Color('green')
    color_passive = pygame.Color('blue')

    # input color state
    active = False
    running =  True
    
    while running:
            SCOREMENU_MOUSE_POS = pygame.mouse.get_pos()

            SCREEN.blit(pygame.image.load("background/score_menu.jpg"),(0,0))

            
            SCOREMENU_BACK = Button(image=None, pos=(s_width/8 - 100,s_height - 50), 
                                text_input="BACK", font=get_font(50), base_color="White", hovering_color="Green")

            SCOREMENU_BACK.changeColor(SCOREMENU_MOUSE_POS)
            SCOREMENU_BACK.update(SCREEN)
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if  SCOREMENU_BACK.checkForInput( SCOREMENU_MOUSE_POS):
                        pygame.mixer.Sound.play(menuConfirm_sound)
                        main_menu()
                    
                    if input_rect.collidepoint(event.pos):
                        active = True
                    else :
                        active = False
                if event.type == pygame.KEYDOWN:
                    if event.key == K_ESCAPE:
                            pygame.quit()
                            quit()
                    if active:
                        if event.key == pygame.K_BACKSPACE:
                            textS = textS[:-1]
                            if event.key == pygame.K_RETURN: 
                                High_score(textS, score)              
                                main_menu()   
                        else:
                            textS += event.unicode
                            if event.key == pygame.K_RETURN:
                                High_score(textS, score)
                                main_menu()   
                          
            if active:
                color_default = color_active
            else: 
                color_default = color_passive

            user_text = pygame.font.Font('font/Pixeboy-z8XGD.ttf',25).render(textS, True,(255,255,255))    
            title= text_format("Scores", 'font/Pixeboy-z8XGD.ttf', 90, 'white')
            title_rect = title.get_rect()  
            input_label = text_format("Insert Name Here : ", 'font/Pixeboy-z8XGD.ttf', 40, 'white')
            input_rect = pygame.Rect(s_width/2-250,s_height/2+180 ,140,32)#text form
            input_rect.w = max(500,user_text.get_width(),200)
            
            if END_GAME:
                SCREEN.blit(user_text,(input_rect.x + 5,input_rect.y + 5))
                SCREEN.blit(input_label, (s_width/2-150,s_height/2+150 ))
                pygame.draw.rect(SCREEN, color_default, input_rect, 2)    

            SCREEN.blit(title, (s_width/2-150,s_height/8))
            with open('highscore.json') as highscore_file:
                data = json.load(highscore_file)
                padding_y = 0
                max_scores = 6 # We *could* paint every score, but it's not any good if you can't see them (because we run out of the screen).
                nbr_scores = 1
                for i in data:
                    if nbr_scores <= max_scores:                    
                        SCREEN.blit(pygame.font.Font(None,40).render(str(nbr_scores)+" " +str(i["name"]), 1, ('white')), (title_rect[2]/2 + 400,200 + padding_y))
                        SCREEN.blit(pygame.font.Font(None,40).render(str(i["score"]), 1, ('white')), (title_rect[2]+700, 200 + padding_y))
                        padding_y += 50
                        nbr_scores += 1

            pygame.display.update()
    
def main_menu():
    pygame.mixer.music.load(os.path.join("sound", 'mainMenuMusic.mp3'))
    pygame.mixer.music.play(-1)	# -1 to made music infinitely loop
    while True:
        SCREEN.blit(BG, (0, 0))

        MENU_MOUSE_POS = pygame.mouse.get_pos()

        MENU_TEXT = get_font(100).render("ROCK SCISSORS GAME", True, "red")
        MENU_RECT = MENU_TEXT.get_rect(center=(s_width/2, s_height/6))

        PLAY_BUTTON = Button(image=pygame.image.load("background/menu_rect.png"), pos=(s_width/4 - 50, s_height/2 + 50), 
                            text_input="PLAY", font=get_font(40), base_color="#d7fcd4", hovering_color="Green")
        SCOREMENU_BUTTON = Button(image=pygame.image.load("background/menu_rect.png"), pos=(s_width/2, s_height/2 + 50), 
                            text_input="SCORES", font=get_font(40), base_color="#d7fcd4", hovering_color="Green")
        QUIT_BUTTON = Button(image=pygame.image.load("background/menu_rect.png"), pos=(s_width - 250, s_height/2 + 50), 
                            text_input="QUIT", font=get_font(40), base_color="#d7fcd4", hovering_color="Green")

        SCREEN.blit(MENU_TEXT, MENU_RECT)

        for button in [PLAY_BUTTON,  SCOREMENU_BUTTON, QUIT_BUTTON]:
            button.changeColor(MENU_MOUSE_POS)
            button.update(SCREEN)
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if PLAY_BUTTON.checkForInput(MENU_MOUSE_POS):
                    pygame.mixer.Sound.play(menuConfirm_sound)
                    print("[INFO] To get started, press 'SPACE' after adjusting hand in the box")
                    rpsGame(totalScore=10)
                if  SCOREMENU_BUTTON.checkForInput(MENU_MOUSE_POS):
                    pygame.mixer.Sound.play(menuConfirm_sound)
                    show_scores()
                if QUIT_BUTTON.checkForInput(MENU_MOUSE_POS):
                    pygame.mixer.Sound.play(menuConfirm_sound)
                    pygame.quit()
                    sys.exit()
        pygame.display.update()

main_menu()
