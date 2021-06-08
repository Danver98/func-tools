from match import Match
class BasketballMatch(Match):
    def __init__(self,date,team,rival,self_score,rival_score,place):
        self_total , rival_total = 0 , 0
        length = len(self_score)
        maintime = None
        for sc in self_score:
            self_total+=int(sc)
        for sc in rival_score:
            rival_total+=int(sc)
        if length > 4:
            self_maintime = self_total - int(self_score[length - 1])
            rival_maintime = rival_total - int(rival_score[length - 1])
            maintime = {'home-score':self_maintime, 'guest-score': rival_maintime}
        Match.__init__(self,date,team,rival,self_total,rival_total,place, maintime)
        self.quarters = [int(quarter) for quarter in self_score]
        self.rival_quarters = [int(quarter) for quarter in rival_score]

    def quarter_odd_even(self,quarter):
        return "Чёт" if (self.quarters[quarter -1] + self.rival_quarters[quarter-1]) % 2 == 0 else "Нечет"
    
    def quarter_total(self,quarter):
        return self.quarters[quarter -1] + self.rival_quarters[quarter-1]

    def ind_quarter_odd_even(self,quarter):
        return "Чёт" if self.quarters[quarter - 1] % 2 == 0 else "Нечет"

    def half_total(self,half):
        if half ==1:
            return self.quarter_total(1) + self.quarter_total(2)
        elif half ==2:
            return self.quarter_total(3) + self.quarter_total(4)
        else:
            return -1
    
    def ind_half_total(self,half):
        if half ==1:
            return self.quarters[0] + self.quarters[1]
        elif half ==2:
            return self.quarters[2] + self.quarters[3]
        else:
            return -1

    def half_odd_even(self,half):
        return "Чёт" if (self.half_total(half)) % 2 == 0 else "Нечет"

    def ind_half_odd_even(self,half):
        return "Чёт" if (self.ind_half_total(half))% 2 == 0 else "Нечет"
    
    def first_greater_second(self):
        if self.half_total(1) > self.half_total(2):
            return "Да"
        elif self.half_total(1) < self.half_total(2):
            return "Нет"
        else:
            return "Одинаково"
    
    def ind_first_greater_second(self):
        if self.ind_half_total(1) > self.ind_half_total(2):
            return "Да"
        elif self.ind_half_total(1) < self.ind_half_total(2):
            return "Нет"
        else:
            return "Одинаково"
