import os
import os.path
import shutil
import re
from tqdm import tqdm

import whoosh
from whoosh.compat import text_type
from whoosh import index, highlight, fields
from whoosh.fields import Schema, TEXT, ID
from whoosh.qparser import QueryParser, FuzzyTermPlugin, PhrasePlugin, SequencePlugin
from whoosh.scoring import FunctionWeighting
from whoosh.analysis import CharsetFilter, LowercaseFilter, RegexTokenizer, Token, default_pattern
from whoosh.support.charset import accent_map


class HTMLRegexTokenizer(RegexTokenizer):

    def __call__(self, value, positions=False, chars=False, keeporiginal=False,
                 removestops=True, start_pos=0, start_char=0, tokenize=True,
                 mode='', **kwargs):
        """
        :param value: The unicode string to tokenize.
        :param positions: Whether to record token positions in the token.
        :param chars: Whether to record character offsets in the token.
        :param start_pos: The position number of the first token. For example,
            if you set start_pos=2, the tokens will be numbered 2,3,4,...
            instead of 0,1,2,...
        :param start_char: The offset of the first character of the first
            token. For example, if you set start_char=2, the text "aaa bbb"
            will have chars (2,5),(6,9) instead (0,3),(4,7).
        :param tokenize: if True, the text should be tokenized.
        """

        assert isinstance(value, text_type), "%s is not unicode" % repr(value)
        
        # overwrite all html tags with spaces to preserve the 
        # ability to highlight based on start and end positions
        parsed_value = re.sub("\<[^>]*\>", lambda x: len(x.group(0)) * ' ', value)

        t = Token(positions, chars, removestops=removestops, mode=mode,
                  **kwargs)
        if not tokenize:
            t.original = t.text = parsed_value
            t.boost = 1.0
            if positions:
                t.pos = start_pos
            if chars:
                t.startchar = start_char
                t.endchar = start_char + len(parsed_value)
            yield t
        elif not self.gaps:
            # The default: expression matches are used as tokens
            for pos, match in enumerate(self.expression.finditer(parsed_value)):
                t.text = match.group(0)
                t.boost = 1.0
                if keeporiginal:
                    t.original = t.text
                t.stopped = False
                if positions:
                    t.pos = start_pos + pos
                if chars:
                    t.startchar = start_char + match.start()
                    t.endchar = start_char + match.end()
                yield t
        else:
            # When gaps=True, iterate through the matches and
            # yield the text between them.
            prevend = 0
            pos = start_pos
            for match in self.expression.finditer(parsed_value):
                start = prevend
                end = match.start()
                text = parsed_value[start:end]
                if text:
                    t.text = text
                    t.boost = 1.0
                    if keeporiginal:
                        t.original = t.text
                    t.stopped = False
                    if positions:
                        t.pos = pos
                        pos += 1
                    if chars:
                        t.startchar = start_char + start
                        t.endchar = start_char + end

                    yield t

                prevend = match.end()

            # If the last "gap" was before the end of the text,
            # yield the last bit of text as a final token.
            if prevend < len(parsed_value):
                t.text = parsed_value[prevend:]
                t.boost = 1.0
                if keeporiginal:
                    t.original = t.text
                t.stopped = False
                if positions:
                    t.pos = pos
                if chars:
                    t.startchar = prevend
                    t.endchar = len(parsed_value)
                yield t


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

    def search(self, text, _type='sequence'):

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
                               'header_text': f"{result['id']}: {result.score} matches for {', '.join([x[1].decode('utf-8') for x in result.matched_terms()])}"}
                              for result in results]

            return {'search_results': search_results,
                    'num_results': len(search_results),
                    'chapter_links': '<br>'.join([f"<span class='chapter_link' id='chapter_link-{i}' role='link'>{result['id']} ({result.score})</span>"
                                                 for i, result in enumerate(results)])}


def create_index(index_dir, text_dict):

    # For example, to add an accent-folding filter to a stemming analyzer:
    my_analyzer = HTMLRegexTokenizer() | LowercaseFilter() | CharsetFilter(accent_map)

    schema = Schema(id=ID(stored=True), 
                    text=TEXT(stored=True, analyzer=my_analyzer))

    if not os.path.exists(index_dir):
        os.mkdir(index_dir)

    ix = index.create_in(index_dir, schema)

    writer = ix.writer()

    for title, text in tqdm(text_dict.items(), total=len(text_dict), desc='Creating index'):
        writer.add_document(id=title, text=text)       

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
