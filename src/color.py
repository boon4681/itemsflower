from PIL import Image
from src.source import VersionPath

class ColorMap:
    def __init__(self,source:VersionPath) -> None:
        self.dist_colormap = {
            'grass': Image.open(source.colormap.joinpath('grass.png')).load(),
            'foliage': Image.open(source.colormap.joinpath('foliage.png')).load()
        }
    def get(self,colormap,temperature,humidity):
        downfall = humidity * temperature
        x = (int)((1 - temperature) * 255)
        y = (int)((1 - downfall) * 255)
        if(colormap in self.dist_colormap):
            r,g,b = self.dist_colormap[colormap][x,y][0:3]
            return to_hex((r << 16) + (g << 8) + b)
        return "ERROR - Incorrect value given."
    
def to_hex(decimal):
    r = (decimal >> 16 & 255)
    g = (decimal >> 8 & 255)
    b = (decimal & 255)
    return '%02x%02x%02x' % (r,g,b)