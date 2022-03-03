# -*- coding: utf-8 -*-    
from pickle import FALSE
from statistics import multimode
from cv2 import cv2

#from captcha.solveCaptcha import solveCaptcha

from os import listdir

from matplotlib.pyplot import legend
from src.logger import logger, loggerMapClicked
from random import randint
from random import random
import pygetwindow
import numpy as np
import mss
import pyautogui
import time
import sys

import yaml
from datetime import datetime
from PIL import Image

cat = """
>>---> Version 1.2.11 - 2022
>>---> Bot started! Now just wait to gain $$$$ ;)

>>---> Press ctrl + c to stop bot.

In this version:
Add new screen login
Add feature to sleep heroes before refresh
"""

print(cat)

if __name__ == '__main__':
    stream = open("config.yaml", 'r')
    c = yaml.safe_load(stream)

ct = c['threshold']
ch = c['home']

if not ch['enable']:
    print('>>---> Home feature disabled! ')
print('\n')

pause = c['time_intervals']['interval_between_moviments']
pyautogui.PAUSE = pause

pyautogui.FAILSAFE = False
hero_clicks = 0
total_hero_clicks = 0
login_attempts = 0
last_log_is_progress = False
leftWindow = 0
topWindow = 0
widthWindow = 0
heightWindow = 0
multiWindow = False
browserZoom = c['browser_zoom']
offsetAdjustZoom = 1
preventLoop = False
communLast = False

def addRandomness(n, randomn_factor_size=None):
    if randomn_factor_size is None:
        randomness_percentage = 0.1
        randomn_factor_size = randomness_percentage * n

    random_factor = 2 * random() * randomn_factor_size
    if random_factor > 5:
        random_factor = 5
    without_average_random_factor = n - randomn_factor_size
    randomized_n = int(without_average_random_factor + random_factor)
    # logger('{} with randomness -> {}'.format(int(n), randomized_n))
    return int(randomized_n)

def moveToWithRandomness(x,y,t):
    pyautogui.moveTo(addRandomness(x,10),addRandomness(y,10),t+random()/2)

def remove_suffix(input_string, suffix):
    if suffix and input_string.endswith(suffix):
        return input_string[:-len(suffix)]
    return input_string

def selectTargetsFolder():
    global browserZoom
    global offsetAdjustZoom
    result = 'targets'

    if browserZoom == 50:
        result = 'targets_50'
        offsetAdjustZoom = 0.6
    elif browserZoom == 80:
        result = 'targets_80'
        offsetAdjustZoom = 0.8

    return result

def load_images():
    file_names = listdir('./'+selectTargetsFolder()+'/')
    targets = {}
    for file in file_names:
        path = ''+selectTargetsFolder()+'/' + file
        targets[remove_suffix(file, '.png')] = cv2.imread(path)

    return targets

images = load_images()

def loadHeroesToSendHome():
    file_names = listdir('./'+selectTargetsFolder()+'/heroes-to-send-home')
    heroes = []
    for file in file_names:
        path = './'+selectTargetsFolder()+'/heroes-to-send-home/' + file
        heroes.append(cv2.imread(path))

    print('>>---> %d heroes that should be sent home loaded' % len(heroes))
    return heroes

if ch['enable']:
    home_heroes = loadHeroesToSendHome()

#For debug use!!!
def show(rectangles, img = None):
    if img is None:
        with mss.mss() as sct:
            monitor = sct.monitors[0]
            sct_img = np.array(sct.grab(monitor))
            if multiWindow:
                img = sct_img[topWindow:topWindow+heightWindow,leftWindow:leftWindow+widthWindow,:3]                
            else:
                img = sct_img[:,:,:3]

    for (x, y, w, h) in rectangles:
        cv2.rectangle(img, (x, y), (x + w, y + h), (255,255,255,255), 2)

    cv2.imshow('img',img)
    cv2.waitKey(0)

def clickBtn(img,name=None, timeout=3, threshold = ct['default']):
    logger(None, progress_indicator=True)
    if not name is None:
        pass
        # print('waiting for "{}" button, timeout of {}s'.format(name, timeout))
    start = time.time()
    while(True):
        matches = positions(img, threshold=threshold)
        if(len(matches)==0):
            hast_timed_out = time.time()-start > timeout
            if(hast_timed_out):
                if not name is None:
                    pass
                    # print('timed out')
                return False
            # print('button not found yet')
            continue

        x,y,w,h = matches[0]
        pos_click_x = x+w/2
        pos_click_y = y+h/2
        # mudar moveto pra w randomness
        moveToWithRandomness(pos_click_x,pos_click_y,1)
        pyautogui.click()
        return True

def printScreen():
    global multiWindow
    global leftWindow
    global topWindow
    global widthWindow
    global heightWindow

    with mss.mss() as sct:
        monitor = sct.monitors[1]
        sct_img = np.array(sct.grab(monitor))

        if multiWindow:            
            return sct_img[topWindow:topWindow+heightWindow,leftWindow:leftWindow+widthWindow,:3] 

        return sct_img[:,:,:3]

def positions(target, threshold=ct['default'],img = None):
    global multiWindow
    global leftWindow
    global topWindow
    
    if img is None:
        img = printScreen()
    
    rectangles = []
    if not len(img):
        logger("Is not possible find bombcrypto windows, please check de monitors you are using and adjust in config ")
        time.sleep(2)
        return rectangles
    else:        
        result = cv2.matchTemplate(img,target,cv2.TM_CCOEFF_NORMED)
        w = target.shape[1]
        h = target.shape[0]

        yloc, xloc = np.where(result >= threshold)
        
        for (x, y) in zip(xloc, yloc):
            if multiWindow:
                rectangles.append([int(x+leftWindow), int(y+topWindow), int(w), int(h)])
                rectangles.append([int(x+leftWindow), int(y+topWindow), int(w), int(h)])
            else:
                rectangles.append([int(x), int(y), int(w), int(h)])
                rectangles.append([int(x), int(y), int(w), int(h)])

        rectangles, weights = cv2.groupRectangles(rectangles, 1, 0.2)
        return rectangles

def scroll():
    global offsetAdjustZoom
    #img_separator
    #commoms = positions(images['commom-text'], threshold = ct['commom'])
    commoms = positions(images['img_separator'], threshold = ct['commom'])
    if (len(commoms) == 0):
        return
    x,y,w,h = commoms[len(commoms)-1]

    moveToWithRandomness(x,y,1)

    if not c['use_click_and_drag_instead_of_scroll']:
        pyautogui.scroll(-c['scroll_size'])
    else:
        scrollSize = c['click_and_drag_amount'] * offsetAdjustZoom
        pyautogui.dragRel(0,-scrollSize,duration=1, button='left')

def clickButtons():
    global preventLoop
    buttons = positions(images['go-work'], threshold=ct['go_to_work_btn'])
    # print('buttons: {}'.format(len(buttons)))
    for (x, y, w, h) in buttons:
        moveToWithRandomness(x+(w/2),y+(h/2),1)
        pyautogui.click()
        global hero_clicks
        hero_clicks = hero_clicks + 1
        global total_hero_clicks
        total_hero_clicks = total_hero_clicks + 1
        #cv2.rectangle(sct_img, (x, y) , (x + w, y + h), (0,255,255),2)
        if hero_clicks > 5:
            logger('too many hero clicks, try to increase the go_to_work_btn threshold')
            preventLoop = True
            return
    return len(buttons)

def isHome(hero, buttons):
    y = hero[1]

    for (_,button_y,_,button_h) in buttons:
        isBelow = y < (button_y + button_h)
        isAbove = y > (button_y - button_h)
        if isBelow and isAbove:
            # if send-home button exists, the hero is not home
            return False
    return True

def isWorking(bar, buttons):
    y = bar[1]

    for (_,button_y,_,button_h) in buttons:
        isBelow = y < (button_y + button_h)
        isAbove = y > (button_y - button_h)
        if isBelow and isAbove:
            return False
    return True

def isLowBar(bar, lowBars):
    y = bar[1]

    for (_,lowBar_y,_,lowBar_h) in lowBars:
        isBelow = y < (lowBar_y + lowBar_h)
        isAbove = y > (lowBar_y - lowBar_h)
        if isBelow and isAbove:
            return True
    return False

def isFullBar(bar, fullBars):
    y = bar[1]

    for (_,fullBar_y,_,fullBar_h) in fullBars:
        isBelow = y < (fullBar_y + fullBar_h)
        isAbove = y > (fullBar_y - fullBar_h)
        if isBelow and isAbove:
            return True
    return False

def isCommum(bar, communPositions):
    y = bar[1]

    for (_,cp_y,_,cp_h) in communPositions:        
        isBelow = y < (cp_y + cp_h)
        isAbove = y > (cp_y - cp_h)
        if isBelow and isAbove:
            return True
    return False

def clickGreenBarButtons(sendCommuns=False):
    global offsetAdjustZoom  
    global preventLoop
    global communLast

    offset = round(130 * offsetAdjustZoom)

    commoms = positions(images['commom-text'], threshold = ct['commom'])
    logger(' %d common heroes detected' % len(commoms))
    rare = positions(images['rare-text'], threshold = ct['commom'])
    logger(' %d rare heroes detected' % len(rare))
    sr = positions(images['sr-text'], threshold = ct['commom'])
    logger(' %d super rare heroes detected' % len(sr))
    epic = positions(images['epic-text'], threshold = ct['commom'])
    logger(' %d epic heroes detected' % len(epic))
    legend = positions(images['legend-text'], threshold = ct['commom'])
    logger(' %d legend heroes detected' % len(legend))
    sl = positions(images['sl-text'], threshold = ct['commom'])
    logger(' %d super legend heroes detected' % len(sl))

    low_bar_0 = positions(images['low_bar_0'], threshold=0.9)    
    low_bar_1 = positions(images['low_bar_1'], threshold=0.9)    
    low_bar_2 = positions(images['low_bar_2'], threshold=0.9)    
    low_bar_3 = positions(images['low_bar_3'], threshold=0.9)
    logger(' %d low_bars detected' % (len(low_bar_0)+len(low_bar_1)+len(low_bar_2)+len(low_bar_3)))

    full_bars = positions(images['full-stamina'], threshold=ct['green_bar'])
    logger(' %d full bars detected' % len(full_bars))

    green_bars = positions(images['green-bar'], threshold=ct['green_bar'])
    logger(' %d green bars detected' % len(green_bars))
    buttons = positions(images['go-work'], threshold=ct['go_to_work_btn'])
    logger(' %d buttons detected' % len(buttons))

    not_working_green_bars = []
    for bar in green_bars:
        if not isWorking(bar, buttons) or \
           (not isLowBar(bar, low_bar_0) and not isLowBar(bar, low_bar_1) \
            and not isLowBar(bar, low_bar_2) and not isLowBar(bar, low_bar_3)):
            
            if isFullBar(bar, full_bars):
                not_working_green_bars.append(bar)     
            elif communLast:                  
                if sendCommuns and isCommum(bar, commoms):                    
                    not_working_green_bars.append(bar)
                elif not sendCommuns and not isCommum(bar, commoms):
                    not_working_green_bars.append(bar)
            else:                
                not_working_green_bars.append(bar)                    

    if len(not_working_green_bars) > 0:
        logger(' %d buttons with green bar detected' % len(not_working_green_bars))
        logger(' Clicking in %d heroes' % len(not_working_green_bars))

    # se tiver botao com y maior que bar y-10 e menor que y+10
    for (x, y, w, h) in not_working_green_bars:
        # isWorking(y, buttons)
        moveToWithRandomness(x+offset+(w/2),y+(h/2),1)
        pyautogui.click()
        global hero_clicks
        hero_clicks = hero_clicks + 1
        global total_hero_clicks
        total_hero_clicks = total_hero_clicks + 1
        if hero_clicks > 5:
            logger('Too many hero clicks, try to increase the go_to_work_btn threshold')
            preventLoop = True
            return
        #cv2.rectangle(sct_img, (x, y) , (x + w, y + h), (0,255,255),2)
    return len(not_working_green_bars)

def clickFullBarButtons():
    global offsetAdjustZoom
    offset = round(100 * offsetAdjustZoom)
    full_bars = positions(images['full-stamina'], threshold=ct['default'])
    buttons = positions(images['go-work'], threshold=ct['go_to_work_btn'])

    not_working_full_bars = []
    for bar in full_bars:
        if not isWorking(bar, buttons):
            not_working_full_bars.append(bar)

    if len(not_working_full_bars) > 0:
        logger(' Clicking in %d heroes' % len(not_working_full_bars))

    for (x, y, w, h) in not_working_full_bars:
        moveToWithRandomness(x+offset+(w/2),y+(h/2),1)
        pyautogui.click()
        global hero_clicks
        hero_clicks = hero_clicks + 1
        global total_hero_clicks
        total_hero_clicks = total_hero_clicks + 1

    return len(not_working_full_bars)

def clickAllRestButton():    
    global offsetAdjustZoom
    global preventLoop
    time.sleep(1) #wait load button before try click in
    offset = round(9 * offsetAdjustZoom)
    all_btn_position = positions(images['all_btn_rest'], threshold=ct['all_btn_rest'])
    logger(' %d all rest button detected' % len(all_btn_position))
    
    for (x, y, w, h) in all_btn_position:        
        moveToWithRandomness(x+offset+(w/2),y+(h/2)+3,1)
        pyautogui.click()
        global hero_clicks
        hero_clicks = hero_clicks + 1
        global total_hero_clicks
        total_hero_clicks = total_hero_clicks + 1
        if hero_clicks > 2:
            logger('Too many all clicks, try to increase the all_btn_rest threshold')
            preventLoop = True
            return
        
    return len(all_btn_position)

def clickAllButton():    
    global offsetAdjustZoom
    global preventLoop
    time.sleep(1) #wait load button before try click in
    offset = round(9 * offsetAdjustZoom)
    all_btn_position = positions(images['all_btn'], threshold=ct['all_btn'])
    logger(' %d all button detected' % len(all_btn_position))
    
    for (x, y, w, h) in all_btn_position:        
        moveToWithRandomness(x+offset+(w/2),y+(h/2)+3,1)
        pyautogui.click()
        global hero_clicks
        hero_clicks = hero_clicks + 1
        global total_hero_clicks
        total_hero_clicks = total_hero_clicks + 1
        if hero_clicks > 2:
            logger('Too many all clicks, try to increase the all_btn threshold')
            preventLoop = True
            return
        
    return len(all_btn_position)

def goToHeroes():
    if clickBtn(images['go-back-arrow']):
        global login_attempts
        login_attempts = 0
    
    if not clickBtn(images['hero-icon']):
        clickBtn(images['hero-icon'])

    time.sleep(2) #need to wait to open heroes
    
def goToGame():    
    logger('Closed popup and enter in map')    
    if not clickBtn(images['x']):
        if not clickBtn(images['x']):
            clickBtn(images['x'])
    
    if not clickBtn(images['treasure-hunt-icon']):
        if not clickBtn(images['treasure-hunt-icon']):
            clickBtn(images['treasure-hunt-icon'])

def refreshHeroesPositions():
    count = 0
    logger('Refreshing Heroes Positions')
    if clickBtn(images['go-back-arrow']):
        while not clickBtn(images['treasure-hunt-icon']):
            clickBtn(images['treasure-hunt-icon'])
            count += 1
            time.sleep(1)
            if count > 3:
                logger('Is not possible enter in map again')
                break

def rewardsFollowPrint(windowIdx="0"):
    global leftWindow
    global topWindow
    logger('Click in chest reward')
    time.sleep(5) #just wait to enter in map, before click in chest reward
    if clickBtn(images['chest_rewards'], threshold=0.9):
        time.sleep(10) #sometimes the reward is very slow to show
        fileName = "ChestReward_Window-"+ windowIdx + "_left-" + str(leftWindow) + "_top-" + str(topWindow) + "_" + str(datetime.utcnow().strftime('%Y-%m-%d-%H-%M-%S')) + ".png"
        logger(fileName)
        path = "chest/"
        saveImg(printScreen(), fileName, path) 
        count = 0
        while not clickBtn(images['x']):
            clickBtn(images['x'])
            count += 1
            time.sleep(1)
            if count > 3:
                logger('Is not possible close the chest reward')
                break

def saveImg(img, fileName, path="temp/"):  
    img = Image.fromarray(cv2.cvtColor(img, cv2.COLOR_BGR2RGB), mode="RGB")    
    img.save(path+fileName)

def login():
    global login_attempts
    logger('Checking if game has disconnected')

    if login_attempts > 3:
        logger(' Too many login attempts, refreshing')
        login_attempts = 0
        pyautogui.hotkey('ctrl','f5')
        return

    if clickBtn(images['ok'], name='okBtn', timeout=3):
        logger('Ok Button detected, clicked')
        login()

    if clickBtn(images['connect-wallet'], name='connectWalletBtn', timeout = 13):
        logger(' Connect wallet button detected, logging in!')        
        login_attempts = login_attempts + 1
    elif clickBtn(images['connect-login'], name='connectLoginBtn', timeout = 3):
        logger(' Connect login button detected, clicked in!')        
        login_attempts = login_attempts + 1    
    elif clickBtn(images['recarregar'], name='recarregarBtn', timeout = 3) or clickBtn(images['recarregar_2'], name='recarregarBtn', timeout = 3):
        logger('Out of memory error, please check! Retryng login')
        login_attempts = 0
        login()    
    else:
        return

    if clickBtn(images['connect-login'], name='connectLoginBtn', timeout = 3):
        logger(' Connect login button detected, clicked in!')        
        login_attempts = login_attempts + 1

    if clickBtn(images['recarregar'], name='recarregarBtn', timeout = 2) or clickBtn(images['recarregar_2'], name='recarregarBtn', timeout = 2):
        logger('Out of memory error, please check! Retryng login')
        login_attempts = 0
        login()
    elif clickBtn(images['ok'], name='okBtn', timeout=2):
        logger('Ok Button detected, clicked')
        login()

    global leftWindow
    global topWindow
    global widthWindow
    global heightWindow
    if browserZoom == 50:
        tempLeftWindow = leftWindow
        tempTopWindow = topWindow
        tempWidthWindow = widthWindow
        tempHeightWindow = heightWindow
        for count, w in enumerate(pygetwindow.getWindowsWithTitle('MetaMask Notification')):
            w.activate()
            leftWindow = w.left
            topWindow = w.top
            widthWindow = w.width
            heightWindow = w.height            
            logger('Window MetaMask ' + str(count) + ' selected, position > ')
            logger(w)

            if ((len(positions(images['select-wallet-2-eng'])) > 0) and clickBtn(images['select-wallet-2-eng'], name='sign button', timeout=6)) or \
                ((len(positions(images['select-wallet-2'])) > 0) and clickBtn(images['select-wallet-2'], name='sign button', timeout=6)):
                leftWindow = tempLeftWindow
                topWindow = tempTopWindow
                widthWindow = tempWidthWindow
                heightWindow = tempHeightWindow 

                # sometimes the sign popup appears imediately
                login_attempts = login_attempts + 1
                if clickBtn(images['recarregar'], name='recarregarBtn', timeout = 3) or clickBtn(images['recarregar_2'], name='recarregarBtn', timeout = 3):
                    logger('Out of memory error, please check! Retryng login')
                    login_attempts = 0
                    login()
                elif clickBtn(images['treasure-hunt-icon'], name='teasureHunt', timeout = 8):            
                    login_attempts = 0
                if clickBtn(images['ok'], name='okBtn', timeout=3):
                    logger('Ok Button detected, clicked')
                    login()
                return 
    else:
        if ((len(positions(images['select-wallet-2-eng'])) > 0) and clickBtn(images['select-wallet-2-eng'], name='sign button', timeout=6)) or \
            ((len(positions(images['select-wallet-2'])) > 0) and clickBtn(images['select-wallet-2'], name='sign button', timeout=6)):
            # sometimes the sign popup appears imediately
            login_attempts = login_attempts + 1
            if clickBtn(images['recarregar'], name='recarregarBtn', timeout = 4) or clickBtn(images['recarregar_2'], name='recarregarBtn', timeout = 4):
                logger('Out of memory error, please check! Retryng login')
                login_attempts = 0
                login()
            elif clickBtn(images['treasure-hunt-icon'], name='teasureHunt', timeout = 8):            
                login_attempts = 0
            if clickBtn(images['ok'], name='okBtn', timeout=4):
                logger('Ok Button detected, clicked')
                login()
            return           

    if browserZoom == 50:
        tempLeftWindow = leftWindow
        tempTopWindow = topWindow
        tempWidthWindow = widthWindow
        tempHeightWindow = heightWindow
        for count, w in enumerate(pygetwindow.getWindowsWithTitle('MetaMask Notification')):
            w.activate()
            leftWindow = w.left
            topWindow = w.top
            widthWindow = w.width
            heightWindow = w.height            
            logger('Window MetaMask ' + str(count) + ' selected, position > ')
            logger(w)

            if ((len(positions(images['select-wallet-2-eng'])) > 0) and clickBtn(images['select-wallet-2-eng'], name='sign button', timeout=10)) or \
                ((len(positions(images['select-wallet-2'])) > 0) and clickBtn(images['select-wallet-2'], name='sign button', timeout=10)):
                leftWindow = tempLeftWindow
                topWindow = tempTopWindow
                widthWindow = tempWidthWindow
                heightWindow = tempHeightWindow 
                login_attempts = login_attempts + 1
                if clickBtn(images['recarregar'], name='recarregarBtn', timeout = 4) or clickBtn(images['recarregar_2'], name='recarregarBtn', timeout = 4):
                    logger('Out of memory error, please check! Retryng login')
                    login_attempts = 0
                    login()
                elif clickBtn(images['treasure-hunt-icon'], name='teasureHunt', timeout=12):          
                    login_attempts = 0            
    else:
        if ((len(positions(images['select-wallet-2-eng'])) > 0) and clickBtn(images['select-wallet-2-eng'], name='sign button', timeout=10)) or \
            ((len(positions(images['select-wallet-2'])) > 0) and clickBtn(images['select-wallet-2'], name='sign button', timeout=10)):
            login_attempts = login_attempts + 1
            if clickBtn(images['recarregar'], name='recarregarBtn', timeout = 4) or clickBtn(images['recarregar_2'], name='recarregarBtn', timeout = 4):
                logger('Out of memory error, please check! Retryng login')
                login_attempts = 0
                login()
            elif clickBtn(images['treasure-hunt-icon'], name='teasureHunt', timeout=12):          
                login_attempts = 0            

    if clickBtn(images['ok'], name='okBtn', timeout=3):
        logger('Ok Button detected, clicked')
        login()

def sendHeroesHome():
    if not ch['enable']:
        return
    heroes_positions = []
    for hero in home_heroes:
        hero_positions = positions(hero, threshold=ch['hero_threshold'])
        if not len (hero_positions) == 0:
            #TODO maybe pick up match with most wheight instead of first
            hero_position = hero_positions[0]
            heroes_positions.append(hero_position)

    n = len(heroes_positions)
    if n == 0:
        print('No heroes that should be sent home found.')
        return
    print(' %d heroes that should be sent home found' % n)
    # if send-home button exists, the hero is not home
    go_home_buttons = positions(images['send-home'], threshold=ch['home_button_threshold'])
    # TODO pass it as an argument for both this and the other function that uses it
    go_work_buttons = positions(images['go-work'], threshold=ct['go_to_work_btn'])

    for position in heroes_positions:
        if not isHome(position,go_home_buttons):
            print(isWorking(position, go_work_buttons))
            if(not isWorking(position, go_work_buttons)):
                print ('hero not working, sending him home')
                moveToWithRandomness(go_home_buttons[0][0]+go_home_buttons[0][2]/2,position[1]+position[3]/2,1)
                pyautogui.click()
            else:
                print ('hero working, not sending him home(no dark work button)')
        else:
            print('hero already home, or home full(no dark home button)')

def sleepAllHeroes():    
    logger('Search for heroes to sleep')
    goToHeroes()

    global total_hero_clicks
    total_hero_clicks = 0
    global hero_clicks
    hero_clicks = 0

    empty_scrolls_attempts = c['scroll_attemps']
    while(empty_scrolls_attempts >0):
        logger('------------------')
        logger('Loop scroll attempts, count: ' + str(empty_scrolls_attempts))
        logger('Loop total hero clicks, count: ' + str(total_hero_clicks))
        if total_hero_clicks > 20:
            empty_scrolls_attempts = -1
            break

        buttonsClicked = clickAllRestButton()
        empty_scrolls_attempts = empty_scrolls_attempts - 2
        
        time.sleep(3)
    logger('{} all button clicked'.format(hero_clicks))


def refreshHeroes(sendCommuns=False):
    global preventLoop
    logger('Search for heroes to work')
    goToHeroes()

    isAllBtn = False
    if c['select_heroes_mode'] == "full":
        logger('Sending heroes with full stamina bar to work')
    elif c['select_heroes_mode'] == "green":
        logger('Sending heroes with green stamina bar to work')
    elif c['select_heroes_mode'] == "allBtn":
        isAllBtn = True
        logger('Sending all heroes in btn all')
    else:
        logger('Sending all heroes to work')

    buttonsClicked = 1
    empty_scrolls_attempts = c['scroll_attemps']
    
    global total_hero_clicks
    total_hero_clicks = 0
    global hero_clicks
    hero_clicks = 0

    preventLoop = False
    while(empty_scrolls_attempts >0):
        logger('------------------')
        logger('Loop scroll attempts, count: ' + str(empty_scrolls_attempts))
        logger('Loop total hero clicks, count: ' + str(total_hero_clicks))
        if preventLoop or total_hero_clicks > 20:
            empty_scrolls_attempts = -1
            break

        if c['select_heroes_mode'] == 'full':
            buttonsClicked = clickFullBarButtons()
        elif c['select_heroes_mode'] == 'green':
            buttonsClicked = clickGreenBarButtons(sendCommuns)
        elif isAllBtn:
            buttonsClicked = clickAllButton()
        else:
            buttonsClicked = clickButtons()        

        sendHeroesHome()

        #if buttonsClicked == 0 or preventLoop:
        if isAllBtn:
            empty_scrolls_attempts = empty_scrolls_attempts - 2
        else:
            empty_scrolls_attempts = empty_scrolls_attempts - 1

        if not isAllBtn:
            scroll()            
            hero_clicks = 0
            preventLoop = False
        
        time.sleep(3)
        
    if isAllBtn:
        logger('{} all button clicked'.format(hero_clicks))
    else:
        logger('{} heroes sent to work'.format(hero_clicks))

    goToGame()
    return total_hero_clicks

def checkError():
    posConWal = positions(images['connect-wallet'])
    if len(posConWal) > 0:
        return True
    
    posOk = positions(images['ok'])
    if len(posOk) > 0:
        return True
    
    posRec = positions(images['recarregar'])
    if len(posRec) > 0:
        return True
    
    posWhite = positions(images['white-screen'])
    if len(posWhite) > 0:
        return True

    posLoggin = positions(images['connect-login'])
    if len(posLoggin) > 0:
        return True

    posLoaScr = positions(images['load_screen'])
    if len(posLoaScr) > 0:
        pyautogui.hotkey('ctrl','f5')
        time.sleep(5)
        return True

    return False

def main():    
    t = c['time_intervals']
    global multiWindow
    global leftWindow
    global topWindow
    global widthWindow
    global heightWindow
    global communLast
    
    multiWindow = c['split_window']
    communLast = c['commum_last']
    windows = []

    count = 0
    for count, w in enumerate(pygetwindow.getWindowsWithTitle('bombcrypto')):
        windows.append({
            "window": w,
            "login"+ str(count) : 0,
            "refresh"+ str(count) : time.time(),
            "heroes"+ str(count) : 0,
            "new_map"+ str(count) : 0,
            "check_for_captcha"+ str(count) : 0,
            "refresh_heroes"+ str(count) : 0,
            "rewards_follow"+ str(count) : 0,
            "commum_last"+ str(count): communLast
            })

    while True:
        now = time.time()
        sendHero = False
        idx = 0
        for idx, last in enumerate(windows):
            last["window"].activate()
            leftWindow = last["window"].left
            topWindow = last["window"].top
            widthWindow = last["window"].width
            heightWindow = last["window"].height
            #time.sleep(1)
            logger('Window ' + str(idx) + ' selected, position > ')
            logger(last["window"])

            doLogin = False
            if checkError():
                logger("Connect-Wallet, Ok or recarregar button detected, login is running!")
                login()
                last["login"+ str(idx)] = now
                doLogin = True

            if not doLogin and now - last["refresh"+ str(idx)] > addRandomness(t['refresh_avoid_bug'] * 60):
                if c['sleep_all_heroes_before_refresh']:
                    sleepAllHeroes()
                pyautogui.hotkey('ctrl','f5')
                last["refresh"+ str(idx)] = now
                last["login"+ str(idx)] = now
                login()
                sendHero = True
            else:
                sendHero = False

            if checkError():
                logger("Connect-Wallet, Ok or recarregar button detected, login is running!")
                login()
                last["login"+ str(idx)] = now
                doLogin = True

            #if not doLogin and now - last["login"+ str(idx)] > addRandomness(t['check_for_login'] * 60):
                #sys.stdout.flush()
                #last["login"+ str(idx)] = now
                #login()
            
            timeoutSendHeroes = addRandomness(t['send_heroes_for_work'] * 60)
            if(communLast and not last["commum_last"+ str(idx)]):
                timeoutSendHeroes = timeoutSendHeroes * 2
            
            if checkError():
                logger("Connect-Wallet, Ok or recarregar button detected, login is running!")
                login()
                last["login"+ str(idx)] = now
                doLogin = True

            if now - last["heroes"+ str(idx)] > timeoutSendHeroes:
                sendHero = True
                last["heroes"+ str(idx)] = now
                heroesSendToWork = refreshHeroes(sendCommuns=not last["commum_last"+ str(idx)])
                if communLast:
                    if heroesSendToWork == 0:
                        logger("Nobody was sent to work, trying sent the other group now")
                        time.sleep(3)
                        heroesSendToWork = refreshHeroes(sendCommuns=last["commum_last"+ str(idx)])
                    
                    last["commum_last"+ str(idx)] = not last["commum_last"+ str(idx)]
            else:
                sendHero = False

            if checkError():
                logger("Connect-Wallet, Ok or recarregar button detected, login is running!")
                login()
                last["login"+ str(idx)] = now
                doLogin = True

            if (now - last["refresh_heroes"+ str(idx)] > addRandomness( t['refresh_heroes_positions'] * 60)) and not sendHero:                
                last["refresh_heroes"+ str(idx)] = now
                refreshHeroesPositions()

            if checkError():
                logger("Connect-Wallet, Ok or recarregar button detected, login is running!")
                login()
                last["login"+ str(idx)] = now
                doLogin = True

            if (now - last["rewards_follow"+ str(idx)] > addRandomness( t['rewards_follow_check'] * 60)):                
                last["rewards_follow"+ str(idx)] = now
                rewardsFollowPrint(str(idx))

            logger(None, progress_indicator=True)
            sys.stdout.flush()
            time.sleep(2)
            
main()