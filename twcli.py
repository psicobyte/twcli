#!/usr/bin/python
#coding: utf-8

import os, sys, getopt, tweepy, ConfigParser, codecs, locale

def main(argv):

    # http://stackoverflow.com/questions/4545661/unicodedecodeerror-when-redirecting-to-file
    sys.stdout = codecs.getwriter(locale.getpreferredencoding())(sys.stdout) 

    global color_schema
    color_schema = "Red" 
    
    imagen= ""

    try:                                
        param, args = getopt.getopt(argv, "hni:u:", ["help", "image=", "user=", "nocolor"])
    except getopt.GetoptError:
        show_error("OOOOOH, parámetros")

    for opt, arg in param:
        if opt in ("-h", "--help"):
            show_help()

        elif opt in ("-i", "--image"):
            imagen = arg

        elif opt in ("-n", "--nocolor"):
            color_schema = "None" 

        elif opt in ("-u", "--user"):
            show_user(arg)

    if len(args) > 0:
        if len(args[0]) < 141:
            send_tweet(args[0],imagen)
        else:
            show_error("Demasiado largo")
    else:
        show_my_timeline(10)


def login_api():

    config = ConfigParser.ConfigParser()
    config.read("twcli.ini")

    try:
        consumer_key= config.get("Keys", "consumer_key")
        consumer_key_secret= config.get("Keys", "consumer_key_secret")
        access_token= config.get("Keys", "access_token")
        access_token_secret= config.get("Keys", "access_token_secret")
    except:
        show_error("faltan datos de clave en CONFIG, LECHES")

    auth = tweepy.OAuthHandler(consumer_key,consumer_key_secret)
    auth.set_access_token(access_token,access_token_secret)

    return tweepy.API(auth)


def send_tweet(message,image=""):

    api = login_api()

    if image == "":
        print "Sale sin imagen"
#        api.update_status(message)
    else:
        print "sale con imagen"
#        api.update_with_media(image, status=message)


def show_my_timeline(num):

    api = login_api()

    for s in tweepy.Cursor(api.home_timeline).items(num):
        if hasattr(s, 'retweeted_status'):
    		print text_color("Strong") + unicode(s.user.screen_name) + text_color("Normal") + " " + '[' + unicode(s.id) + ']' + ' << ' + unicode(s.retweeted_status.user.screen_name) + ' (' + unicode(s.created_at) + ')' + '\n' + unicode(s.retweeted_status.text)
    	else:
    		print text_color("Strong") + unicode(s.user.screen_name) + text_color("Normal") + " " + '[' + unicode(s.id) + ']' + ' (' + unicode(s.created_at) + ')' + '\n' + unicode(s.text)


def show_user(user):

    api = login_api()

    s = api.get_user(user)
    print text_color("Strong") + unicode(user) + text_color("Normal") + " " + '[' + unicode(s.id) + '] (' + unicode(s.created_at) + ')'
    print unicode(s.name)
    print unicode(s.description)
    print "Lugar: \t\t" + unicode(s.location)
    print "Imagen: \t" + unicode(s.profile_image_url)
    print "Sigue/Seguido: " + unicode(s.friends_count) + "/" + unicode(s.followers_count)
    print "Idioma: \t" + unicode(s.lang)
    print "Favs: \t\t" + unicode(s.favourites_count)
    print "Listed: \t" + unicode(s.listed_count)
    sys.exit()


def show_error(error):
    
    print error

    sys.exit()

def text_color(color):

    if color_schema == "Red": 
        if color == "Strong":
            code_color= "\033[1;31m"
        elif color == "Normal":
            code_color= "\033[0m"
        else:
            code_color= ""

    if color_schema == "None": 
        code_color= ""

    return code_color


def show_help():

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
    print u"\t\tDebe ir seguido de un nombre o ID de usaurio. Muestra información de ese usuario."
    sys.exit()

if __name__ == "__main__":
    main(sys.argv[1:])
