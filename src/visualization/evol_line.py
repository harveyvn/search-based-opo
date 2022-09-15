class EvolLine:
    def __init__(self, short_name, family, name, metric, point, color, xs, ys):
        self.name = name
        self.short_name = short_name
        self.family = family
        self.metric = metric
        self.point = point
        self.color = color
        self.xs = xs
        self.ys = ys

    def get_label(self, use_family: bool = False, use_short: bool = False):
        if use_family:
            return f'{self.family} - {self.metric}: {str(round(self.point, 2))}'
        if use_short:
            return f'{self.short_name} - {self.metric}: {str(round(self.point, 2))}'
        return f'{self.name} - {self.metric}: {str(round(self.point, 2))}'
