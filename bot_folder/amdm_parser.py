import re
import requests
from bs4 import BeautifulSoup

class AmDm:
    def __init__(self):
        pass

    def get_chords_list(self, query):
        result = requests.post('http://amdm.ru/search/?q={}'.format(
            re.sub(r'\s', '+', query)))
        soup = BeautifulSoup(result.content, "html.parser")
        table = soup.find_all("table", "items")

        if not table:
            return False

        table = table[0]
        if " ".join(table['class']) == "items debug2":
            return False

        r = table.find_all("a", {"class": "artist"})

        results = []
        for index, item in enumerate(r[::2]):
            results.append({'artist': item.contents[0]})
            r.remove(item)

        for index, item in enumerate(r):
            results[index]['title'] = item.contents[0]
            url = item['href']
            if url.startswith('http://') or url.startswith('https://'):
                results[index]['url'] = url
            else:
                results[index]['url'] = 'https://amdm.ru{}'.format(url)
        return results

    def get_chords_song(self, url):
        song = requests.get(url)
        soup = BeautifulSoup(song.content, "html.parser")

        content = soup.find_all("pre", {"itemprop": "chordsBlock"})

        if not content:
            return "аккорды не найдены"

        result_text = ""
        for item in content[0].contents:
            if item.name is None:
                if item.string:
                    result_text += item.string
            else:
                classes = item.get('class', [])
                is_chord_div = ('podbor_chord' in classes or 'podbor__chord' in classes)

                if item.name == 'div' and is_chord_div:
                    chord = item.get('data-chord', '')
                    if chord:
                        result_text += '[' + chord + ']'
                    else:
                        span = item.find('span')
                        if span and span.string:
                            result_text += '[' + span.string + ']'
                elif item.name == 'br':
                    result_text += '\n'
                else:
                    if item.string:
                        result_text += item.string
                    else:
                        inner_text = item.get_text()
                        if inner_text:
                            result_text += inner_text

        result_text = re.sub(r' +', ' ', result_text)
        result_text = re.sub(r'\]\[', '] [', result_text)
        result_text = re.sub(r'\n\s*\n', '\n\n', result_text)
        result_text = re.sub(r'<[^>]+>', '', result_text)
        result_text = re.sub(r'^ +', '', result_text, flags=re.MULTILINE)

        def wrap_chord(match):
            chord = match.group(0)
            if chord.startswith('[') and chord.endswith(']'):
                return chord
            return '[' + chord + ']'

        chord_pattern = r'\b(?:[A-G](?:#|b)?(?:m|M|maj|dim|aug|7|6|9)?)\b'

        lines = result_text.split('\n')
        new_lines = []
        for line in lines:
            if '[' in line:
                parts = re.split(r'(\[[^\]]+\])', line)
                new_parts = []
                for part in parts:
                    if part.startswith('[') and part.endswith(']'):
                        new_parts.append(part)
                    else:
                        new_parts.append(re.sub(chord_pattern, wrap_chord, part))
                new_lines.append(''.join(new_parts))
            else:
                new_lines.append(re.sub(chord_pattern, wrap_chord, line))

        result_text = '\n'.join(new_lines)
        result_text = re.sub(r'\[\[([^\]]+)\]\]', r'[\1]', result_text)

        return result_text