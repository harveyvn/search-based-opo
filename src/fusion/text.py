class Text:
    def __init__(self, data):
        self.data = data
        self.case = data["case"]
        self.roads = data["roads"]
        self.weather = data["environment"]
        try:
            self.vehicles = data["vehicles"]
        except Exception as e:
            print(f'Exception: Vehicle not found for case {data["case"]}!')
