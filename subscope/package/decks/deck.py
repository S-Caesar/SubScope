import pandas as pd
import os
from pathlib import Path

from subscope.package.decks.card import Card, CardHeading
from subscope.package.database.database import Database
from subscope.package.options.options import Options


class Deck:
    _START = str(Path(__file__).parent.parent.parent) + '/user/subtitles'
    _VIDEO = 'video'
    _CUMULATIVE_WORDS = 'Cumulative Words'
    _WORD_COLUMN = 'reading'
    _STATUS = 'status'

    @classmethod
    def create(cls, deck_name, new_limit, review_limit, card_format, source=None, target_comp=None):
        headings = []
        for heading in CardHeading:
            headings.append(heading.text)

        if source is not None:
            target_comp = int(target_comp) / 100
            cards = cls._create_cards(source, target_comp)

            video_folder = cls._START + '/' + source + '/' + cls._VIDEO
            for file in os.listdir(video_folder):
                os.remove(video_folder + '/' + file)

            deck = []
            for card in cards:
                deck.append(card.entry())
            deck = pd.DataFrame(deck, columns=headings)

        else:
            deck = cls._create_blank_deck(headings)

        cls._write_deck_to_file(deck_name, deck)
        cls._add_deck_to_settings_file(deck_name, new_limit, review_limit, card_format)

    @staticmethod
    def _create_blank_deck(headings):
        blank_deck = pd.DataFrame(columns=headings)
        return blank_deck

    @classmethod
    def _create_cards(cls, source, target_comp):
        source_database = Database.get_columns_by_subtitle_source(source)
        words_list = cls._get_words_for_target_comprehension(source_database, source, target_comp)

        cards = []
        for word in words_list:
            cards.append(Card(word))
        return cards

    @classmethod
    def _get_words_for_target_comprehension(cls, database, source, target_comp):
        words_list = []
        for column_name in database.columns:
            if source in column_name:
                column_words = database[database[column_name] != 0]
                column_words = column_words.sort_values(by=[column_name], ascending=False, ignore_index=True)
                total_words = column_words[column_name].sum()
                target_words = round(total_words * target_comp)

                column_words[cls._CUMULATIVE_WORDS] = column_words[column_name].cumsum()
                required_words = column_words.loc[column_words[cls._CUMULATIVE_WORDS] < target_words]
                unknown_required_words = required_words[required_words[cls._STATUS] == 0]
                words_list.extend(list(unknown_required_words[cls._WORD_COLUMN]))
        return list(set(words_list))

    @staticmethod
    def _write_deck_to_file(deck_name, deck):
        deck_folder = Options.deck_folder_path()
        deck.to_csv(deck_folder + '/' + deck_name + '.txt', sep='\t', index=None)

    @staticmethod
    def _add_deck_to_settings_file(deck_name, new_limit, review_limit, card_format):
        Options.add_deck_to_settings(deck_name, new_limit, review_limit, card_format)


if __name__ == '__main__':
    Deck.create('Test', '10', '50', 'Default', 'SteinsGate', '5')
