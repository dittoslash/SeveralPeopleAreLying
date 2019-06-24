import json

# loads the config.json file
def load_config():
    with open('config.json', 'r+') as f:
        config = json.load(f)

    return config

# loads the questions.json file and rot13s it
def load_questions():
    with open('questions.json', 'r+') as f:
        questions = json.load(f)["questions"]

    for q in questions:
        q["answer"] = rot13(q["answer"])

    return questions

config = load_config()
pre = config['prefix']  # fast access of the prefix


# main message parser
def parse_message(message):
    if not message.startswith(pre):
        return False

    message = message[len(pre):]  # shorten message

    in_quotes = False  # Are we in quotes?
    parsed_message = ['']  # The final parsed message with the arguments as items in the list
    for letter in message:
        if letter == '"':
            parsed_message.append('')
            in_quotes = not in_quotes
            continue

        if letter == ' ' and not in_quotes:
            if parsed_message[-1] == '':  # we don't need to append a new item if the last item is empty
                continue
            else:
                parsed_message.append('')
        else:
            parsed_message[-1] += letter

    return parsed_message

# rot13 decode/encode
def rot13(input):
    rot13 = str.maketrans( 
    "ABCDEFGHIJKLMabcdefghijklmNOPQRSTUVWXYZnopqrstuvwxyz", 
    "NOPQRSTUVWXYZnopqrstuvwxyzABCDEFGHIJKLMabcdefghijklm")
    return str.translate(input, rot13)