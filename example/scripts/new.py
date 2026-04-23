import markdown
import pathlib
import argparse

NEWS = "content/news/"

parser = argparse.ArgumentParser()

parser.add_argument('-l', '--language')
parser.add_argument('-f', '--file')

args = parser.parse_args()


source_file_path = pathlib.Path(args.file)
data = source_file_path.read_text(encoding='utf-8')
md = markdown.Markdown(extensions=['meta'])
md.convert(data)
date = md.Meta["date"][0][0:10]

index_file_name = "index." + args.language + ".md"

dest_file_path = pathlib.Path(pathlib.Path(NEWS) / date / index_file_name)
source_file_path.rename(dest_file_path)


