import numpy as np
import re

import astropy.units as u
from astropy.time import Time

from astropy.io import fits
from astropy.stats import sigma_clipped_stats

def curva_de_luz(imagenes, x_fuente, y_fuente, directorio_imagenes_reducidas="imagenes_reducidas", directorio_fotometria="fotometria"):
    """
    Es rutina toma todas las mediciones de la fotometría y genera la curva de luz para un objeto en cuestión, usando todo el resto de los objetos como referencia para calibrar las magnitudes.

    Parametros
    ----------

    imagenes: lista
        lista de imagenes a incluir en la curva de luz.

    x_fuente: float
        Posición en x de la fuente para la que se medirá la curva de luz.

    y_fuente: float
        Posición en y de la fuente para la que se medirá la curva de luz.

    directorio_imagenes_reducidas: str, opcional
        Directorio donde se encuentra la imagen.

    directorio_fotometria: string, opcional
        Directorio donde se encuentran los archivos de la fotometría.

    """

    target_mag = []
    target_mag_err = []
    mjd = []

    for k, imagen in enumerate(imagenes):

        #Definir el nombre del archivo que guardará la fotometría.
        phot_fname = re.sub(".fits",".phot.dat",imagen)
        try:
            #Tratar de leer el archivo con la fotometría. Si no existe, se levantará la excepción OSError y se procederá a hacer el cálculo. Si existe, leer y entregar los valores correspondientes.
            phot_data = np.loadtxt("{}/{}".format(directorio_fotometria, phot_fname))
            h = fits.open("{}/{}".format(directorio_imagenes_reducidas, imagen))
            mag_all = -2.5*np.log10(phot_data[:,0]/h[0].header['EXPTIME'])
            mag_err_all = (2.5/np.log(10.)) * phot_data[:,1]/phot_data[:,0]
        except OSError:
            print("Se debe calcular la fotometria primero.")
            return [None]*3

        #Nombre donde estarían guardadas las posiciones recentradas.
        pos_fname = re.sub(".fits",".pos.dat",imagen)
        try:
            #Tratar de leer el archivo. Si el archivo no existe, se levantará la excepción OSError, que llevará a calcular las posiciones.
            pos_data = np.loadtxt("{}/{}".format(directorio_fotometria,pos_fname))
            x = pos_data[:,0]
            y = pos_data[:,1]
            posiciones = np.vstack((x,y)).T
        except OSError:
            print("Se deben calcular las posiciones primero.")
            return [None]*3


        #Si es la primera imagen, guardar las magnitudes como referencias.
        if k==0:
            mag_ref = mag_all

        #Encontrar cual es la fuente que queremos medir.
        d2 = (posiciones[:,0]-x_fuente)**2 + (posiciones[:,1]-y_fuente)**2
        imin = np.argmin(d2)

        #Cacular la normalización
        cond = np.arange(0,len(phot))!=kmin
        norm, norm_median, norm_std = sigma_clipped_stats(mag_ref[cond]-mag_all[cond])
        #print(norm, norm_median, norm_std)
        target_mag.append(mag_all[kmin]+norm)
        target_mag_err.append(mag_err_all[kmin])

        #Guardar el dia Juliano modificado de las observaciones.
        t = Time(h[0].header['DATE-OBS'], format='isot', scale='utc') + 4.0*u.hr
        mjd.append(t.mjd)

    return mjd, target_mag, target_mag_err
