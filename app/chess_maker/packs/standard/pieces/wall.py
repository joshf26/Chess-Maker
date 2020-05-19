from piece import Piece, load_image


class Wall(Piece):
    name = 'Wall'
    image = load_image('standard', 'images/wall.svg')
