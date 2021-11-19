import random
def password_gen(len_pass, use_number, use_lower, use_special, password_qty):
    len_pass = int(len_pass)
    password_qty = int(password_qty)
    passwords = [] 
    password = ''
    possible_symbols = ''
    if use_number:
        possible_symbols += '1234567890'
    if use_lower:
        possible_symbols += 'abcdefghijklmnopqrstuvwxyz'
    if use_special:
        possible_symbols += '`~!@"#$%^&*()_+№;:?*-='
    for x in range(password_qty):
        for i in range(len_pass):

            password += random.choice(possible_symbols)
        passwords.append(password)
        password = ''

    return passwords





