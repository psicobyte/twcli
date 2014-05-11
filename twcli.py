#!/usr/bin/python
#coding: utf-8

import os, sys, getopt, tweepy, ConfigParser

def main(argv):

    imagen= ""

    try:                                
        param, args = getopt.getopt(argv, "hi:", ["help", "image="])
    except getopt.GetoptError:
        show_error("OOOOOH, parámetros")

    for opt, arg in param:
        if opt in ("-h", "--help"):
            show_error("AYUDA")

        elif opt in ("-i", "--image"):
            imagen = arg

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
    		print '\033[1;31m' + unicode(s.user.screen_name) + '\033[0m ' + '[' + unicode(s.id) + ']' + ' << ' + unicode(s.retweeted_status.user.screen_name) + ' (' + unicode(s.created_at) + ')' + '\n' + unicode(s.retweeted_status.text)
    	else:
    		print '\033[1;31m' + unicode(s.user.screen_name) + '\033[0m ' + '[' + unicode(s.id) + ']' + ' (' + unicode(s.created_at) + ')' + '\n' + unicode(s.text)


def show_error(error):
    
    print error

    print "USO: Bla bla bla bla"

    sys.exit()


if __name__ == "__main__":
    main(sys.argv[1:])
