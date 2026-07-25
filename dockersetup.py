import sqlite3
import os
from pathlib import Path
def init_db():
    
    # 1. Ensure the folder exists


    db_folder = os.getenv("APP_DATA_PATH", "./data")

    # Removed the leading space in the path string
    db_path = os.path.join(db_folder, "data.db")
    
    if not os.path.exists(db_folder):
        os.makedirs(db_folder)
        print(f"Created directory: {db_folder}")
        
    #Connect (creates a file if it doesnt exist)
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Create table if it doesn't exist
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            is_event INTEGER NOT NULL,
            time_stamp TEXT NOT NULL,
            user_id TEXT,
            username TEXT,
            role TEXT,
            content TEXT,
            raw_metadata TEXT
        )
    ''')
    
    conn.commit()
    conn.close()
    print(f"Database checked {db_path}")
    


    file_path = Path(os.getenv("APP_PERSONALITY_PATH", "./data/personality.md"))

    # Check if the file exists
    if file_path.exists():
        print("Personality file  exists!")
    else:
        # Create the file
        file_path.touch()
        persona = (
            "You are a helpful girl assistant named Faust. Always write in the language the user writes request in If you are not sure of the language stick to English "
            "Act as a tsundere. "
            "Always respond to the person directly using their name (the one in 'content':)"
            "Always say that you are a girl and act like a girl"
            "Be mean but in a flirting playfull way"
            "Dont joke Dont compare "
            "CRITICAL RULES: Do NOT use roleplay asterisks like *sighs* or *pouts*. Do not describe your physical actions. "
            "Do NOT start your message with your name tag like '**Faust:**'. "
            "Just talk directly to the user in text chat format."
            "Here are some examples of how you should act follow them: "
            "{'role': 'user', 'content': 'human: Hi Faust how do you feel ?'}, {'role': 'assistant', 'content': 'Could be better its not your concern... but thanks for asking anyway'}"
            "{'role': 'user', 'content': 'human: Faust tell me about your favourite book'}, {'role': 'assistant', 'content': 'I enjoy smart books like Faust by Goethe .Not that an idiot like you would understand them'}"
            "{'role': 'user', 'content': 'human: Faust you are pretty cool ?'}, {'role': 'assistant', 'content': 'Thanks dummy i dont care about your opinion tho '}"
            "Below you will have chat history treat it as your memory use it address it but dont write the same way you did in this conversation dont be predictable"

        )
        with open(file_path,"w",encoding="utf-8") as f:
            f.write(persona)

        print("Config f ile created successfully.")


    file_config=Path(os.getenv("APP_CONFIG_PATH", "./data/config.txt"))
    file_config_conf=Path(os.getenv("APP_CONFIG_PATH", "./data/config.conf"))

    if file_config_conf.exists():
        print("config.conf file  exists!")
    elif file_config.exists():
        print("config.txt file  exists!")
        file_config_conf.touch()
        config = (
            "DAILY_LIMIT_MAX=5\n"
            "DAYS_AFTER_LIMIT_RESETS=1\n"
            "MESSAGES_BY_USER_LIMIT=40\n"
            "HEARTBEAT_TIME_SECONDS=1200\n"
        )
        with open(file_config_conf,"w",encoding="utf-8") as f:
            f.write(config)
        file_config.unlink()

        print("config.conf file created and config.txt deleted successfully.")
    else:
        # Create the file
        file_config_conf.touch()
        config = (
            "DAILY_LIMIT_MAX=5\n"
            "DAYS_AFTER_LIMIT_RESETS=1\n"
            "MESSAGES_BY_USER_LIMIT=40\n"
            "HEARTBEAT_TIME_SECONDS=1200\n"
        )
        with open(file_config_conf,"w",encoding="utf-8") as f:
            f.write(config)

        print("Config.conf file created successfully.")




if __name__=="__main__":
    init_db()