import time
import os
import random
from pathlib import Path
from datetime import datetime, timedelta,timezone
from multiprocessing import Process
from dotenv import load_dotenv

from kairos import decide
from context import context_kairos
from context import context_call


load_dotenv(dotenv_path="./data/config.conf")
RESET_ANCHOR = datetime.now(timezone.utc)
data_path = os.getenv("APP_DATA_PATH", "./data/")
db_path = os.path.join(data_path, "data.db")

personality_path = "/app/data/personality.md"
personality_path= Path(os.getenv("APP_PERSONALITY_PATH", "./data/personality.md"))

try:
    with open(personality_path, "r", encoding="utf-8") as f:
        CHARACTER_PROFILE= f.read()
except Exception as e:
    print(f"DEBUG: Could not load personality file: {e}")        


#lmits for max times of heartbeast engaging
def restart_limit():
    global RESET_ANCHOR
    now = datetime.now(timezone.utc)
    
    days_after_limit_resets = os.getenv("DAYS_AFTER_LIMIT_RESETS")
    days_after_limit_resets = int(days_after_limit_resets)
    
    if now - RESET_ANCHOR >= timedelta(days_after_limit_resets):
        RESET_ANCHOR = now  
        return True # Signal that it's time to reset
    return False

def check_limits(daily_limit):
    daily_limit_max=os.getenv("DAILY_LIMIT_MAX")
    daily_limit_max=int(daily_limit_max)



    if daily_limit >= daily_limit_max:
        return "daily limit for heartbeat used"
    return 0


#in future engament from 0-100 pulled from config.conf in which it is from 0-1 and multiplied by 100 and rounded
def probability(last_message_minutes_time: int,engagement: int=0) -> float:
        return (last_message_minutes_time*0.0001)
def roll(probability: float) -> bool:
    if random.random() <= probability:
        return True
    else:
        return False
#calculate pulls from the sqlite latest message time
def heartbeating(task_queue):
    #delete this before release
    #last_message_minutes_time=720
    last_message_minutes_time=0
    daily_limit=0
    while True:
        heartbeat_time=os.getenv("HEARTBEAT_TIME_SECONDS")
        heartbeat_time=int(heartbeat_time)
        time.sleep(heartbeat_time)


        #check if required time passed
        if restart_limit():
            daily_limit = 0
            print("Daily limit has been reset.")

        print("daily limit counter: ",daily_limit)
        if check_limits(daily_limit)==0:
            pass
        else:
            print("going to sleep")
            continue

        #If last message is by assistant

        row=context_call(limit=1)
        if row[0]['role'] == "assistant":
            print("Last message by assistant going to sleep")
            continue
        else:
            pass

        print("[Background] Running heartbeat...")
        chance=probability(last_message_minutes_time)
        if roll(chance):
            #some activation here and prompts etc for openfaust to use 
            last_message_minutes_time=0
            daily_limit+=1
            task_queue.put("TRIGGER_WAKE")
            print("Faust activated via heartbeat")
        else:
            last_message_minutes_time+=20


    
    
    





