import numpy as np
import re

import astropy.units as u
from astropy.time import Time

from astropy.io import fits
from astropy.stats import sigma_clipped_stats, SigmaClip

from photutils import CircularAperture, CircularAnnulus, aperture_photometry
from photutils import Background2D, SExtractorBackground

pix_scale = 0.6 # Escala de un pixel en segundos de arco.
fwhm_pix  = 1./pix_scale #Seeing fue aproximadamente 1".

def medir_fotometria(imagen, r_ap, r_an_in=None, r_an_out=None, directorio_imagenes_reducidas="imagenes_reducidas", directorio_fotometria="fotometria", bkg_type='global', RON=15.0, GAIN=1.33, recalcular=False):
    """
    Rutina para medir fotometría de apertura de las fuentes en una imagen ubicadas en ciertas posiciones.

    Parametros
    ----------

    imagen: str
        Imagen en la que se medirá la fotometría.

    r_ap: float
        Radio de la apertura en segundos de arco.

    r_an_in: float, opcional
        Radio interior del anillo para calcular la contribución del cielo. Solo es usado si bkg_type es "local".

    r_an_out: float, opcional
        Radio exterior del anillo para calcular la contribución del cielo. Solo es usado si bkg_type es "local".

    directorio_imagenes_reducidas: str, opcional
        Directorio donde se encuentra la imagen.

    directorio_fotometria: str, opcional
        Directorio donde se encuentran, o donde se guardarán, los cálculos de la fotomería.

    bkg_type: float, opcional
        Debe ser igual a "global" para hacer una estimación global del cielo, o "local" para hacerlo local a cada aperture usando un anillo. Si se usa local, se debe también definir r_an_in y r_an_out.

    recalcular: boolean, opcional
        Debe ser True para recalcular la fotometría y la imagen de fondo (si bkg_type=global) si es que ya han sido calculadas con anterioridad.

    """

    #Definir el nombre del archivo que guardará la fotometría.
    phot_fname = re.sub(".fits?",".phot.dat",imagen)
    try:
        #Si se pide recalcular la fotometria, forzar la excepción.
        if recalcular:
            raise OSError

        #Tratar de leer el archivo con la fotometría. Si no existe, se levantará la excepción OSError y se procederá a hacer el cálculo. Si existe, leer y entregar los valores correspondientes.
        phot_data = np.loadtxt("{}/{}".format(directorio_fotometria, phot_fname))
        return phot_data[:,0], phot_data[:,1]

    except OSError:
        pass

    #Nombre donde estarían guardadas las posiciones recentradas.
    pos_fname = re.sub(".fits?",".pos.dat",imagen)
    try:
        #Tratar de leer el archivo. Si el archivo no existe, se levantará la excepción OSError, que llevará a calcular las posiciones.
        pos_data = np.loadtxt("{}/{}".format(directorio_fotometria,pos_fname))
        x = pos_data[:,0]
        y = pos_data[:,1]
        posiciones = np.vstack((x,y)).T
    except OSError:
        print("Se deben calcular las posiciones primero.")
        return None, None

    #Transformar la apertura y anillo a escala de pixeles y crear las aperturas.
    r_ap_use     = r_ap/pix_scale
    aps   = CircularAperture(posiciones, r=r_ap_use)
    if bkg_type=='local':
        r_an_in_use  = r_an_in/pix_scale
        r_an_out_use = r_an_out/pix_scale
        anns  = CircularAnnulus(posiciones, r_in=r_an_in_use, r_out=r_an_out_use)

    #Abrir la imagen y medir la fotometría en las aperturas.
    h = fits.open("{}/{}".format(directorio_imagenes_reducidas, imagen))

    #Calcular la fotometria de apertura.
    phot_table = aperture_photometry(h[0].data*GAIN, [aps])

    #Sustraer el cielo y calcular los errores.
    if bkg_type=='global':

        #Si es global, lo primero es calcular la imagen del fondo.
        bname = re.sub(".fits?",".bkg.fits",imagen)
        bkg = _global_back(h, bname, directorio_imagenes_reducidas, recalcular=recalcular)

        #Calcular la fotometria de apertura pero en la imagen de fondo ahora.
        bkg_table = aperture_photometry(bkg.background*GAIN, [aps])

        #Ahora sustraemos la contribución del fondo y determinamos los errores.
        suma_final = phot_table['aperture_sum_0'] - bkg_table['aperture_sum_0']
        error_final = ( phot_table['aperture_sum_0'] + bkg_table['aperture_sum_0'] )**0.5

    elif bkg_type=='local':

        #Si es local, entonces calcular la contribución de los anillos.
        bkg_mean, bkg_sig = _local_back(h, anns, posiciones)

        #Sustraer la contribución del fondo.
        bkg_sum = bkg_mean * aps.area
        suma_final  = phot_table['aperture_sum_0'] - bkg_sum
        error_final = ( phot_table['aperture_sum_0'] + bkg_sig**2 * (aps.area)**2 )**0.5

    #Guardar la fotometria.
    np.savetxt("{}/{}".format(directorio_fotometria, phot_fname), np.array([suma_final, error_final]).T)

    #Retornar la fotometria.
    return suma_final, error_final


def _global_back(h, bname, data_folder, recalcular=False):
    sigma_clip = SigmaClip(sigma=3.)
    bkg_estimator = SExtractorBackground()
    bkg = Background2D(h[0].data, (50, 50), filter_size=(3, 3), sigma_clip=sigma_clip, bkg_estimator=bkg_estimator)
    try:
        if recalcular:
            raise FileNotFoundError
        bkg_image = fits.open("{0:s}/{1:s}".format(data_folder, bname))
        bkg.background = bkg_image[0].data
    except FileNotFoundError:
        bkg = Background2D(h[0].data, (50, 50), filter_size=(3, 3), sigma_clip=sigma_clip, bkg_estimator=bkg_estimator)
        fits.writeto("{0:s}/{1:s}".format(data_folder, bname), bkg.background, overwrite=True)
    return bkg

def _local_back(h, anns, posiciones):
    annulus_masks = anns.to_mask(method='center')
    bkg_mean = np.zeros(len(posiciones))
    bkg_sig  = np.zeros(len(posiciones))
    for k, ann_mask in enumerate(annulus_masks):
        ann_data = ann_mask.multiply(h[0].data)
        ann_data_1d = ann_data[ann_data>0]
        bkg_mean[k], bkg_median, bkg_sig[k] = sigma_clipped_stats(ann_data_1d)
    return bkg_mean, bkg_sig
