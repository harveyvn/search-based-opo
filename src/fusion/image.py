class Image:
    def __init__(self, data):
        self.data = data
        self.case = data["name"]
        self.roads = data["roads"]
        self.vehicles = data["vehicles"]
        self.degree = data["rot_deg"]
