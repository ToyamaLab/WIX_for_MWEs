from ahocorasick import MachineAC
import json
import pandas
import sys

def main():
    """
    アタッチする
    """
    # findindexの読み込み（事前に作成したオートマトンを呼び出し）
    ac = pandas.read_pickle("./findindex/findindex.pkl")

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

    f = open(sys.argv[1])
    document = f.read()

    with open("./output.html", mode='w') as f:
        f.write(ac.link(document))
    
if __name__ == "__main__":
    main()
