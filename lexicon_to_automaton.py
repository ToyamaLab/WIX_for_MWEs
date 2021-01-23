import pandas
import json
from pos_tagger import POSTagger
from ahocorasick import MachineAC
import sys

def patterns_detail(pattern_list):
    result = "["
    for each_pattern in pattern_list:
        result += each_pattern.print_pattern() + ","
    result = result[:-1] + "]"
    return result

def main():
    """
    json形式の辞書からACオートマトンを構築して保存する
    """

    """
    辞書構築
    MachineAC構築時に必要なイディオムデータは以下のような形の配列で用意
    idiom_patterns = [["put", "on"], ["on", "time"], ["on", "earth"]]
    """
    file_name = './lexicon/sample_lexicon.json'

    if(sys.argv[1]):
        file_name = sys.argv[1]

    idiom_patterns = []
    json_open = open(file_name, 'r') # 辞書（WIXファイル）を読み込み
    json_data = json.load(json_open)

    for idiom in json_data:
        pos = POSTagger(idiom['pattern']) # 各イディオムパターンを品詞解析
        idiom['pattern'] = ""
        processed_word_counter = 0
        for token in pos.tokens:
            # ホワイトスペースの処理
            if (token.start - processed_word_counter == 1):
                idiom['pattern'] += " "
                processed_word_counter += 1
            
            idiom['pattern'] += token.lemma
            processed_word_counter += len(token.text)
        print(idiom['pattern'])

    for idiom in json_data:
        pattern = []
        for each_word in idiom['pattern'].split():
            if (each_word[0] == "{" and each_word[-1] == "}"):
                pattern.append(("pos", each_word[1:-1].upper()))
            else:
                pattern.append(("lemma", each_word))

        idiom_patterns.append({
            "pattern" : pattern,
            "target" : idiom['target']
        })

    ac = MachineAC(idiom_patterns) # オートマトン構築

    print("goto")
    for each_state in ac.state:
        each_state.print_state()
    print()
    
    print("failure")
    print(ac.failure)
    print()

    print("output")
    print(ac.output)
    print()

    pandas.to_pickle(ac, "./findindex/findindex.pkl") # 外部ファイルにACオブジェクトを保存

if __name__ == "__main__":
    main()