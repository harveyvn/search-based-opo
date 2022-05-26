class Road:
    def __init__(self, img_road, txt_road):
        self.img_left = img_road["left"]
        # self.right = img_road["right"]
        # self.center = img_road["center"]
        # self.marks = img_road["marks"]
        self.limit = txt_road["speed_limit"]
        self.material = txt_road["road_material"]
        self.text_id = txt_road["road_ID"]
        self.text_nav = txt_road["road_navigation"]

    def __str__(self):
        return str(self.__class__) + ": " + str(self.__dict__)