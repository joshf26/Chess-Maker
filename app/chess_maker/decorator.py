class Decorator:
    name = ''
    image = ''

    def __hash__(self):
        return hash((self.name, self.image))
