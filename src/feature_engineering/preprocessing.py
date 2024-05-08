import re
import json
import os
def complete_chat_line(line: str, sender: str) -> str:
    # Verify start pattern
    if re.match("\[\d{2}/\d{2}/\d{4}, \d{2}:\d{2}:\d{2}\] .+: .+", line):
        return line
    else:
        pattern = "\[\d{2}/\d{2}/\d{4}, \d{2}:\d{2}:\d{2}\]"
        line = f'[15/02/2022, 16:16:16] {sender}: {line}'
        return line

def clean_chat(chat_path: str) -> list:
    
    # Open and read the chat file .txt with utf-8 encoding
    with open(chat_path, 'r', encoding='utf-8') as f:
        chat = f.readlines()

    # Remove emojis
    chat = [re.sub(r'[\U00010000-\U0010ffff]', '', line) for line in chat]

    complete_chat = []
    for line in chat:
        if re.match("\[\d{2}/\d{2}/\d{4}, \d{2}:\d{2}:\d{2}\] .+: .+", line):
            sender = re.split("\[\d{2}/\d{2}/\d{4}, \d{2}:\d{2}:\d{2}\]", line)[1].split(':')[0].strip()
        complete_chat.append(complete_chat_line(line, sender))
    chat = complete_chat

    # Replace tildes
    # chat = [re.sub("á", "a", line) for line in chat]
    # chat = [re.sub("é", "e", line) for line in chat]
    # chat = [re.sub(r'[\u00ed]', "i", line) for line in chat]
    # chat = [re.sub("ó", "o", line) for line in chat]
    # chat = [re.sub("ú", "u", line) for line in chat]

    # Remove special characters as ¡!¿? and others
    chat = [re.sub(r'[¡¿]', '', line) for line in chat]
    
    # Remove date and hour from each line
    chat = [re.sub("\[\d{2}/\d{2}/\d{4}, \d{2}:\d{2}:\d{2}\]", "", line).strip() for line in chat]
    
    # Replace "María Clara Jaramillo" with "mcj"
    chat = [re.sub("María Clara Jaramillo", "mcj", line) for line in chat]

    # Replace "Johny Aleksander" with "me"
    chat = [re.sub("Johny Aleksander", "jav", line) for line in chat]

    # Remove stickers messages
    chat = [line for line in chat if not 'sticker omitted' in line]

    # Remove images messages
    chat = [line for line in chat if not 'image omitted' in line]

    # Remove audio messages
    chat = [line for line in chat if not 'audio omitted' in line]

    # Remove video messages
    chat = [line for line in chat if not 'video omitted' in line]

    # Remove encrytion info
    chat = [line for line in chat if not 'end-to-end encrypted' in line]
    
    # Remove Voice Calls
    chat = [line for line in chat if not 'Voice call' in line]

    return chat

def extract_sender(line: str) -> str:
    sender = line.split(':')[0]
    return sender

def txt_to_json(chat: list) -> dict:
    # Initialize the dictionary
    chat_dict = dict()
    
    # Group by me and mcj messages from
    complete_message = ''
    conversation = []
    starter = extract_sender(chat[0])
    for i, chat_line in enumerate(chat):
        if starter != 'jav' and starter != 'mcj':
            print(f'Role: {starter} ({len(starter)}) \t Message: {chat_line} \t Index: {i}')

        if 'jav:' in chat_line and starter=='jav':
            single_message = chat_line.split(':')[1]
            complete_message = f'{complete_message}. {single_message.strip()}'
        elif 'mcj:' in chat_line and starter=='mcj':
            single_message = chat_line.split(':')[1]
            complete_message = f'{complete_message}. {single_message.strip()}'
        try:
            continuer = extract_sender(chat[i+1])
            if starter != continuer:
                chat_dict[starter] = complete_message
                complete_message = ''
                starter = continuer
                # verify that chat_dict has both keys
                if 'jav' in chat_dict and 'mcj' in chat_dict:
                    conversation.append(chat_dict)
                    chat_dict = dict()
        # Exception index out of range
        except IndexError:
            print('Chat ended')

    return conversation

def write_json(conversation: list, path: str) -> None:
    conversation = {'conversations': conversation}
    with open(path, 'w') as f:
        json.dump(conversation, f, indent=4)

def format_for_fine_tuning(path: str) -> None:
    with open (path, 'r') as f:
        data = json.load(f)
    data = data['conversations']

    # Remove the file conversation-prod.jsonl if it exists
    if os.path.exists('data/curated/conversation-prod.jsonl'):
        os.remove('data/curated/conversation-prod.jsonl')

    transformed_data = {"messages": []}
    for i, messages in enumerate(data):
        for role, content in messages.items():
            if role != 'jav' and role != 'mcj':
                print(f'Role: {role}')
            transformed_data["messages"].append({"role": role, "content": content})
        if i%11 == 0:
            transformed_data["messages"].append({'role': 'system', 'content': 'You are a clone of mcj role, you respond only in spanish and the same tone as mcj'})
            # write transformed_data in append mode in a file named conversation-prod.jsonl
            with open('data/curated/conversation-prod.jsonl', 'a') as f:
                f.write(json.dumps(transformed_data))
                f.write('\n')
            transformed_data = {"messages": []}

    # Convert the transformed data back to a JSON string
    #transformed_json = json.dumps(transformed_data, indent=4)
    
    # write as jsonl
    # with open('data/curated/conversation-prod.jsonl', 'w') as f:
    #     f.write(transformed_json)

    
            

if __name__ == '__main__':
    chat_path = 'data/raw/_chat-prod.txt'
    chat = clean_chat(chat_path)
    chat_sample = chat[:]
    conversation = txt_to_json(chat_sample)
    write_json(conversation, 'data/curated/conversation-prod.json')
    format_for_fine_tuning('data/curated/conversation-prod.json')