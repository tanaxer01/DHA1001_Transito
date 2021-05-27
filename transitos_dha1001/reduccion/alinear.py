import numpy as np
import astroalign as aa
from astropy.io import fits
import os
import re

def alinear_imagenes_ciencia(imagenes,
                    prefijo="ali",
                    directorio_imagenes_reducidas="red",
                    recalcular=True):

    """
    Rutina para alinear las imagenes de ciencia. La primera imagen de la lista siempre se va a usar como referencia para alinear el resto.

    Parametros
    ----------

    imagenes: lista
        Lista de imagenes de entrada que queremos alinear.

    prefijo: string, opcional
        Prefijo que se le antepondrá al prefijo de la imagen para indicar que ha sido alineada.

    directorio_imagenes_reducidas: string, opcional
        Directorio donde vamos a guardar las imagenes reducidas.

    recalcular: bool, opcional
        Si es True, se recalculará el alineamiento aún cuando una versión de la imagen alineada ya exista en el directorio de imagenes reducidas.

    """

    #La primera imagen será utilizada como la referencia, y el resto se va a linear para calzar con esta.
    referencia = fits.open("{}/{}".format(directorio_imagenes_reducidas, imagenes[0]))

    #Pasar por cada imagen alineandola a la de referencia. Si no se pide recalcular, y la imagen ya existe, saltarse el alineamiento.
    for imagen in imagenes_reducidas_ciencia:

        #Ver si la imagen alineada ya existe.
        imagen_salida = prefijo + "_" + imagen
        if not recalcular and os.path.exists("{}/{}".format(directorio_imagenes_reducidas, imagen_salida)):
            continue

        #Alinear la imagen.
        im = fits.open("{}/{}".format(directorio_imagenes_reducidas, imagen))
        im_alineada, footprint = aa.register(im[0].data, referencia[0].data)

        #Guardar la imagen alineada.
        im[0].data = im_alineada
        im.writeto("{}/{}".format(directorio_imagenes_reducidas, imagen_salida))
        im.close()
