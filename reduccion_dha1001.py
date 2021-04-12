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


def crear_masterdark(imagenes, nombre_dark="MasterDark.fits",
                     nombre_bias="MasterBias.fits",
                     directorio_entrada="raw", directorio_salida="red"):
    """
    Rutina para crear el Master Dark. Esta rutina usa las imagenes de dark, después de sustraer el bias, tomadas por la camara del telescopio MAS de 50cm en El Sauce y genera el cuadro de dark que vamos a usar en la reducción de las otras imágenes.

    Parámetros
    ----------

    imagenes: lista
        Lista de las imagenes que vamos a combinar.

    nombre_dark: string, opcional
        Nombre de la imagen de salida que va a tener el cuadro de dark combinado.

    nombre_bias: string, opcional
        Nombre de la imagen de salida que va a tener el cuadro de bias combinado.

    directorio_entrada: string, opcional
        Directorio donde están las imágenes tomadas por el telescopio.

    directorio_salida: string, opcional
        Directorio donde vamos a guardar las imagenes reducidas.

    """

    #Abrir el bias.
    if nombre_bias is not None:
        master_bias = fits.open("{}/{}".format(directorio_salida,nombre_bias))

    #Lista donde vamos a guardar los arrays de todas las imágenes.
    all_darks = []

    #Leemos todas las imagenes de darks.
    for imagen in imagenes:
        fname = "{}/{}".format(directorio_entrada, imagen)
        h = fits.open(fname)

        #Sustraemos el bias.
        h[0].data = np.float64(h[0].data)
        if nombre_bias is not None:
            h[0].data -= master_bias[0].data

        all_darks.append(h[0].data)
        h.close()

    #Combinamos las imagenes de dark. Específicamente, tomamos la mediana en cada pixel.
    master_dark = np.median(all_darks, axis=0)

    #Guardamos la imagen combinada.
    subprocess.call(["mkdir",directorio_salida], stderr=subprocess.DEVNULL)
    fits.writeto("{}/{}".format(directorio_salida, nombre_dark), master_dark, overwrite=True)

    return
