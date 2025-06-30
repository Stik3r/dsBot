import os
import sys
from bot import init

def main(voice_assistant, bypass_path):
    voice_assistant_bool = False
    if voice_assistant.lower() == "true":
        voice_assistant_bool = True
    if bypass_path == "":
        bypass_path = None
    bot = init(voice_assistant_bool, bypass_path)
    bot.run(os.getenv("DISCORD_TOKEN"))

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Wrong arguments count")
        sys.exit(1)

    main(sys.argv[1], sys.argv[2])

