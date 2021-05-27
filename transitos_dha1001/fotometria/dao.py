import numpy as np
import re

from astropy.io import fits
from astropy.stats import sigma_clipped_stats

from photutils import DAOStarFinder, centroid_sources, centroid_com

import subprocess

def dao_busqueda(imagen, directorio_imagenes_reducidas="imagenes_reducidas", directorio_fotometria="fot", recalcular=True):
    """
    Función que busca fuentes (estrellas) en una imagen.

    Parametros
    ----------

    imagen: str
        Nombre del archivo que contiene la imagen en la que se hará la búsqueda.

    directorio_imagenes_reducidas: string, opcional
        Nombre del directorio donde se encuentran la imagen en que se hará la búsqueda.

    directorio_fotometria: string, opcional
        Nombre del directorio donde se guardarán los datos fotométricos.

    recalcular: boolean, opcional
        Debe ser igual a True si se desea recalcular las posiciones.

    """

    #Crear el directorio de la fotometria si no existe.
    subprocess.call(["mkdir",directorio_fotometria], stderr=subprocess.DEVNULL)

    #Determinar el nombre del archivo con las posiciones.
    pos_fname = re.sub(".fits?",".pos.dat",imagen)
    try:
        #Si se ha pedido recalcular, avanzar inmediatamente a la excepción.
        if recalcular:
            raise OSError

        #Tratar de leer el archivo. Si el archivo no existe, se levantará la excepción OSError, que llevará a calcular las posiciones.
        pos_data = np.loadtxt("{}/{}".format(directorio_fotometria,pos_fname))
        x = pos_data[:,0]
        y = pos_data[:,1]

    except OSError:

        print("Buscando fuentes en la imagen ",imagen)

        #Abrir la imagen.
        h = fits.open("{}/{}".format(directorio_imagenes_reducidas, imagen))

        #Calcular la mediana y desviación estándar haciendo reyección de 3 sigma para solo contabilizar el cielo.
        mean, median, std = sigma_clipped_stats(h[0].data, sigma=3.0)

        #Buscar las fuentes. Su brillo debe estar 20 veces sobre el ruido del cielo.
        daofind = DAOStarFinder(fwhm=3.0, threshold=20.*std)
        fuentes = daofind(h[0].data - median)
        x = fuentes['xcentroid']
        y = fuentes['ycentroid']
        h.close()

        #Solo vamos a querer fuentes lejos de los bordes.
        cond = (x>150) & (x<1850) & (y>150) & (y<1850)
        x = x[cond]
        y = y[cond]

        #Guardar las posiciones en el archivo correspondiente.
        np.savetxt("{}/{}".format(directorio_fotometria, pos_fname), np.array([x,y]).T)

    #Poner todas las posiciones en un solo arreglo y devolverlo.
    posiciones = np.vstack((x,y)).T
    return posiciones


def dao_recentrar(imagen, posiciones_referencia, directorio_imagenes_reducidas="imagenes_reducidas", directorio_fotometria="fot", caja_busqueda=21, recalcular=True):
    """
    Rutina para recentrar un set de posiciones de referencia. Estas posiciones de referencia deben haber sido calculadas con la función dao_busqueda.

    Parametros
    ----------

    imagen: str
        Nombre del archivo que contiene la imagen en la que se centrarán las fuentes.

    posiciones_referencia: numpy array
        Arreglo con las posiciones de las fuentes en la imagen de referencia. Debe ser generado por la función dao_busqueda.

    directorio_imagenes_reducidas: string, opcional
        Nombre del directorio donde se encuentran la imagen en que se hará la búsqueda.

    directorio_fotometria: string, opcional
        Nombre del directorio donde se guardarán los datos fotométricos.

    caja_busqeda: int, opcional
        Tamaño de la caja de búsqueda de las fuentes.

    recalcular: boolean, opcional
        Debe ser igual a True si se desea recalcular las posiciones.

    """

    print("Recentrando fuentes en la imagen",imagen)

    #Nombre donde estarían guardadas las posiciones recentradas.
    pos_fname = re.sub(".fits?",".pos.dat",imagen)

    try:
        #Si se ha pedido recalcular, avanzar inmediatamente a la excepción.
        if recalcular:
            raise OSError

        #Tratar de leer el archivo. Si el archivo no existe, se levantará la excepción OSError, que llevará a calcular las posiciones.
        pos_data = np.loadtxt("{}/{}".format(directorio_fotometria,pos_fname))
        x = pos_data[:,0]
        y = pos_data[:,1]

    except OSError:

        #Abrir la image,
        h = fits.open("{0:s}/{1:s}".format(directorio_imagenes_reducidas, imagen))

        #Tomar las posiciones de referencia y recentrar las fuentes alrededor de estas posiciones tomando una caja de tamaño caja_busqueda.
        x_ref = np.copy(posiciones_referencia[:,0])
        y_ref = np.copy(posiciones_referencia[:,1])
        x, y = centroid_sources(h[0].data, x_ref, y_ref, box_size=caja_busqueda, centroid_func=centroid_com)
        h.close()

        #Guardar las posiciones en el archivo correspondiente.
        np.savetxt("{}/{}".format(directorio_fotometria, pos_fname), np.array([x,y]).T)

    #Poner las posiciones en un solo arreglo y devolver el arreglo.
    posiciones = np.vstack((x,y)).T
    return posiciones

def filtrar_posiciones(imagen, zonas_a_filtrar,
                       radio_de_filtro=10,
                       directorio_fotometria="fot"):

    """
    Rutina par filtrar fuentes en zonas problematicas de la imagen de referencia usando sus coordenadas.

    Parametros
    ----------

    imagen: str
        Imagen que se usará como referencia para las posiciones.

    zonas_a_filtrar: lista de dos dimensiones, float
        Posiciones alrededor de las cuales se quieren eliminar fuentes detectadas.

    radio_de_filtro: float o lista, opcional
        Radio, en pixeles, de la zona de eliminación alrededor de las zonas_a_filtrar. Si es un escalar, se usará el mismo valor para todas las zonas. Si es una lista, debe ser del mismo largo que las zonas_a_filtrar. Valor predeterminado es 10 pixeles.

    directorio_fotometria: str, opcional
        Directorio donde se guardan los archivos relacionados a la fotometría.

    """

    #Partir por leer las posiciones.
    archivo_posiciones = re.sub(".fits?", ".pos.dat", imagen)
    posiciones_referencia = np.loadtxt("{}/{}".format(directorio_fotometria, archivo_posiciones))

    #Poner las posiciones a filtrar en formato de arreglos de numpy.
    zonas_a_filtrar = np.array(zonas_a_filtrar)
    x_bad = zonas_a_filtrar[:,0]
    y_bad = zonas_a_filtrar[:,1]

    #El radio de eliminación puede ser distinto para cada zona de eliminación o la misma para todas.
    if np.isscalar(radio_de_filtro):
        r_bad = radio_de_filtro * np.ones(len(x_bad))
    else:
        r_bad = np.array(radio_de_filtro)

    #Pasar por todas las zonas a filtrar, y crear una condición para luego filtrar el arreglo.
    for k in range(len(x_bad)):
        dx = (posiciones_referencia[:,0]-x_bad[k])
        dy = (posiciones_referencia[:,1]-y_bad[k])
        d  = (dx**2+dy**2)**0.5
        if k==0:
            cond = (d>r_bad[k])
        else:
            cond = cond & (d>r_bad[k])
        posiciones_referencia = posiciones_referencia[cond]

    #Guardar las posiciones filtradas.
    np.savetxt("{}/{}".format(directorio_fotometria, archivo_posiciones), posiciones_referencia)

    return
