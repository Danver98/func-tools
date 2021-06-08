from match import Match
class HockeyMatch(Match):
    def __init__(self,date,team,rival,self_score,rival_score,place):
        self.self_total , self.rival_total = 0 , 0
        maintime = None
        length = len(self_score)
        self.periods = [int(period) for period in self_score]
        self.rival_periods = [int(period) for period in rival_score]
        for i in range(length):
            self.self_total+=int(self_score[i])
            self.rival_total+=int(rival_score[i])
        #for score in self_score:
            #self_total+=int(score)
        #for score in rival_score:
            #rival_total+=int(score)
        if length > 3:
            self_maintime = int(self_score[0]) + int(self_score[1]) + int(self_score[2]) 
            rival_maintime = int(rival_score[0]) + int(rival_score[1]) + int(rival_score[2])
            maintime = {'home-score':self_maintime, 'guest-score': rival_maintime}     
        self_total , rival_total = self.self_total , self.rival_total
        Match.__init__(self,date,team,rival,self_total,rival_total,place, maintime)

    def period_odd_even(self,period):
        return "Чёт" if (self.periods[period - 1] + self.rival_periods[period - 1]) % 2 ==0 else "Нечет"
    
    def period_total(self,period):
        return self.periods[period -1] + self.rival_periods[period-1]

    def ind_period_odd_even(self,period):
        return "Чёт" if self.periods[period - 1] % 2 == 0 else "Нечет"
    