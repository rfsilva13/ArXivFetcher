import arxiv
import pandas as pd
from rich import print
import subprocess
import argparse
import yaml
from yaml import SafeLoader


inputfile = "keywords.yaml"


def read_input_yaml(filename):
    try:
        with open(filename) as f:
            data = yaml.load(f, Loader=SafeLoader)
        return data
    except FileNotFoundError:
        print("File not found")
        return None


def UpdateDatabase(
    input_file=inputfile, DatabaseName="Articles", max_results=20,
):
    data = read_input_yaml(input_file)
    keywords = data["Keywords"]
    categories = data["Categories"]
    cat = f"(cat:{categories[0]}"
    for c in categories[1:]:
        cat += f"+OR+cat:{c}"
    cat += ")"
    dfs = []
    try:
        dfs.append(pd.read_excel(f"{DatabaseName}.xlsx"))
    except:
        ...
    for keyword in keywords:
        search = arxiv.Search(
            query=f"ti:{keyword}",
            max_results=max_results,
            sort_by=arxiv.SortCriterion.SubmittedDate,
        )
        # print(f'ti:{keyword}+AND+{cat}')
        titles, authors, dates, dois, arxivs, links, cat, bib, keywords = (
            [],
            [],
            [],
            [],
            [],
            [],
            [],
            [],
            [],
        )
        for result in search.results():
            titles.append(result.title)
            authors.append(f"{result.authors[0].name} et al.")
            dates.append(result.published.strftime("%d.%b.%Y"))
            dois.append(result.doi)
            arxivs.append(result.pdf_url)
            links.append(result.links[0])
            cat.append(result.primary_category)
            keywords.append(keyword)
            bib.append("Not in .bib")
        Table = {
            "Title": titles,
            "Author": authors,
            "Published": dates,
            "Link": links,
            "Category": cat,
            "bib": bib,
            "Keyword": keywords,
        }
        df = pd.DataFrame(Table)
        dfs.append(df)
        # print(df)
    df = pd.concat(dfs, axis=0, ignore_index=True)
    df = df.drop_duplicates(subset=["Title"])
    df = df.drop_duplicates(subset=["Title"])
    df["Published"] = pd.to_datetime(df["Published"], dayfirst=True)
    df = df.sort_values(by="Published", ascending=True, ignore_index=True)
    df["Published"] = df["Published"].dt.strftime("%d.%b.%Y")
    return df


def Link2bib(df, filename="Articles", print_to_screen=False):
    for i, l in enumerate(df["Link"]):
        if df["bib"][i] == "Not in .bib":
            if str(l)[:17] == "http://dx.doi.org":
                l = str(l).replace(")", "\)")
                l = str(l).replace("(", "\(")
                bashcommand = f"doi2bib {l} >> {filename}.bib"
            else:
                l = str(l).replace(")", "\)")
                l = str(l).replace("(", "\(")
                bashcommand = f"arxivcheck {l} >> {filename}.bib"
            #   if l[]
            if print_to_screen:
                print(bashcommand)
            process = subprocess.run(bashcommand, shell=True, check=True)
            df["bib"][i] = "In .bib"
        else:
            if print_to_screen:
                print(f'{i} {df["Title"][i]} already in .bib')
    return df


def ArXivFetcher(input_file=inputfile, database_name='Articles', max_results=20, filename="Articles", print_to_screen=False):
    df = UpdateDatabase(input_file=input_file, DatabaseName=database_name,  max_results=max_results)
    df = Link2bib(df, filename=filename, print_to_screen=print_to_screen)
    df.to_excel(f"{filename}.xlsx", index=False)
    return df


if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "-inp", "--input", type=str, help="Name of the inputfile used. Defaults to 'input.yaml'.", default="input.yaml"
    )

    parser.add_argument("-m", "--max_results", type=int, help="Number of max results taken for each keyword search. Used to avoid long running times. Default to 20.", default=20)

    parser.add_argument(
        "-f", "--filename", type=str, help="Filename given to the .bib and .xlsx files. Default to 'Articles'.", default="Articles"
    )
    parser.add_argument(
        "-d", "--database", type=str, help="Name of a previous .bib and xlsx files which looks for to try to update, instead of creating a new file.", default=""
    )

    parser.add_argument("-p", "--print", type=bool, help="Controls printing to screen. Defaults to False - meaning that printing is omitted.", default=False)

    args = parser.parse_args()
    df = ArXivFetcher(
        input_file=args.input,database_name=args.database, max_results=args.max_results, filename=args.filename, print_to_screen=args.print
    )
