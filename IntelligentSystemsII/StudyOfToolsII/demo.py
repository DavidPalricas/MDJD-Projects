from sys import argv
from demo_train import train
from demo_run import run

if __name__ == "__main__":
    # demo.py train => run demo_train.py
    if len(argv) > 1 and argv[1] == "train":
        train()

    # demo.py run => run demo_run.py
    else:
        run()
