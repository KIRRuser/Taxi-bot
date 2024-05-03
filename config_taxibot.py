token = '6473499327:AAHisAxt2hgwizxj8ulVBcc57pOw4JEJIDE'
id_group = '-1002031313595'

import random

def generate_key():
    chars = '+-/*!&$#?=@<>abcdefghijklnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890'
    key =''
    for i in range(16):
        key += random.choice(chars)
    return key

