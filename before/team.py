class Team:
    def __init__(self,sport,league,name,matches = None,next= None):
        self.sport = sport
        self.league = league
        self.name = name
        self.matches = matches or []
        self.next = next or {'date':'' , 'rival': ''}

    def push(self,match):
        self.matches.append(match)

    def peek(self):
        return self.matches[len(self.matches) - 1]


        # match: {'place':'home/away' 'rival' : 'some_team' , 'self_score': int(some_score) ,'rival_score': int(some_score), 'overtime': boolean(yes/no)}
        
    
  
 