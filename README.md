Twcli
=====

##ADVERTENCIA

**Twcli está aún en fase pre-alpha!** 

##Descripción

Twcli es un (otro) cliente de twitter en línea de comandos.

Twcli necesita una api key de twitter. Se trata de un conjunto de cuatro claves (dos de aplicación y dos de usaurio) que se obtienen al dar de alta una aplicación aquí: [https://dev.twitter.com/apps/new](https://dev.twitter.com/apps/new)

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

Ver menú de ayuda:

`twcli.pl -h`


##twcli.ini

El archivo twcli.ini contiene las claves de acceso a twitter y algunas opciones de configuración.

Twcli buscará el archivo en "/home/USER/twcli.ini". Si no lo encuentra ahí, lo buscará en "/home/USER/.twcli" y, si tampoco está ahí, lo buscará en el directorio de la propia aplicación con el nombre de "twcli.ini".

Dentro de este archivo hay dos secciones:

###Keys

Esta sección contiene las claves del usaurio (se pueden obtener de [https://dev.twitter.com/apps/new](https://dev.twitter.com/apps/new)).

* consumer_key: API key de Twitter
* consumer_key_secret: API secret de Twitter
* access_token: Access token de Twitter
* access_token_secret: Access token secret de Twitter

###Preferences

* tweets_per_page: Número de tuits que se mostrarán en una página (El valor por defecto es 20)

* color_schema: Color que se usará para resaltar el texto. Las opciones son:
..* red
..* green
..* blue
..* purple
..* cyan
..* none

El valor por defecto es "red"

* ask_confirmation: Si tiene el valor "yes" pedirá confirmación antes de enviar un tweet

