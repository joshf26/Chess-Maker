from decorator import Decorator
from pack_util import load_image


class Wall(Decorator):
    name = 'Wall'
    image = load_image('standard', 'images/wall.svg')
