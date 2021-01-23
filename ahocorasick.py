# Aho-Corasick法
from pos_tagger import POSTagger

class MachineAC:
    class State:
        def __init__(self, id):
            self.id = id
            self.next = {}
        
        def has_key(self, x):
            return x in self.next
        
        def print_state(self):
            '''
            状態のidと、ラベル・遷移先状態のidの組み合わせを表示する
            '''
            next_state_dict = {}
            for next_key, next_state in self.next.items():
                next_state_dict[next_key] = next_state.id
            print(self.id, next_state_dict)
    
    def __init__(self, terms):
        self.state = [MachineAC.State(0)]
        self.output = [[]] # output関数を配列として用意
        self._make_goto(terms)
        self._make_failure()
    
    # goto関数を構成する、つまりトライ木を作る処理
    def _make_goto(self, idiom_patterns):
        for idiom_pattern in idiom_patterns:
            cur = self.state[0]
            for x in idiom_pattern['pattern']: # xはキーで、('lemma', 'take')とか('pos', 'NN')みたいなタプル
                if not cur.has_key(x): # 状態curが文字xに対応する状態へのキーを持っていなかったら、状態を増やす
                    new = MachineAC.State(len(self.state)) # 新しい状態を作成
                    cur.next[x] = new # 新しい状態を、cur状態の遷移先に追加
                    self.state.append(new) # 新しい状態をstate配列に追加
                    self.output.append([]) # 新しい状態に対応する番号のoutput関数を定義
                cur = cur.next[x]
            s = cur.id
            self.output[s].append(idiom_pattern) # 最終的な状態に対応する番号のoutput関数にキーワードを追加
    
    # failure関数の構成 => 入力1つに対して出力が1つに決まるので、配列によるテーブルで実装
    def _make_failure(self):
        failure = [0] * len(self.state)
        queue = [0]
        while len(queue) > 0:
            s = queue.pop(0)
            for x in self.state[s].next.keys():
                next = self.g(s, x) # 状態sから1つ深い状態
                if next is not None:
                    queue.append(next) # トライ木だから、1つ深い状態は全部queueに追加しちゃってOK
                if s != 0:
                    f = failure[s]
                    while self.g(f, x) is None: # 状態sからxで遷移しない場合、failure関数をたどれるだけたどる
                        f = failure[f]
                    failure[next] = self.g(f, x) # failure関数をたどれるだけたどった状態から文字xで遷移する先の状態, 本の例で言うと, nextが状態s, self.g(f, x)が状態q b 
                    self.output[next].extend(self.output[failure[next]]) # 本の例で言うと、qのoutputがsのoutputにもなる
        
        # 名詞の入力で遷移するような状態に対して、failureリンクを自分にする(skippable)
        for i, each_state in enumerate(self.state):
            for transition_key in each_state.next.keys():
                if (transition_key[0] == "pos" and transition_key[1] == "N"):
                    failure[i] = i

        self.failure = failure
    
    def g(self, s, x):
        if x in self.state[s].next:
            return self.state[s].next[x].id
        else:
            if s == 0:
                return 0
            else:
                return
    
    def match(self, query):
        # s = 0
        document_with_pos = POSTagger(query).tokens
        document_to_be_matched = [document_with_pos]
        # skipped_count = 0
        identified_idioms = []
        while (document_to_be_matched != []):
            s = 0
            skipped_count = 0
            skipped_tokens = []
            matchcing_document = document_to_be_matched.pop(0)

            for i, token in enumerate(matchcing_document):
                """
                tokenの開始位置、元の文字列、品詞タグ、lemma形はそれぞれ次のようにして取り出す
                print(token.start, token.text, token.pos, token.lemma)
                """
                if (token.text == "."):
                    s = 0
                    continue
                
                if (token.pos[0] == "N"):
                    token.pos = token.pos[0]
                while (self.g(s, ("lemma", token.lemma)) is None) and (self.g(s, ("pos", token.pos)) is None):
                    if (s == self.failure[s]): # 元の状態に返ってくる(skip)
                        skipped_tokens.append(token)
                        skipped_count += 1
                        break
                    s = self.failure[s]
                    if (skipped_tokens != []):
                        document_to_be_matched.append(skipped_tokens)
                    skipped_tokens = []
                    skipped_count = 0

                if (self.g(s, ("lemma", token.lemma)) is not None): # lemma形で遷移可能だったら遷移
                    s = self.g(s, ("lemma", token.lemma))
                elif (self.g(s, ("pos", token.pos)) is not None): # posで遷移可能だったら遷移
                    s = self.g(s, ("pos", token.pos))
                
                for x in self.output[s]:
                    # print (matchcing_document[i - (len(x['pattern']) - 1) - skipped_count].start, token.start + len(token.text), x)
                    identified_idioms.append({
                        "start" : matchcing_document[i - (len(x['pattern']) - 1) - skipped_count].start,
                            # skippableにしたとき、ここを修正しないといけないかも
                        "end" : token.start + len(token.text),
                        "idiom" : x,
                        "attachable": True
                    })
                    # skipped_count = 0

        # attachableなイディオムとそうでないものを識別
        identified_idioms = sorted(identified_idioms, key=lambda x: x['start']) # start位置順にソート
        for i in range(1, len(identified_idioms)):
            if (identified_idioms[i - 1]['end'] > identified_idioms[i]['start']):
                if ((identified_idioms[i - 1]['end'] - identified_idioms[i - 1]['start']) >= (identified_idioms[i]['end'] - identified_idioms[i]['start'])):
                    identified_idioms[i]['attachable'] = False
                else:
                    identified_idioms[i - 1]['attachable'] = False
        return identified_idioms
    
    def link(self, document):
        output = ""
        identified_idioms = self.match(document)
        attachable_idioms = [identified_idiom for identified_idiom in identified_idioms if identified_idiom['attachable'] == True] # アタッチ可能なイディオムだけ取り出す
        if (len(attachable_idioms) == 0): # 検出されたイディオムがなかったら、ここで終了
            return document
        
        targetIdiom = attachable_idioms[0]

        for char_idx, char in enumerate(document):
            if (char_idx == targetIdiom['start']): # イディオムの開始位置にきたら、開始タグを追加
                output += '<a href="' + targetIdiom['idiom']['target'] + '" target="_blank">'
                print(targetIdiom)
            
            if (char_idx == targetIdiom['end']): # イディオムの終了位置にきたら、終了タグを追加
                output += '</a>'
                del attachable_idioms[0]
                if (len(attachable_idioms) != 0):
                    targetIdiom = attachable_idioms[0]
            
            output += char
        return output
