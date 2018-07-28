# -*- coding: utf-8 -*-
'''
@author:lulonghui
@date:2018-07-22
@filename:main.py
'''

import random
import sys
import time
import json
import os

# 默认配置
DEFAULT_LIMIT = 1000
DEFAULT_RECORD_PATH = "records.json"
CONFIG_FILE = "config.json"

def init_output_msg(msg):
    ##格式化输入内容
    max_len = 0
    for i in msg:
        if len(i) > max_len:
            max_len = len(i)
    box = '*' * (max_len + 4) + "\n"
    rows = box
    for row in msg:
        row = format(row,"<{}".format(max_len))
        rows = rows + (("{0} {1} {2}\n".format("*",row,"*")))
    rows = rows + box
    return rows

def user_game_info(username,records):
    if username not in records:
        print "{0} doesn't have any record.\n".format(username)
    else:
        user_records = records[username]
        if user_records['total'] == 0:
            print "{0} doesn't have any record.\n".format(username)
        else:
            user_game_info = "Name: {0}\nTotla game: {1}\nBest guess: {2}\tBest time: {3}".format(username,user_records['total'],user_records['best_guess'],user_records['best_time'])
            total_guess = 0
            total_time = 0
            for i in user_records['game_records']:
                total_guess = total_guess + i['guess']
                total_time = total_time + i['time']
            avg_guess = total_guess / float(user_records['total'])
            avg_time = total_time / float(user_records['total'])
            print user_game_info
            print "Avg guess: {0}\tAvg time: {1}s\n".format(avg_guess,avg_time)
            played = 1
            for i in user_records['game_records']:
                print "====== Game {0} at {1} ======\nTarget: {2}\tGuess: {3}\tTime cost: {4}s\n".format(played,i['start'],i['num'],i['guess'],i['time'])
                played += 1

def run():
    ## 判断默认配置文件是否存在，不存在则使用默认值
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE) as f:
            config = json.load(f)
    else:
        config = {"limit":DEFAULT_LIMIT,"record_path":DEFAULT_RECORD_PATH}

    #判断默认的成绩文件是否存在，不存在则置为空
    if os.path.exists(config['record_path']):
        with open(config['record_path']) as f:
            records = json.load(f)
    else:
        records = {}

    #判断是否在执行脚本时指定了要判断的值，没有指定使用随机数
    if len(sys.argv) > 1:
        if sys.argv[1].isdigit():
            target = int(sys.argv[1])
        else:
            print "Error input."
            sys.exit(-1)
    else:
        target = random.randint(1, config["limit"])


    ##定义脚本执行的菜单
    username = raw_input("Please input your name:")
    print "Welcome, {0}!\n".format(username)
    main_msg = ["[g] --> Play Game","[c] --> Config Paramenters","[v] --> View Records","[e] --> Clear Records","[q] --> Quit"]
    #判断用户名是否存在records中，不存在则做用户的初始化，存在则取存在的值
    if username not in records:
        records[username] = {'game_records': [], 'best_time': None, 'best_guess': None, 'total': 0}
    user_records = records[username]
    while True:
        print init_output_msg(main_msg)
        action = raw_input("Your action:")
        action = action.lower()
        if action =='g':
            count = 0
            game_msg = ['Enter number as your guess', '[r] --> Restart', '[q] --> Quit']
            print "\n----- Start Game -----\n{0}".format(init_output_msg(game_msg))
            while True:
                starttime = time.time()
                guess = raw_input("Your guess:")
                guess = guess.lower()
                if guess == "r":
                    target = random.randint(1, config["limit"])
                    continue
                elif guess == "q":
                    print "----- End Game -----\n"
                    target = random.randint(1, config["limit"])
                    break
                else:
                    if guess.isdigit():
                        guess = int(guess)
                    else:
                        print "Error input.\n"
                        continue
                    count += 1
                    if guess < target:
                        print "{0} is too small.\n".format(guess)
                    elif guess > target:
                        print "{0} is too large.\n".format(guess)
                    elif guess == target:
                        endtime = time.time()
                        elapsed = endtime - starttime
                        result = {
                            'num': target,
                            'guess': count,
                            'time': elapsed,
                            'start': time.strftime("%Y-%m-%d %H:%M:%S",time.localtime(starttime))
                        }
                        user_records['game_records'].append(result)
                        print "Bingo! Target:{0},Total guess:{1},Time cost:{2}s".format(target,count,elapsed)
                        if not user_records['best_time'] or elapsed < user_records['best_time']:
                            print "Congratulations! You've made a best guess!"
                            user_records['best_time'] = elapsed
                        if not user_records['best_guess'] or count < user_records['best_guess']:
                            user_records['best_guess'] = count
                        user_records['total'] += 1
                        print "----- End Game -----\n"
                        print "\n----- Start Game -----\n{0}".format(init_output_msg(game_msg))
                        continue
        elif action == "v":
            user_game_info(username,records)
            while True:
                print init_output_msg(['[v] --> View Other Player','[q] --> Back to Main Page'])
                view_select = raw_input("Your action:")
                view_select = view_select.lower()
                if view_select == "v":
                    player = raw_input("please enter other player name: ")
                    user_game_info(player,records)
                elif view_select == "q":
                    break
                else:
                    print "Error input.Please enter again."
                    continue

        elif action == "c":
            print "--- Current config ---\nRecord File Locatiom: {0}\nLimit: {1}\n".format(config['record_path'],config['limit'])
            config_msg = ["[f] --> Record File Location","[l] --> Limit","[q] --> Quit"]
            print init_output_msg(config_msg)
            while True:
                item = raw_input("Select an item:")
                item = item.lower()
                if item == "f":
                    new_path = raw_input("Please enter location to store game records:")
                    #将游戏结果输出到新的路径下
                    with open(new_path,'w') as f:
                        json.dump(records,f)
                    #删除原游戏结果文件
                    os.remove(config['record_path'])
                    #更新配置文件的结果保存路径
                    config['record_path'] = new_path
                    with open(CONFIG_FILE,'w') as f:
                        json.dump(config,f)
                    print "Success!"
                elif item == "l":
                    select = raw_input("Changing limit will erase all previous records.\nDo you want to continue? [y/n]")
                    select = select.lower()
                    if select == "y":
                        while True:
                            new_limit = raw_input("Please enter number limit:")
                            if new_limit.isdigit():
                                if new_limit > 0 :
                                    config['limit'] = int(new_limit)
                                    with open(CONFIG_FILE,'w') as f:
                                        json.dump(config,f)
                                    os.remove(config['record_path'])
                                    print "Success!"
                                    break
                                else:
                                    print "limit must be greater than 1."
                                    continue
                            else:
                                print "Error Input.Please enter again."
                                continue
                    elif select == "n":
                        print init_output_msg(main_msg)
                        break
                elif item == "q":
                    print "Go to main page.\n"
                    break
                else:
                    print "Unknown item,please enter again."
                    continue
            
        elif action == "e":
            os.remove(config['record_path'])
            print "Delete Success!"
            sys.exit(-1)

        elif action == "q":
            with open(config["record_path"],'w') as f:
                json.dump(records,f)
            print "ByeBye!"
            sys.exit(-1)
        else:
            print "Unknown action.\n"



if __name__ == "__main__":
    run()