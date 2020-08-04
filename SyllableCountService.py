import syllapy

class SyllableCountService:
    def __init__(self):
        super().__init__()
    
    def syllableCount(self, article):
        count = 0
        for word in article:
            count += syllapy.count(word)
        return count