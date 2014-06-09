Twcli
=====

**Twcli está aún en fase pre-alpha!** 

##Descripción

Twcli es un (otro) cliente de twitter en línea de comandos.

Twcli necesita una api key de twitter. Se trata de un conjunto de cuatro claves (dos de aplicación y dos de usaurio) que se obtienen al dar de alta una palicación aquí: [https://dev.twitter.com/apps/new](https://dev.twitter.com/apps/new)

Twcli usa un archivo INI para almacenar las contraseñas y las opciones de configuración

Por orden de preferencia, buscará el archivo en

* /home/USER/twcli.ini
* /home/USER/.twcli
* twcli.ini

##Ejemplos

Ver tu propio timeline (tweets de gente que sigues o que te mencionan)

`twcli.pl`

Ver detalles de un usuaio:

`twcli.pl -u Usuario`

Ver timeline de un usuaio:

`twcli.pl -t Usuario`

Enviar un tweet:

`twcli.pl "texto del tweet"`

Enviar un tweet con una imagen adjunta;

`twcli.pl -i "/ruta/a/la/imagen" "texto del tweet"`

Ver menú de ayuda

Ver detalles de un usuaio:

`twcli.pl -h`

