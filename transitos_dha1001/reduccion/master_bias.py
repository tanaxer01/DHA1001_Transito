import numpy as np
from astropy.io import fits
import subprocess


def crear_masterbias(imagenes, nombre_bias="MasterBias.fits",
                    directorio_imagenes_originales="raw", directorio_imagenes_reducidas="red", recalcular=False):
    """
    Rutina para crear el Master Bias. Esta rutina combina las imagenes de bias tomadas por la camara del telescopio MAS de 50cm en El Sauce y genera el cuadro de bias que vamos a usar en la reducción de las otras imágenes.

    Parámetros
    ----------

    imagenes: lista
        Lista de las imagenes que vamos a combinar.

    nombre_bias: string, opcional
        Nombre de la imagen de salida que va a tener el cuadro de bias combinado.

    directorio_imagenes_originales: string, opcional
        Directorio donde están las imágenes tomadas por el telescopio.

    directorio_imagenes_reducidas: string, opcional
        Directorio donde vamos a guardar las imagenes reducidas.

    recalcular: boolean, opcional
        Debe ser True para que la imagen sea recalculada si ya existe.

    """

    #Tratemos de abrir la imagen. Si no existe, o si se ha pedido recalcularla, proseguir con la combinación.
    try:
        if recalcular:
            raise FileNotFoundError
        master_bias = fits.open("{}/{}".format(directorio_imagenes_reducidas, nombre_bias))
        master_bias.close()
        return
    except FileNotFoundError:
        pass

    #Lista donde vamos a guardar los arrays de todas las imágenes.
    all_biases = []

    #Leemos todas las imagenes de bias.
    for imagen in imagenes:
        fname = "{}/{}".format(directorio_imagenes_originales, imagen)
        h = fits.open(fname)
        all_biases.append(h[0].data)
        h.close()

    #Combinamos las imagenes de bias. Específicamente, tomamos la mediana en cada pixel.
    master_bias = np.median(all_biases, axis=0)

    #Guardamos la imagen combinada.
    subprocess.call(["mkdir",directorio_imagenes_reducidas], stderr=subprocess.DEVNULL)
    fits.writeto("{}/{}".format(directorio_imagenes_reducidas, nombre_bias), master_bias, overwrite=True)

    return
