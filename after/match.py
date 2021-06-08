class Match:
    def __init__(self,date,team,rival,self_score,rival_score,place, maintime):
        self.date = date
        self.team = team
        self.rival = rival
        if maintime:
            self.score = maintime['home-score']
            self.rival_score = maintime['guest-score']
            self.total_score = int(self_score)
            self.rival_total_score = int(rival_score)         
        else:
            self.score = int(self_score)
            self.rival_score = int(rival_score)
            self.total_score = int(self_score)
            self.rival_total_score = int(rival_score)
        self.place = place 
        self.maintime = maintime
    
    def odd_even(self):
        return "Чёт" if (self.score + self.rival_score) % 2 == 0 else "Нечет"

    def total(self):
        return self.score + self.rival_score
        
    def total_with_overtime(self):
        return self.total_score + self.rival_total_score

    def match_score(self):
        if self.place =="дом":
            return "{} -- {} ".format(self.total_score , self.rival_total_score)  
        else:
            return "{} -- {} ".format(self.rival_total_score,self.total_score)

    def ind_odd_even(self):
        return "Чёт" if self.score % 2 == 0 else  "Нечет"
    
    def result(self):
        if self.total_score > self.rival_total_score:
            return "Победа"
        elif self.total_score == self.rival_total_score:
            return "Ничья" 
        else:
            return "Поражение"

    def overtime(self):
        if self.maintime:
            return 'Да'
        else:
            return 'Нет'