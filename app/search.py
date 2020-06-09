import os
from whoosh.fields import Schema, TEXT, ID
from whoosh import index
from unicodedata import normalize
from whoosh.qparser import *
import whoosh
from whoosh.scoring import FunctionWeighting
from whoosh.analysis import CharsetFilter, StemmingAnalyzer
from whoosh import fields
from whoosh.support.charset import accent_map
import os.path


class Search:

    def __init__(self, index_dir, text_dir):

        try:
            self.ix = index.open_dir(index_dir)
        except index.EmptyIndexError:
            self.ix = self.create_index(index_dir, text_dir)

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
            results.formatter = whoosh.highlight.UppercaseFormatter()
            results.fragmenter = whoosh.highlight.WholeFragmenter()

            return [result.highlights('text') for result in results]

    def create_index(self, index_dir, text_dir):

        # For example, to add an accent-folding filter to a stemming analyzer:
        my_analyzer = StemmingAnalyzer() | CharsetFilter(accent_map)

        schema = Schema(id=ID(stored=True), text=TEXT(stored=True, analyzer=my_analyzer))

        if not os.path.exists(index_dir):
            os.mkdir(index_dir)

        ix = index.create_in(index_dir, schema)
        
        writer = ix.writer()

        (_, _, file_names) = next(os.walk(text_dir))       

        for file_name in file_names:
            with open(os.path.join(text_dir, file_name), 'r') as f:
                writer.add_document(id=f"{file_name.split('.')[0]}", text=normalize('NFKC', f.read()))

        writer.commit()

        return ix