#!/usr/bin/python
#coding: utf-8

#!/usr/bin/perl

# CopyRight 2014 Allan Psicobyte (psicobyte@gmail.com)
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.


import os, sys, getopt, tweepy, ConfigParser, codecs, locale

def main(argv):

    # http://stackoverflow.com/questions/4545661/unicodedecodeerror-when-redirecting-to-file
    sys.stdout = codecs.getwriter(locale.getpreferredencoding())(sys.stdout) 

    config = open_config()

    imagen = ""
    reply = ""

    try:                                
        param, args = getopt.getopt(argv, "hnR:i:u:r:t:", ["help", "image=", "user=", "reply=", "retweet=", "timeline=", "nocolor"])
    except getopt.GetoptError:
        show_error("OOOOOH, parámetros")
        sys.exit()
    for opt, arg in param:
        if opt in ("-h", "--help"):
            show_help()
            sys.exit()

        elif opt in ("-i", "--image"):
            imagen = arg

        elif opt in ("-R", "--reply"):
            reply = arg

        elif opt in ("-n", "--nocolor"):
            config.set("Preferences", "color_schema", "none") 

        elif opt in ("-u", "--user"):
            config.set("Preferences", "tweets_per_page", "5")
            show_user(config,arg,1)
            sys.exit()

        elif opt in ("-r", "--retweet"):
            send_retweet(config,arg)
            sys.exit()

        elif opt in ("-t", "--timeline"):
            show_user(config,arg,0)
            sys.exit()

    if len(args) > 0:
        send_tweet(config, args[0], imagen, reply)
    else:
        show_my_timeline(config)


def open_config():
    """Busca y abre un archivo INI para extraer las contraseñas y la configuración
    Por orden de preferencia, busca el archivo en /home/USER/twcli.ini, en /home/USER/.twcli y en twcli.ini
    """ 

    home_dir_ini_file = os.path.join(os.path.expanduser("~"),"twcli.ini")
    home_dir_ini_hidden_file = os.path.join(os.path.expanduser("~"),".twcli")
    my_dir_ini_file = os.path.join(os.path.abspath(os.path.dirname(__file__)),"twcli.ini")

    if os.path.isfile(home_dir_ini_file):
        configfile = home_dir_ini_file
    elif os.path.isfile(home_dir_ini_hidden_file):
        configfile = home_dir_ini_hidden_file
    elif os.path.isfile(my_dir_ini_file):
        configfile = my_dir_ini_file
    else:
        show_error("Falta archivo INI")
        sys.exit()

    config = ConfigParser.ConfigParser()

    config.read(configfile)

    if not config.has_section("Preferences"):
        config.add_section("Preferences")

    if not config.has_option("Preferences", "tweets_per_page"):
        config.set("Preferences", "tweets_per_page", "20")
    if not isinstance(config.get("Preferences", "tweets_per_page"),int):
        config.set("Preferences", "tweets_per_page", "20")

    if not config.has_option("Preferences", "color_schema"):
        config.set("Preferences", "color_schema", "red")
    if not config.get("Preferences", "color_schema"):
        config.set("Preferences", "color_schema", "red")

    return config


def login_api(config):
    """Se loguea en twitter mediante OAuth con las claves extraídas del archivo de configuración"""

    try:
        consumer_key= config.get("Keys", "consumer_key")
        consumer_key_secret= config.get("Keys", "consumer_key_secret")
        access_token= config.get("Keys", "access_token")
        access_token_secret= config.get("Keys", "access_token_secret")
    except:
        show_error("faltan datos de clave en CONFIG, LECHES")
        sys.exit()

    auth = tweepy.OAuthHandler(consumer_key,consumer_key_secret)
    auth.set_access_token(access_token,access_token_secret)

    api = tweepy.API(auth)

    if api.verify_credentials():
        return api
    else:
        show_error("error de autorizacion")
        sys.exit()


def send_tweet(config, message, image="", reply=""):
    """Envía un tweet"""

    api = login_api(config)

    message = message.decode("utf8")

    if reply != "":

        try:
            s = api.get_status(reply)
        except:
            show_error("No se encuentra el tuit")
            sys.exit()

        message = "@" + s.user.screen_name + " " + message

    if len(message) > 140:
        print message
        show_error("Demasiado largo")
        sys.exit()

    if image == "":
#        print "Sale sin imagen:", message
        api.update_status(message, in_reply_to_status_id=reply)

    else:
#        print "sale con imagen"
        api.update_with_media(image, status=message, in_reply_to_status_id=reply)


def send_retweet(config,id):
    """retuitea el tuit que se le pasa como id"""

    api = login_api(config)
    try:    
        api.retweet(id)
    except:
        show_error("no retuit")


def show_my_timeline(config):
    """Muestra el timeline del usuario logeado (los tweets de aquellos alos que sigue etc)"""

    api = login_api(config)

    for s in tweepy.Cursor(api.home_timeline).items(config.getint("Preferences", "tweets_per_page")):
        if hasattr(s, "retweeted_status"):
            print text_color(config,"Strong") + unicode(s.user.screen_name) + text_color(config,"Normal") + " " + "[" + unicode(s.id) + "]" + " << " + unicode(s.retweeted_status.user.screen_name) + " (" + unicode(s.created_at) + ")" + "\n" + unicode(s.retweeted_status.text)
        else:
            print text_color(config,"Strong") + unicode(s.user.screen_name) + text_color(config,"Normal") + " " + "[" + unicode(s.id) + "]" + " (" + unicode(s.created_at) + ")" + "\n" + unicode(s.text)


def show_user(config,user,view_details_user=0):
    """Muestra detalles de un usuario (si view_details_user=1) y sus últimos tweets"""

    api = login_api(config)

    s = api.get_user(user)

    if view_details_user == 1:
        print text_color(config,"Strong") + unicode(user) + text_color(config,"Normal") + " " + "[" + unicode(s.id) + "] (" + unicode(s.created_at) + ")"
        print unicode(s.name)
        print unicode(s.description)
        print "Lugar: \t\t" + unicode(s.location)
        print "Imagen: \t" + unicode(s.profile_image_url)
        print "Sigue/Seguido: " + unicode(s.friends_count) + "/" + unicode(s.followers_count)
        print "Idioma: \t" + unicode(s.lang)
        print "Favs: \t\t" + unicode(s.favourites_count)
        print "Listed: \t" + unicode(s.listed_count)

    if unicode(s.protected) != "True" or unicode(s.following) == "True":
        for s in tweepy.Cursor(api.user_timeline, id= user).items(config.getint("Preferences", "tweets_per_page")):
            if hasattr(s, "retweeted_status"):
                print text_color(config,"Strong") + unicode(s.user.screen_name) + text_color(config,"Normal") + " " + "[" + unicode(s.id) + "]" + " << " + unicode(s.retweeted_status.user.screen_name) + " (" + unicode(s.created_at) + ")" + "\n" + unicode(s.retweeted_status.text)
            else:
                print text_color(config,"Strong") + unicode(s.user.screen_name) + text_color(config,"Normal") + " " + "[" + unicode(s.id) + "]" + " (" + unicode(s.created_at) + ")" + "\n" + unicode(s.text)
    else:
        print "PROTECTED"


def show_error(error):
    """Muestra los errores, o los mostrará cuando esta función esté hecha"""
    
    print error


def text_color(config,color):
    """Asigna códigos de color a cada tipo de texto en función de la configuración"""

    if config.get("Preferences", "color_schema").lower() == "red": 
        if color == "Strong":
            code_color= "\033[1;31m"
        elif color == "Normal":
            code_color= "\033[0m"
        else:
            code_color= ""

    elif config.get("Preferences", "color_schema").lower() == "green": 
        if color == "Strong":
            code_color= "\033[1;32m"
        elif color == "Normal":
            code_color= "\033[0m"
        else:
            code_color= ""

    elif config.get("Preferences", "color_schema").lower() == "blue": 
        if color == "Strong":
            code_color= "\033[1;34m"
        elif color == "Normal":
            code_color= "\033[0m"
        else:
            code_color= ""

    elif config.get("Preferences", "color_schema").lower() == "purple": 
        if color == "Strong":
            code_color= "\033[1;35m"
        elif color == "Normal":
            code_color= "\033[0m"
        else:
            code_color= ""

    elif config.get("Preferences", "color_schema").lower() == "cyan": 
        if color == "Strong":
            code_color= "\033[1;36m"
        elif color == "Normal":
            code_color= "\033[0m"
        else:
            code_color= ""

    elif config.get("Preferences", "color_schema").lower() == "none": 
        code_color= ""

    else:
        if color == "Strong":
            code_color= "\033[1;31m"
        elif color == "Normal":
            code_color= "\033[0m"
        else:
            code_color= ""

    return code_color


def show_help():
    """Muestra un texto de ayuda básico"""

    print u" "
    print u"\ttwcli.py [opciones] [mensaje]"
    print u" "
    print u"\tSi se invoca sin parámetros, mostrará el timeline del usaurio."
    print u"\tSi hay un mensaje, lo envía como tweet."
    print u" "
    print u"\t-h, --help"
    print u"\t\tMuestra este texto de ayuda."
    print u" "
    print u"\t-n, --nocolor"
    print u"\t\tDesactiva el uso de color."
    print u" "
    print u"\t-i, --image"
    print u"\t\tDebe ir seguido del path de un archivo. Adjunta ese archivo al tweet."
    print u" "
    print u"\t-u, --user"
    print u"\t\tDebe ir seguido de un nombre (ID) de usaurio. Muestra información de ese usuario."
    print u" "
    print u"\t-t, --timeline"
    print u"\t\tDebe ir seguido de un nombre (ID) de usaurio. Muestra el timeline de ese usuario."




if __name__ == "__main__":
    main(sys.argv[1:])
