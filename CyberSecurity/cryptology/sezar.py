import math

alfabe_kucuk = "ğüıjçzköybşrhdalvmtnepsuocfgi̇"
alfabe_buyuk = "ŞZÜKÇYIRĞJHİTVDMÖEALONBPGSUFC"

def sezar_encryption(text, type, time = 2):
    ham_text = ""
    counter = 1
    
    if type == 'encrypt':
        for r in text:
            if r.isupper():
                ham_text += alfabe_buyuk[((alfabe_buyuk.index(r)) + tri(counter))%29]
                counter += 1
            elif r.islower():
                ham_text += alfabe_kucuk[((alfabe_kucuk.index(r)) + tri(counter))%29]
                counter += 1
            else:
                ham_text+=r
                counter += 1
        
        if time > 1:
            return sezar_encryption(ham_text, 'encrypt', time - 1)
        else:        
            return ham_text
        
    elif type == 'decrypt':
        for r in text:
            if r.isupper():
                ham_text += alfabe_buyuk[((alfabe_buyuk.index(r)) - tri(counter))%29]
                counter += 1
            elif r.islower():
                ham_text += alfabe_kucuk[((alfabe_kucuk.index(r)) - tri(counter))%29]
                counter += 1
            else:
                ham_text+=r
                counter += 1

        if time > 1:
            return sezar_encryption(ham_text, 'decrypt', time - 1)
        else:        
            return ham_text
    else:
        return 'geçerli işlem giriniz. encrypt ,  decrypt'

def tri(i):
    return round((math.sin(i) + 1) * 15)

#ToDo: Kullanıcıdan input alınacak şekilde ve des ve 3 des algoritmaları incelenip dahil edilecek şekilde güncellenecek  

print(sezar_encryption('mehmet', 'encrypt'))


print(sezar_encryption('lemcsr', 'decrypt'))







