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
        param, args = getopt.getopt(argv, "hnR:i:u:r:t:f:v:s:", ["help", "image=", "user=", "reply=", "retweet=", "timeline=", "fav=", "nocolor", "view=", "search="])
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

        elif opt in ("-v", "--view"):
            show_tweet(config,arg)
            sys.exit()

        elif opt in ("-f", "--fav"):
            favorite(config,arg)
            sys.exit()

        elif opt in ("-t", "--timeline"):
            show_user(config,arg,0)
            sys.exit()

        elif opt in ("-s", "--search"):
            search(config,arg)
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
    if not config.get("Preferences", "tweets_per_page").isdigit:
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

    message = message.decode(sys.stdin.encoding)

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

        if config.get("Preferences", "ask_confirmation").lower() == "yes":
            confirma = raw_input( message + " " + text_color(config,"Strong") + "Send? [Y/n]" + text_color(config,"Normal"))
            if confirma.lower() == "y" or confirma == "":
                api.update_status(message, in_reply_to_status_id=reply)
            else:
                print text_color(config,"Strong") + "Cancelled"  + text_color(config,"Normal")
        else:
            api.update_status(message, in_reply_to_status_id=reply)

    else:

        path_image = os.path.abspath(image)

        if os.path.isfile(path_image):

            if config.get("Preferences", "ask_confirmation").lower() == "yes":
                confirma = raw_input( message + " " + text_color(config,"Strong") + "Send? [Y/n]" + text_color(config,"Normal"))
                if confirma.lower() == "y" or confirma == "":
                    api.update_with_media(path_image, status=message, in_reply_to_status_id=reply)
                else:
                    print text_color(config,"Strong") + "Cancelled"  + text_color(config,"Normal")
            else:
                api.update_with_media(path_image, status=message, in_reply_to_status_id=reply)
        else:
            show_error("no se encuentra la imagen")
            sys.exit()


def send_retweet(config,id):
    """retuitea el tuit que se le pasa como id"""

    api = login_api(config)

    if config.get("Preferences", "ask_confirmation").lower() == "yes":

        try:
            s = api.get_status(id)
        except:
            show_error("el tuit original no existe")
            sys.exit()

        confirma = raw_input(unicode(s.text) + text_color(config,"Strong") + " Retweet? [Y/n]" + text_color(config,"Normal"))
        if confirma.lower() == "y" or confirma == "":
            try:
                api.retweet(id)
            except:
                show_error("no retuit")
        else:
            print text_color(config,"Strong") + "Cancelled"  + text_color(config,"Normal")
    else:
        try:
            api.retweet(id)
        except:
            show_error("no retuit")


def show_my_timeline(config):
    """Muestra el timeline del usuario logeado (los tweets de aquellos a los que sigue etc)"""

    api = login_api(config)

    for s in tweepy.Cursor(api.home_timeline).items(config.getint("Preferences", "tweets_per_page")):
        if hasattr(s, "retweeted_status"):
            print text_color(config,"Strong") + unicode(s.user.screen_name) + text_color(config,"Normal") + " " + "[" + unicode(s.id) + "]" + " << " + unicode(s.retweeted_status.user.screen_name) + " (" + unicode(s.created_at) + ")" + "\n" + unicode(s.retweeted_status.text)
        else:
            print text_color(config,"Strong") + unicode(s.user.screen_name) + text_color(config,"Normal") + " " + "[" + unicode(s.id) + "]" + " (" + unicode(s.created_at) + ")" + "\n" + unicode(s.text)


def search(config,query):
    """Buscar"""

    query = query.decode(sys.stdin.encoding)
    api = login_api(config)

    for s in tweepy.Cursor(api.search, q = query).items(config.getint("Preferences", "tweets_per_page")):
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


def show_tweet(config, id):
    """Muestra detalles de un tweet"""

    api = login_api(config)

    try:
        s = api.get_status(id)
    except:
        show_error("el tuit buscado no existe")
        sys.exit()


    reply = s.in_reply_to_status_id_str

    list_previous_tweets = []

    while reply != None:
        s2 = api.get_status(reply)
        list_previous_tweets.append("   " + text_color(config,"Middle") + unicode(s2.user.screen_name) + text_color(config,"Normal") + " " + "[" + unicode(s2.id) + "]" + " (" + unicode(s2.created_at) + ")" + "\n" + "   " + unicode(s2.text))
        reply = s2.in_reply_to_status_id_str

    list_previous_tweets.reverse()

    for elem in list_previous_tweets:
        print elem


    if hasattr(s, "retweeted_status"):
        print text_color(config,"Strong") + unicode(s.user.screen_name) + text_color(config,"Normal") + " " + "[" + unicode(s.id) + "]" + " << " + unicode(s.retweeted_status.user.screen_name) + " (" + unicode(s.created_at) + ")" + "\n" + unicode(s.retweeted_status.text)
    else:
        print text_color(config,"Strong") + unicode(s.user.screen_name) + text_color(config,"Normal") + " " + "[" + unicode(s.id) + "]" + " (" + unicode(s.created_at) + ")" + "\n" + unicode(s.text)

    print text_color(config,"Strong") + "Favs: " + text_color(config,"Normal") + str(s.favorite_count)
    print text_color(config,"Strong") + "RTS:  " + text_color(config,"Normal") + str(s.retweet_count)


def show_error(error):
    """Muestra los errores, o los mostrará cuando esta función esté hecha"""
    
    print error


def text_color(config,color):
    """Asigna códigos de color a cada tipo de texto en función de la configuración"""

    if config.get("Preferences", "color_schema").lower() == "red": 
        if color == "Strong":
            code_color= "\033[1;31m"
        elif color == "Middle":
            code_color= "\033[0;31m"
        elif color == "Normal":
            code_color= "\033[0m"
        else:
            code_color= ""

    elif config.get("Preferences", "color_schema").lower() == "green": 
        if color == "Strong":
            code_color= "\033[1;32m"
        elif color == "Middle":
            code_color= "\033[0;32m"
        elif color == "Normal":
            code_color= "\033[0m"
        else:
            code_color= ""

    elif config.get("Preferences", "color_schema").lower() == "blue": 
        if color == "Strong":
            code_color= "\033[1;34m"
        elif color == "Middle":
            code_color= "\033[0;34m"
        elif color == "Normal":
            code_color= "\033[0m"
        else:
            code_color= ""

    elif config.get("Preferences", "color_schema").lower() == "purple": 
        if color == "Strong":
            code_color= "\033[1;35m"
        elif color == "Middle":
            code_color= "\033[0;35m"
        elif color == "Normal":
            code_color= "\033[0m"
        else:
            code_color= ""

    elif config.get("Preferences", "color_schema").lower() == "cyan": 
        if color == "Strong":
            code_color= "\033[1;36m"
        elif color == "Middle":
            code_color= "\033[0;36m"
        elif color == "Normal":
            code_color= "\033[0m"
        else:
            code_color= ""

    elif config.get("Preferences", "color_schema").lower() == "none": 
        code_color= ""

    else:
        if color == "Strong":
            code_color= "\033[1;31m"
        elif color == "Middle":
            code_color= "\033[0;31m"
        elif color == "Normal":
            code_color= "\033[0m"
        else:
            code_color= ""

    return code_color


def favorite(config, id):
    """marca como favorito el tuit que se le pasa como id"""

    api = login_api(config)

    if config.get("Preferences", "ask_confirmation").lower() == "yes":

        try:
            s = api.get_status(id)
        except:
            show_error("el tuit a favear no existe")
            sys.exit()

        confirma = raw_input(unicode(s.text) + text_color(config,"Strong") + " Fav? [Y/n]" + text_color(config,"Normal"))
        if confirma.lower() == "y" or confirma == "":
            try:
                api.create_favorite(id)
            except:
                show_error("no Fav")
        else:
            print text_color(config,"Strong") + "Cancelled"  + text_color(config,"Normal")
    else:
        try:
            api.create_favorite(id)
        except:
            show_error("no Fav")


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
    print u"\t-R, --reply"
    print u"\t\tDebe ir seguido del ID de un tweet. El [mensaje] se enviará como respuesta a ese tweet."
    print u" "
    print u"\t-i, --image"
    print u"\t\tDebe ir seguido del path de un archivo. Adjunta ese archivo al tweet."
    print u" "
    print u"\t-u, --user"
    print u"\t\tDebe ir seguido de un nombre (ID) de usaurio. Muestra información de ese usuario."
    print u" "
    print u"\t-t, --timeline"
    print u"\t\tDebe ir seguido de un nombre (ID) de usaurio. Muestra el timeline de ese usuario."
    print u" "
    print u"\t-v, --view"
    print u"\t\tDebe ir seguido del ID de un tweet. Muestra detalles de ese tweet."
    print u" "
    print u"\t-r, --retweet"
    print u"\t\tDebe ir seguido del ID de un tweet. Retuitea ese tweet."
    print u" "
    print u"\t-f, --fav"
    print u"\t\tDebe ir seguido del ID de un tweet. Marca ese tweet como favorito."
    print u" "
    print u"\t-s, --search"
    print u"\t\tDebe ir seguido de una cadena. Busca esa cadena y muestra el resultado."


if __name__ == "__main__":
    main(sys.argv[1:])
