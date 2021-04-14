import numpy as np
from astropy.io import fits
from astroscrappy import detect_cosmics

def reducir_imagenes_ciencia(imagenes, prefijo="ciencia",
                     reyeccion_rayos_cosmicos=True,
                     nombre_flat="MasterFlat.fits",
                     nombre_dark="MasterDark.fits",
                     nombre_bias="MasterBias.fits",
                     directorio_imagenes_originales="raw", directorio_imagenes_reducidas="red"):
    """
    Rutina para reducir las imagenes de ciencia. Esta rutina sustrae el bias y dark, y corrige las diferencias de sensibilidad entre pixeles usando el flat en imagenes tomadas por la camara del telescopio MAS de 50cm en El Sauce.

    Parámetros
    ----------

    imagenes: lista
        Lista de las imagenes que vamos a combinar.

    prefijo: string, opcional
        Prefijo que se le antepondrá al prefijo de la imagen para indicar que ha sido reducida.

    reyeccion_rayos_cosmicos: boolean, opcional
        True si se desea remover los rayos cósmicos.

    nombre_flat: string, opcional
        Nombre de la imagen que tiene el cuadro de Flat combinado.

    nombre_dark: string, opcional
        Nombre de la imagen que tiene el cuadro de dark combinado.

    nombre_bias: string, opcional
        Nombre de la imagen que tiene el cuadro de bias combinado.

    directorio_imagenes_originales: string, opcional
        Directorio donde están las imágenes tomadas por el telescopio.

    directorio_imagenes_reducidas: string, opcional
        Directorio donde vamos a guardar las imagenes reducidas.

    """

    #Abrir el master dark y el master bias.
    if nombre_bias is not None:
        master_bias = fits.open("{}/{}".format(directorio_imagenes_reducidas, nombre_bias))
    if nombre_dark is not None:
        master_dark = fits.open("{}/{}".format(directorio_imagenes_reducidas, nombre_dark))
    if nombre_flat is not None:
        master_flat = fits.open("{}/{}".format(directorio_imagenes_reducidas, nombre_flat))


    #Pasar por cada imagen removiendo bias y dark, corrigiendo por el flat, y removiendo los rayos cósmicos.
    for imagen in imagenes:

        #Abrir la imagen.
        fname = "{}/{}".format(directorio_imagenes_originales, imagen)
        h = fits.open(fname)

        #Sustraer el bias y el dark, y corregir por el flat.
        h[0].data = np.float64(h[0].data)
        if nombre_bias is not None:
            h[0].data -= master_bias[0].data
        if nombre_dark is not None:
            h[0].data -= master_dark[0].data
        if nombre_flat is not None:
            h[0].data /= master_flat[0].data

        #Limpiar los rayos cosmicos.
        if reyeccion_rayos_cosmicos:
            crmask, clean_image = detect_cosmics(h[0].data)
            h[0].data = clean_image

        #Guardar la imagen reducida.
        h[0].writeto("{}/{}_{}".format(directorio_imagenes_reducidas, prefijo, imagen), overwrite=True)
