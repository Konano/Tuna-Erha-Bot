import re

# MarkdownV2 Mode


def escaped(str):
    return re.sub(r'([\_\*\[\]\(\)\~\`\>\#\+\-\=\|\{\}\.\!])', '\\\\\\1', str)
