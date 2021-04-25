import matplotlib.pyplot as plt
from astropy.visualization import ZScaleInterval, ImageNormalize
from astropy.io import fits

def desplegar_imagen(imagen, cmin=None, cmax=None, titulo=None):

    #Crear la figura.
    fig = plt.figure(figsize=(10,10))
    ax = fig.add_subplot(1, 1, 1)

    #Abrir la imagen.
    h = fits.open(imagen)

    #Definir la normalización.
    norm = ImageNormalize(h[0].data, interval=ZScaleInterval())

    #Graficar la figura.
    im = ax.imshow(h[0].data, origin='lower', norm=norm, cmap='gray')

    #Desplegar el titulo si se indicó uno.
    if titulo is not None:
        ax.set_title(titulo, fontsize=16)

    #Poner los limites de profundidad si se han declarado.
    if cmin is not None and cmax is not None:
        im.set_clim(cmin, cmax)

    #Desplegar la barra de colores.
    fig.colorbar(im)

    return
