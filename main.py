import os
import os.path as osp
import argparse

from utils.bilibili_spider import Bilibili_Spider


def main(args):
    pass

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--uid', type=str, default='562085182')
    parser.add_argument('--save_dir', type=str, default='json')
    args = parser.parse_args()
    print(args)
    
    main(args)
