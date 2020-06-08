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

    def __init__(self):

        if not os.path.exists("indexdir"):
            os.mkdir("indexdir")

        # For example, to add an accent-folding filter to a stemming analyzer:
        my_analyzer = StemmingAnalyzer() | CharsetFilter(accent_map)

        self.schema = Schema(id=ID(stored=True), text=TEXT(stored = True, analyzer=my_analyzer))

        with open('./raw_texts/mn_4.txt', 'r') as f:
            text_4 = normalize('NFKC', f.read())

        with open('./raw_texts/mn_5.txt', 'r') as f:
            text_5 = normalize('NFKC', f.read())

        text_4 = text_4[:593]
        text_5 = text_5[:544]

        self.ix = index.create_in("indexdir", self.schema)
        
        writer = self.ix.writer()
        writer.add_document(id=u"mn_4", text=text_4)
        writer.add_document(id=u"mn_5", text=text_5)
        
        writer.commit()


    def search(self, text, _type='default'):

        def myscore_fn(searcher, fieldname, text, matcher):
            return matcher.value_as("frequency")

        pos_weighting = FunctionWeighting(myscore_fn)
        
        with self.ix.searcher(weighting=pos_weighting) as searcher:
            parser = QueryParser("text", self.schema)
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

