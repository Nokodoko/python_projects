as the world's best pythonista:

write a shell-gpt app (in python) that will take a string as a payload and send a prompt to the grok backend api. It will stream tokens as a response to stdout.

it will also store chats with the --chats flag the user will have the ability to locally store a chat thread and recall it. The chat flag will take a string argument of the chat name and that will be the file name for which the thread is stored and recalled as. If the --chat flag is used with a string that is already stored, that file will be recalled as the context for the following prompt.
there will also be a --prompt flag that will allow the user to modify a prompt before sending to the grok back end.
