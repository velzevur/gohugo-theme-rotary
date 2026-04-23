import os
import re
from argparse import ArgumentParser

def findfiles(path, regex):
    regObj = re.compile(regex)
    res = []
    for root, dirs, fnames in os.walk(path):
        for fname in fnames:
            if regObj.match(fname):
                res.append(os.path.join(root, fname))
    return res

def grep(filepath, regex):
    regObj = re.compile(regex)
    res = []
    with open(filepath) as f:
        for line in f:
            if regObj.match(line):
                res.append(line.strip())
    return res

def parse_list_of_tags(line):
    res = []
    temp_tag = ""
    in_tag = False
    for c in line:
        if(c == "\"" or c == "'"):
            if(not in_tag):
                in_tag = True
            else:
                in_tag = False
                if(temp_tag != ""):
                    res.append(temp_tag)
                    temp_tag = ""
        else:
            if(in_tag):
                temp_tag = temp_tag + c
    return res

def parse_tags(tags):
    trunc = tags[6:]
    parsed = []
    if(trunc[0] == "["):
        trunc = trunc[1: -1]
        parsed = parse_list_of_tags(trunc)
    else:
        if(trunc[0] == '"' or trunc[0] == "'"):
            parsed = [trunc[1:-1]]
        else:
            parsed = [trunc]
    return parsed

def count_uniques(aa):
    return dict(zip(list(aa),[list(aa).count(i) for i in list(aa)]))

parser = ArgumentParser()
parser.add_argument("-l", "--language", dest="language",
                    help="which language to scan",
                    required=True,
                    choices=["bg", "en", "de"])
parser.add_argument("-m", "--mode", dest="mode",
                    default="list",
                    choices=["list", "find"])
parser.add_argument("-v", "--verbose", dest="verbose", default=False)
parser.add_argument("-t", "--tag", dest="tag")
args = parser.parse_args()

files = findfiles("./content/news", r'index\.' + args.language  +'\.md')
all_tags = []
tags_files = {}
for f in files:
    tags_str = grep(f, "tags: ")[0]
    if(args.verbose):
        print(f)
    tags = parse_tags(tags_str)
    all_tags.extend(tags)
    for t in tags:
        ts = tags_files.get(t, [])
        ts.append(f)
        tags_files[t] = ts
    if(args.verbose):
        for t in tags:
            print("     " + t)

if(args.mode == "list"):
    print("All tags")
    for t, cnt in count_uniques(all_tags).items():
        print("     " + t + ": " + str(cnt))

if(args.mode == "find"):
    print("Searching for tag [" + args.tag + "]")
    for f in tags_files.get(args.tag, []):
        print("   " + f)

