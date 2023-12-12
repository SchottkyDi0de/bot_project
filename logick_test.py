
class Test:
    def __init__(self, tanks_count, include_rating) -> None:
        self.tanks_count = tanks_count
        self.include_rating = include_rating
        self.blocks = 1
        self.small_blocks = 0
        
        if self.include_rating:
            self.blocks += 1
        
        if self.tanks_count >= 1:
            self.blocks += 1
            
        if self.tanks_count >= 2:
            self.blocks += 1
        
        if self.tanks_count >= 3:
            if self.include_rating:
                self.small_blocks = 2
                self.blocks -= 1
            else:
                self.blocks += 1
                
        if self.tanks_count >= 4:
            if not self.include_rating:
                self.small_blocks = 2
                self.blocks -= 1
    
    def show(self):
        return f'{self.blocks=} {self.small_blocks=}'
    
print(Test(4, False).show())