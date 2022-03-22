def decrypt(str1):
    strn = ""
    counter = 0;
    for strg in str1.split("\n"):
        for chrt in strg.split(" "):
            if chrt != "":
                strn+=str(chr(int(chrt)-counter))
                counter += 1
                if(counter>1000):
                    counter = 0
        strn+="\n"
    return strn[:-1]

def encrypt(str1):
    strn = ""
    counter = 0;
    for chr in str1:
        if chr != "\n":
            strn += str(ord(chr)+counter)+" "
            counter += 1
            if(counter>1000):
                counter = 0
        else:
            strn+="\n"
    return strn
