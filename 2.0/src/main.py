from macros.macros import read_yaml

def main():
    
    files = load_macros('macros','','','')

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
    for count, window_name in enumerate(pygetwindow.getWindowsWithTitle('bombcrypto')):
        windows.append({
            "window": window_name,
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