import numpy as np
from astropy.io import fits
import subprocess


def crear_masterbias(imagenes, nombre_bias="MasterBias.fits",
                    directorio_entrada="raw", directorio_salida="red"):
    """
    Rutina para crear el Master Bias. Esta rutina combina las imagenes de bias tomadas por la camara del telescopio MAS de 50cm en El Sauce y genera el cuadro de bias que vamos a usar en la reducción de las otras imágenes.

    Parámetros
    ----------

    imagenes: lista
        Lista de las imagenes que vamos a combinar.

    nombre_bias: string, opcional
        Nombre de la imagen de salida que va a tener el cuadro de bias combinado.

    directorio_entrada: string, opcional
        Directorio donde están las imágenes tomadas por el telescopio.

    directorio_salida: string, opcional
        Directorio donde vamos a guardar las imagenes reducidas.

    """

    #Lista donde vamos a guardar los arrays de todas las imágenes.
    all_biases = []

    #Leemos todas las imagenes de bias.
    for imagen in imagenes:
        fname = "{}/{}".format(directorio_entrada, imagen)
        h = fits.open(fname)
        all_biases.append(h[0].data)
        h.close()

    #Combinamos las imagenes de bias. Específicamente, tomamos la mediana en cada pixel.
    master_bias = np.median(all_biases, axis=0)

    #Guardamos la imagen combinada.
    subprocess.call(["mkdir",directorio_salida], stderr=subprocess.DEVNULL)
    fits.writeto("{}/{}".format(directorio_salida, nombre_bias), master_bias, overwrite=True)

    return
