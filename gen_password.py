import secrets

def gen_password():
    with open('/usr/share/dict/words') as f:
        words = [word.strip() for word in f if "'" not in word]
    password = ' '.join(secrets.choice(words) for i in range(4))
    return password

if __name__ == '__main__':
    print(gen_password())
