import os
import os.path
import shutil
from unicodedata import normalize

import whoosh
from whoosh import index, highlight
from whoosh.fields import Schema, TEXT, ID
from whoosh.qparser import QueryParser, FuzzyTermPlugin, PhrasePlugin, SequencePlugin
from whoosh.scoring import FunctionWeighting
from whoosh.analysis import CharsetFilter, StemmingAnalyzer
from whoosh import fields
from whoosh.support.charset import accent_map


class PreMarkFormatter(highlight.Formatter):

    def format_token(self, text, token, replace=False):
        # Use the get_text function to get the text corresponding to the
        # token
        tokentext = highlight.get_text(text, token, replace)

        # Return the text as you want it to appear in the highlighted
        # string
        return f'<mark class="main_text_box_match">{tokentext}</mark>'


class Search:

    def __init__(self, index_dir, text_dir):
        self.ix = index.open_dir(index_dir)

    def search(self, text, _type='default'):

        def myscore_fn(searcher, fieldname, text, matcher):
            return matcher.value_as("frequency")

        pos_weighting = FunctionWeighting(myscore_fn)

        with self.ix.searcher(weighting=pos_weighting) as searcher:

            parser = QueryParser("text", self.ix.schema)

            if _type == 'fuzzy':
                parser.add_plugin(FuzzyTermPlugin())

            elif _type == 'sequence':
                parser.remove_plugin_class(PhrasePlugin)
                parser.add_plugin(SequencePlugin())
                parser.add_plugin(FuzzyTermPlugin())

            query = parser.parse(text)

            results = searcher.search(query, terms=True)
            results.formatter = PreMarkFormatter()
            results.fragmenter = whoosh.highlight.WholeFragmenter()

            search_results = [{'id': result['id'],
                               'score': result.score,
                               'matched_terms': [x[1].decode('utf-8') for x in result.matched_terms()],
                               'highlights_text': result.highlights('text'),
                               'summary_text': f"{result['id']}: {result.score} matches for {', '.join([x[1].decode('utf-8') for x in result.matched_terms()])}"}
                              for result in results]

            return search_results


def create_index(index_dir, text_dir):

    # For example, to add an accent-folding filter to a stemming analyzer:
    my_analyzer = StemmingAnalyzer() | CharsetFilter(accent_map)

    schema = Schema(id=ID(stored=True), 
                    text=TEXT(stored=True, analyzer=my_analyzer))

    if not os.path.exists(index_dir):
        os.mkdir(index_dir)

    ix = index.create_in(index_dir, schema)

    writer = ix.writer()

    (_, _, file_names) = next(os.walk(text_dir))

    for file_name in file_names:
        with open(os.path.join(text_dir, file_name), 'r') as f:
            writer.add_document(
                id=f"{file_name.split('.')[0]}", text=normalize('NFKC', f.read()))

    writer.commit()

    return ix


def remove_index(index_dir):
    """ param <index_dir> could either be relative or absolute. """
    if os.path.isfile(index_dir) or os.path.islink(index_dir):
        os.remove(index_dir)  # remove the file
    elif os.path.isdir(index_dir):
        shutil.rmtree(index_dir)  # remove dir and all contains
    else:
        raise ValueError("file {} is not a file or dir.".format(index_dir))
