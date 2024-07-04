import re
# Load txt dataset
def load_data(chat_path: str):
    with open(chat_path, 'r') as f:
        chat = f.readlines()
    return chat

def clean_data(chat: list):
    # Unroll threads
    # pattern_thread = "^\t|    [A-Za-z]{3} \d{2}, \d{4}  \d{1,2}:\d{2}:\d{2} [AP]M"
    pattern_thread = "^\t|    .+"
    patterns_unrolled_message = "This message responded to an earlier message."

    for i, line in enumerate(chat):
        if re.match(pattern_thread, line):
            chat[i] = line.strip()

        # Remove unrolled messages
        if re.match(patterns_unrolled_message, line):
            chat[i-1] = 'DELETE_ME: ' + chat[i-1]
            chat[i-2] = 'DELETE_ME: ' + chat[i-2]
            chat[i-3] = 'DELETE_ME: ' + chat[i-3]


    #chat = [re.sub(pattern_thread, 'thread_delete_me', line).strip() for line in chat]
    # for i, line in enumerate(chat):
    #     if re.match(pattern_thread, line):
    #         unrolled_chat.insert(i, '\n')
    #     if line != '\n':
    #         unrolled_chat.append(line.strip())
    #     else:
    #         unrolled_chat.append(line)
    # chat = unrolled_chat
    return chat

if __name__ == '__main__':
    # Load data
    data_path = 'data/raw/_imessages-prod.txt'
    chat = load_data(data_path)
    # Clean data
    chat = clean_data(chat)
    for line in chat:
        print(line)