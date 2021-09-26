def write_status(text):
    with open('status.txt','w') as file:
        file.write(text)


def load_status():
    try:
        with open('status.txt') as file:
            data = file.read()

        return data

    except FileNotFoundError:
        write_status("false")
