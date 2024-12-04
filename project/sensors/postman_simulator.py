if __name__ == '__main__':
    while True:
        cmd = input("Insert package weigth: ")
        f = open("weight.txt", "w")
        f.write(cmd)
        f.close()