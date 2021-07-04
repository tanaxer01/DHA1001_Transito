import matplotlib.pyplot as plt
import matplotlib.pyplot as plt
from astropy.visualization import ZScaleInterval, ImageNormalize
from astropy.io import fits


def agregar_imagen(figura, imagen, cmin=None, cmax=None, titulo=None):
    ''' Igual que desplegar_imagen pero la agrega a una figura existente    '''

    #Abrir la imagen.
    h = fits.open(imagen)

    #Definir la normalización.
    norm = ImageNormalize(h[0].data, interval=ZScaleInterval())

    #Graficar la figura.
    im = figura.imshow(h[0].data, origin='lower', norm=norm, cmap='gray')

    #Desplegar el titulo si se indicó uno.
    if titulo is not None:
        figura.set_title(titulo, fontsize=16)

    #Poner los limites de profundidad si se han declarado.
    if cmin is not None and cmax is not None:
        im.set_clim(cmin, cmax)
