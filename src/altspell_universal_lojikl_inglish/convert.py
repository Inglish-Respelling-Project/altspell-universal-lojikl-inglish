'''
    Altspell  Universal Lojikl Inglish plugin for altspell.
    Copyright (C) 2024  Nicholas Johnson

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <https://www.gnu.org/licenses/>.
'''

import csv
from importlib.resources import files
from . import data
import spacy


class Dictionary:
    def __init__(self, fwd: bool):
        self.dict = {}
        self._populate_dict(fwd)

    def _populate_dict(self, fwd: bool):
        with files(data).joinpath('universal-lojikl-inglish-dict.csv').open('r') as file:

            for row in csv.reader(file):
                tradspell = row[0]
                uli = row[1]

                if fwd:
                    pos = row[3]
                    if pos == '':
                        pos = None

                    self.dict[(tradspell, pos)] = uli
                else:
                    self.dict[uli] = tradspell

                    alternates = row[2].split(';')

                    for alternate in alternates:
                        self.dict[alternate] = tradspell

class Converter:
    # Load spaCy without any unnecessary components
    _nlp = spacy.load('en_core_web_sm', disable=['parser', 'ner'])

    def __init__(self, fwd: bool):
        self._fwd = fwd
        self._dict = Dictionary(self._fwd)

    def convert_para(self, text: str) -> str:
        out_tokens = []

        doc = Converter._nlp(text)
        for token in doc:
            token_lower = token.text.lower()

            if self._fwd:
                pos = token.pos_
                match pos:
                    case 'NOUN':
                        pos = 'n'
                    case 'VERB':
                        pos = 'v'
                    case 'ADJ':
                        pos = 'adj'
                    case 'ADV':
                        pos = 'adv'
                    case 'INTJ':
                        pos = 'interj'
                    case _:
                        pos = None

                if (token_lower, None) in self._dict.dict:
                    if token.text[0].isupper():
                        word = self._dict.dict[(token_lower, None)]
                        word = word[0].upper() + word[1:]
                        out_tokens.append(word)
                    else:
                        out_tokens.append(self._dict.dict[(token_lower, None)])
                elif (token_lower, pos) in self._dict.dict:
                    if token.text[0].isupper():
                        word = self._dict.dict[(token_lower, pos)]
                        word = word[0].upper() + word[1:]
                        out_tokens.append(word)
                    else:
                        out_tokens.append(self._dict.dict[(token_lower, pos)])
                elif (token.text, None) in self._dict.dict:
                    out_tokens.append(self._dict.dict[(token.text, None)])
                elif (token.text, pos) in self._dict.dict:
                    out_tokens.append(self._dict.dict[(token.text, pos)])
                else:
                    out_tokens.append(token.text)
            else:
                if token_lower in self._dict.dict:
                    if token.text[0].isupper():
                        word = self._dict.dict[token_lower]
                        word = word[0].upper() + word[1:]
                        out_tokens.append(word)
                    else:
                        out_tokens.append(self._dict.dict[token_lower])
                elif token.text in self._dict.dict:
                    out_tokens.append(self._dict.dict[token.text])
                else:
                    out_tokens.append(token.text)

            out_tokens.append(token.whitespace_)

        return ''.join(out_tokens)
