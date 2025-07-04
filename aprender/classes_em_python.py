class Media:
    def __init__(self, *valores:int):
        """Aceita qualquer quantidade de valores"""
        self.valores = valores
    
    def media(self):
        if len(self.valores) == 0:
            return 0
        return sum(self.valores) / len(self.valores)
    
    def __str__(self):
        return f"{self.media()}"

print(Media(1,1,1,1,1))
print(Media(1,2,3,4,4))