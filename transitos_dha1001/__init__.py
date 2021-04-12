name = "transitos_dha1001"

#Importar todos los modulos de reduccion.
from .reduccion.master_bias import crear_masterbias
from .reduccion.master_dark import crear_masterdark
from .reduccion.master_dark import crear_masterflat
from .reduccion.science import reducir_imagenes_ciencia
