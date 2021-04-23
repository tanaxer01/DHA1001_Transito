# Rutinas para el Análisis de Tránsitos para el curso DHA1001 *Sistema Solar y la Búsqueda de Otros Mundos*.

1. Baje e instale el software VirtualBox para su sistema operativo desde [este sitio](https://www.virtualbox.org/wiki/Downloads).

2. Baje y descomprima [este archivo](https://www.astro.udp.cl/~rjassef/DHA1001_2021/Maquina_Virtual.zip) que contiene la máquina virtual preparada en el formato de Virtual Box.  

3. Inicie la Máquina Virtual. Para esto, siga los siguientes pasos:

  * Abra el programa VirtualBox, que instaló en el punto 1.

  * Abra el menú *Machine* y elija la opción *Add*.

  * Busque la carpeta creada de la descompresión del archivo en el punto 2.

  * Elija el archivo **DHA1001-VirtualBox.vbox**.

  * Elija la máquina virtual en el menú de la izquierda y presione *Start*.

4. Una vez que se haya inicializado su máquina virtual Ubuntu, le ofecerá instalar actualizaciones. No lo haga, pues puede hacer que alguno de los programas necesarios deje de funcionar.

5. El siguiente paso es instalar las rutinas proveídas por este repositorio y descargar los datos para el ejemplo con el exoplaneta WASP-43b. Para ello, siga los siguientes pasos:

  * En el costado izquierdo superior verá 5 iconos ordenados verticalmente. Presione el icono inferior de estos para abrir un terminal.

  * Copie las rutinas de este repositorio usando el comando *git clone*. Para esto, ingrese el siguiente comando en la ventana del terminal que acaba de abrir:

    ```bash
    git clone https://github.com/rjassef/DHA1001_Transito
    ```

  * Sin cerrar el terminal, abra ahora una ventana de Firefox (icono superior de los 5 iconos en la parte superior izquiera) y vaya a [esta dirección](https://www.astro.udp.cl/~rjassef/DHA1001_2021) y descarge el archivo *wasp43_raw.zip*. Una vez terminado, usted puede cerrar Firefox.

    *Nota: para escribir en Ubuntu el caracter ~ en la dirección web anterior, debe presionar el botón ALT derecho y la letra ñ al mismo tiempo.*

  * El archivo quedó en el directorio *Descargas*. Presione el icono que está justo por debajo del icono de Firefox para acceder a los archivos de su máquina virtual.

    Vaya al directorio *Descargas*. Haga doble click en el archivo *wasp43_raw.zip* y luego presione la opción de extraer.

    En la ventana que se abrirá, elija *Carpeta personal* en el menú de la izquierda, y luego elija la carpeta *DHA1001_Transito*. Presione **Extraer** en la esquina superior derecha.

5. Finalmente, cierre todas las ventanas, excepto por el terminal que debería aún estar abierto. Para abrir el documento con el ejemplo de desarrollo y análisis de los datos del ejemplo con WASP-43, ingrese el siguiente comando:

  ```bash
  cd DHA1001_Transito
  jupyter lab
  ```
  Este comando abrirá una ventana de Firefox con el ambiente de trabajo de Jupyter Lab cargado.

  Haga doble click, en el costado izquierdo, sobre el archivo *Ejemplo WASP43.ipynb* para abrir el ejemplo.


6. Lea todo el ejemplo en detalle. Una vez que lo haya leído, limpie todos los resultados y ejecute usted todos los comandos.

  En la parte superior de la ventana, elija la opción *Kernel / Restart Kernel and Clear All Outputs*. Seleccione *Restart*.

  Vaya a la primera línea de comando, aquella que dice:

  ```python
  from transitos_dha1001 import *
  ```

  y presione el botón play en el menú superior para ejecutar esa línea de comando.

  Ejecute ahora cada una de las líneas de comando en orden para ejecutar todos los pasos de la reducción y análisis de los datos.

  Para el proyecto, lo más fácil es que usted parta de este ejemplo y lo adapte para procesar y analizar los datos nuevos.

7. Cuando quiera detenerse, note que no tiene que apagar el computador virtual, sino que simplemente lo puede suspender cerrando la ventana de VirtualBox y elgiendo la opción *Save the machine state*.
