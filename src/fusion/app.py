import json
import operator
from .image import Image
from .text import Text
from .road import Road
from src.libraries.common import get_direction_of


class DataFusion:
    def __init__(self, image_dir: str, text_dir: str):
        self.image = Image(self.load(image_dir))
        self.text = Text(self.load(text_dir))

    @staticmethod
    def load(dir):
        # Opening JSON file & returns JSON object as a dictionary
        f = open(dir)
        return json.load(f)

    def create_roads(self):
        roads = []
        img_roads = self.image.roads
        txt_roads = self.text.roads

        print(f'Num Img Roads: {len(img_roads)}')
        print(f'Num Txt Roads: {len(txt_roads)}')

        if len(img_roads) == len(txt_roads) == 1:
            print('This is Single Road Case!')
            img_road, txt_road = img_roads[0], txt_roads[0]

            # Extract number of lanes
            lane_num_img = len(img_road["marks"]) + 1
            lane_num_txt = txt_road["lane_num"]
            print(f'Num Img Lanes: {lane_num_img}')
            print(f'Num Txt Lanes: {lane_num_txt}')
            if lane_num_img == lane_num_txt:
                print(f'Both roads have a same number of lanes ({lane_num_txt})')

            # Extract road points from images and road properties from text
            road = Road(img_road, txt_road)
            roads.append(road)
        else:
            print("This is Multi Road Case!")
            print(f'Based on images, at least {len(img_roads)} pairs of segments!')

            PAIRS = []

            for i, img_road in enumerate(img_roads):
                # 1st cond is direction
                a1 = get_direction_of([(p[0], p[1]) for p in img_road["center"]["points"]], int(self.image.degree))
                # 2nd cond is number of lane
                b1 = len(img_road["marks"]) + 1
                # Local pairs
                local_pairs = {}
                for l, txt_road in enumerate(txt_roads):
                    a2 = [char for char in txt_road["road_navigation"]]
                    # 2-way => 2
                    b21 = int(txt_road["road_direction"].split('-')[0])
                    b22 = int(txt_road["lane_num"])

                    points = 0
                    tmp_point = 0

                    if set(a2).issubset(a1):
                        points += 1
                        tmp_point = 1
                    print(f'Compare {a2} and {a1}: +{tmp_point}')

                    if b21 == b1:
                        points += 1
                        tmp_point = 1
                    else:
                        tmp_point = 0
                    print(f'Compare {b21} and {b1}: +{tmp_point}')

                    if b22 == b1:
                        points += 1
                        tmp_point = 1
                    else:
                        tmp_point = 0
                    print(f'Compare {b22} and {b1}: +{tmp_point}')

                    matched = points / 3 * 100
                    print(f'Seg img-{i}, txt-{l}: {points} points and {matched}% matched!\n')
                    local_pairs[(i, l)] = matched

                local_pairs = dict(sorted(local_pairs.items(), key=operator.itemgetter(1), reverse=True))
                print(f'Local Pairs: {local_pairs}')
                print('\n====\n')

                PAIRS.append(list(local_pairs.keys())[0])

            for i, k in enumerate(PAIRS):
                road = Road(img_roads[k[0]], txt_roads[k[1]])
                print(road)
                print("==")
                roads.append(road)

        return roads
