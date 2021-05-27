import numpy as np
import re
import matplotlib.pyplot as plt

import astropy.units as u
from astropy.time import Time

from astropy.io import fits
from astropy.stats import sigma_clipped_stats

from scipy.signal import savgol_filter

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

    mjd = list()
    for k, imagen in enumerate(imagenes):
        phot_fname = re.sub(".fits?",".phot.dat",imagen)
        pos_fname = re.sub(".fits?",".pos.dat",imagen)

        h = fits.open("{}/{}".format(directorio_imagenes_reducidas, imagen))

        t = Time(h[0].header['DATE-OBS'], format='isot', scale='utc') + 4.0*u.hr
        mjd.append(t.mjd)

        phot_data = np.loadtxt("{}/{}".format(directorio_fotometria, phot_fname))
        if k==0:
            mag_all     = np.zeros((len(imagenes), len(phot_data[:,0])))
            mag_err_all = np.zeros(mag_all.shape)
        mag_all[k] = -2.5*np.log10(phot_data[:,0]/h[0].header['EXPTIME'])
        mag_err_all[k] = (2.5/np.log(10.)) * phot_data[:,1]/phot_data[:,0]

        if k==0:
            pos_data = np.loadtxt("{}/{}".format(directorio_fotometria,pos_fname))
            x = pos_data[:,0]
            y = pos_data[:,1]
            posiciones = np.vstack((x,y)).T

    mag_smoothed = savgol_filter(mag_all, 7, 5, axis=0)

    d2 = (posiciones[:,0]-x_fuente)**2 + (posiciones[:,1]-y_fuente)**2
    imin = np.argmin(d2)

    cond = np.arange(0,mag_all.shape[1])!=imin

    mag_ref = np.tile(mag_smoothed[0,cond], (mag_all.shape[0],1))

    norm, norm_median, norm_std = sigma_clipped_stats(mag_ref-mag_smoothed[:,cond], axis=1)
    #print(norm, norm_median, norm_std)
    target_mag = mag_all[:,imin]+norm
    target_mag_err = mag_err_all[:,imin]

    return mjd, target_mag, target_mag_err


###

def graficar_curva_de_luz(mjd, mag, mag_err, titulo=None):

    #Crear figura.
    fig = plt.figure(figsize=(10,6))
    ax = fig.add_subplot(1, 1, 1)

    #Graficar datos.
    ax.errorbar((mjd-mjd[0])*24., mag, yerr=mag_err, fmt='bo')

    #Invertir el eje y para que los puntos más brillantes este más arriba.
    ymin, ymax = plt.ylim()
    ax.set_ylim([ymax, ymin])

    #Desplegar titulos si fue indicado.
    if titulo is not None:
        ax.set_title(titulo, fontsize=14)

    #Poner nombres de los ejes.
    ax.set_xlabel("MJD - {0:.3f} (hours)".format(mjd[0]), fontsize=14)
    ax.set_ylabel("Magnitud Instrumental", fontsize=14)

    return
