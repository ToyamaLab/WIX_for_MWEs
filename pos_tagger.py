import treetaggerwrapper as ttw
import sys

class POSTagger:
    class Token:
        def __init__(self, start, text, pos, lemma):
            self.start = start
            self.text = text
            self.pos = pos
            self.lemma = lemma
    
    def __init__(self, document):
        self.tagger = ttw.TreeTagger(TAGLANG='en')
        self.tokens = []
        self._make_tokens(document)
    
    def _make_tokens(self, document):
        # 構文解析によりword, pos, lemma の情報を取得する
        tags_tabseparated = self.tagger.TagText(document, numlines=True, tagblanks=True)
        start_position = 0

        for tag in tags_tabseparated:
            word_info = tag.split("\t")
            if (len(word_info) == 3):
                # print(start_position, word_info[0], word_info[1], word_info[2])
                new_token = POSTagger.Token(start_position, word_info[0], word_info[1], word_info[2])
                self.tokens.append(new_token)
                start_position += len(word_info[0])
            elif (len(word_info) == 1 and word_info[0][6:11] == "space"):
                # 空白文字が検出されたときの処理。オートマトンに流す文字ではないから、とりあえずstart_positionのインクリメント以外は何も行わない
                # print(start_position, " ")
                start_position += 1
            elif (len(word_info) == 1 and word_info[0][6:10] == "line"):
                # 空白文字が検出されたときの処理。オートマトンに流す文字ではないから、とりあえずstart_positionのインクリメント以外は何も行わない
                if (word_info[0][15:18] != "\"1\""): # 最初の行は何もしない、2行目以降は改行コード分インクリメントする
                    # print(start_position, "\\n")
                    start_position += 1
            else:
                # HTMLタグが普通にそのまま出てくるので、その分だけstart_positionを動かす
                # print(start_position, word_info[0])
                start_position += len(word_info[0])

def main():
    document = "He spent so much time studying English."
    # f = open(sys.argv[1])
    # document = f.read()

    pos = POSTagger(document)
    for token in pos.tokens:
        print(token.start, token.text, token.pos, token.lemma)

if __name__ == "__main__":
    main()