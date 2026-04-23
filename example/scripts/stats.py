import markdown
import pathlib
import argparse
from tabulate import tabulate

NEWS = "content/news/"

def list_news():
    p = pathlib.Path(NEWS)
    return [x for x in p.iterdir() if x.is_dir()]

def parse_string(lines):
    if lines:
        str = lines[0]
        str = str.replace('"', '')
        str = str.replace("'", '')
        return str
    else:
        return None;

def parse_bool(lines):
    str = lines[0]
    if str == "true":
        return True
    if str == "false":
        return False

def parse_list(lines):
    str = lines[0]
    all = []
    if str[0] == "[":
        str = str[1:-1]
    for t in str.split(","):
        t = t.strip()
        t = t.replace('"', '')
        t = t.replace("'", '')
        all.append(t)
    return all

def parse(md, raw_data):
    title = parse_string(md["title"])
    draft = parse_bool(md["draft"])
    project = parse_string(md.get("project"))
    date = parse_string(md["date"])[0:10]
    tags = parse_list(md["tags"])
    return {'title': title, 'date': date, 'draft': draft, 'project': project, 'tags': tags, "__original": raw_data}

def get_date(meta):
    return meta['date']

def list_news_by_language(lang):
    index_file_name = "index." + lang + ".md"
    all = []
    for n_dir in list_news():
        file_path = pathlib.Path(n_dir / index_file_name)
        if(file_path.exists()):
            data = file_path.read_text(encoding='utf-8')
            md = markdown.Markdown(extensions=['meta'])
            md.convert(data)
            meta = parse(md.Meta, data)
            all.append(meta)
    all.sort(key=get_date)
    return all

def find_published(lang):
    return [n for n in list_news_by_language(lang) if n['draft'] == False]

def find_unpublished(lang):
    return [n for n in list_news_by_language(lang) if n['draft'] == True]


def print_news(news):
    data = [[n['title'], n['date'], n['project']] for n in news]
    print(tabulate(data, headers=['Title', 'Date', 'Project'], tablefmt='orgtbl'))

parser = argparse.ArgumentParser(
                    prog='helpscript',
                    description='Helper script to parse news and extract certain information')

parser.add_argument('-l', '--language')
parser.add_argument('--published', action='store_true')
parser.add_argument('--unpublished', action='store_true')

# actions
parser.add_argument('--to_translate')
parser.add_argument('--count', action='store_true')
parser.add_argument('--count_tags', action='store_true')

args = parser.parse_args()

if(args.to_translate):
    target_cnt = int(args.to_translate)
    bg_news = list_news_by_language("bg")
    bg_news.reverse()

    full_list = []
    target_news = list_news_by_language(args.language)
    for n in bg_news:
        target_ns = list(filter(lambda x: (x["date"] == n["date"]), target_news))
        cnt = len(target_ns)
        if cnt == 0:
            full_list.append(n)
            print("add article")
            if len(full_list) == target_cnt:
                print("BREAK!")
                break
    print_list = [[n["date"], n["title"]] for n in full_list]
    f = open("translate_" + args.language + ".txt", "w")
    for n in full_list:
        f.write(n["__original"])
        f.write("\n\n\n")
    f.close()
    print(tabulate(print_list, headers=["date", 'Bg'], tablefmt='orgtbl'))

        


else:
    news =[]
    if(args.published):
        news = find_published(args.language)
    if(args.unpublished):
        news = find_unpublished(args.language)
    if((args.published or args.unpublished) == False):
        news = list_news_by_language(args.language)

    if(args.count_tags):
        all_tag_lists= [n["tags"] for n in news]
        tags = []
        for t in all_tag_lists:
            if(isinstance(t, str)):
                tags = []
            else:
                for single_tag in t:
                    tags.append(single_tag)
        tag_counts = dict(zip(list(tags),[list(tags).count(i) for i in list(tags)]))
        data = [[cnt, t] for t, cnt in tag_counts.items()]
        data.sort(reverse=True)
        print(tabulate(data, headers=['Tag', 'Count'], tablefmt='orgtbl'))

    elif(args.count):
        print(len(news))
    else:
        print_news(news)
