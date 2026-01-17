from util.parser import SecenePaser





if __name__ == '__main__':
    uid=1
    json={}
    try:
        parser = SecenePaser(uid)
        with open(f"./story/{uid}.txt", "r", encoding="utf-8") as f:
            text = f.read()
            json=parser.parse(text)
            print(json)

    except Exception as e:
        print(e)