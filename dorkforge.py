#!/usr/bin/env python3

import argparse
from pathlib import Path
from urllib.parse import quote


BANNER = r"""
 ____             _     _____
|  _ \  ___  _ __| | __|  ___|__  _ __ __ _  ___
| | | |/ _ \| '__| |/ /| |_ / _ \| '__/ _` |/ _ \
| |_| | (_) | |  |   < |  _| (_) | | | (_| |  __/
|____/ \___/|_|  |_|\_\|_|  \___/|_|  \__, |\___|
                                       |___/
        Authorized Dork Query Generator
"""


CATEGORIES = {
    "basic": [
        'site:{domain}',
        'site:{domain} "{keyword}"',
        'site:{domain} inurl:{keyword}',
        'site:{domain} intitle:{keyword}',
    ],

    "documents": [
        'site:{domain} filetype:pdf',
        'site:{domain} filetype:doc',
        'site:{domain} filetype:docx',
        'site:{domain} filetype:xls',
        'site:{domain} filetype:xlsx',
        'site:{domain} filetype:ppt',
        'site:{domain} filetype:pptx',
        'site:{domain} filetype:txt',
        'site:{domain} filetype:csv',
    ],

    "pages": [
        'site:{domain} inurl:login',
        'site:{domain} inurl:signin',
        'site:{domain} inurl:admin',
        'site:{domain} intitle:login',
        'site:{domain} intitle:dashboard',
        'site:{domain} inurl:portal',
    ],

    "media": [
        'site:{domain} filetype:jpg',
        'site:{domain} filetype:jpeg',
        'site:{domain} filetype:png',
        'site:{domain} filetype:gif',
        'site:{domain} filetype:webp',
    ],

    "code": [
        'site:{domain} filetype:js',
        'site:{domain} filetype:json',
        'site:{domain} filetype:xml',
        'site:{domain} filetype:yaml',
        'site:{domain} filetype:yml',
    ],

    "directories": [
        'site:{domain} intitle:"index of"',
        'site:{domain} "directory listing"',
    ],

    "exclude": [
        'site:{domain} -www',
        'site:{domain} -blog',
        'site:{domain} -shop',
    ],
}


def normalize_domain(domain: str) -> str:
    domain = domain.strip()

    for prefix in (
        "https://",
        "http://",
        "www.",
    ):
        if domain.startswith(prefix):
            domain = domain[len(prefix):]

    domain = domain.split("/")[0]
    domain = domain.strip()

    if not domain:
        raise ValueError("Domain cannot be empty.")

    return domain


def build_queries(domain, categories, keywords=None):
    queries = []

    for category in categories:
        templates = CATEGORIES.get(category, [])

        for template in templates:
            if "{keyword}" in template:
                if keywords:
                    for keyword in keywords:
                        keyword = keyword.strip()
                        if keyword:
                            queries.append(
                                template.format(
                                    domain=domain,
                                    keyword=keyword
                                )
                            )
            else:
                queries.append(template.format(domain=domain))

    return unique(queries)


def unique(items):
    seen = set()
    result = []

    for item in items:
        if item not in seen:
            seen.add(item)
            result.append(item)

    return result


def save_queries(queries, filename):
    path = Path(filename)
    path.write_text(
        "\n".join(queries) + "\n",
        encoding="utf-8"
    )
    return path


def interactive():
    print(BANNER)

    domain = input("Enter authorized domain: ").strip()

    try:
        domain = normalize_domain(domain)
    except ValueError as exc:
        print(f"[!] Error: {exc}")
        return

    print("\nCategories:")
    names = list(CATEGORIES.keys())

    for index, name in enumerate(names, start=1):
        print(f"{index}. {name}")

    raw = input(
        "\nSelect categories "
        "(comma separated, e.g. 1,2,3 or 'all'): "
    ).strip().lower()

    if raw == "all":
        selected = names
    else:
        selected = []

        for value in raw.split(","):
            value = value.strip()

            if value.isdigit():
                index = int(value) - 1

                if 0 <= index < len(names):
                    selected.append(names[index])

        selected = unique(selected)

    if not selected:
        print("[!] No valid categories selected.")
        return

    keyword_input = input(
        "\nCustom keywords (comma separated, optional): "
    ).strip()

    keywords = [
        item.strip()
        for item in keyword_input.split(",")
        if item.strip()
    ]

    queries = build_queries(
        domain,
        selected,
        keywords
    )

    print("\nGenerated dorks:\n")

    for index, query in enumerate(queries, start=1):
        print(f"{index:03}. {query}")

    export = input(
        "\nExport to .txt? [y/N]: "
    ).strip().lower()

    if export == "y":
        filename = input(
            "Filename [dorks.txt]: "
        ).strip() or "dorks.txt"

        path = save_queries(queries, filename)

        print(f"\n[+] Saved {len(queries)} queries to {path}")


def cli():
    parser = argparse.ArgumentParser(
        description="Generate search-engine dork queries for authorized domains."
    )

    parser.add_argument(
        "-d",
        "--domain",
        help="Authorized domain, e.g. example.com"
    )

    parser.add_argument(
        "-c",
        "--categories",
        default="all",
        help="Comma-separated categories or all"
    )

    parser.add_argument(
        "-k",
        "--keywords",
        default="",
        help="Comma-separated custom keywords"
    )

    parser.add_argument(
        "-o",
        "--output",
        help="Export generated queries to a text file"
    )

    args = parser.parse_args()

    if not args.domain:
        interactive()
        return

    domain = normalize_domain(args.domain)

    available = list(CATEGORIES.keys())

    if args.categories.lower() == "all":
        selected = available
    else:
        selected = [
            item.strip().lower()
            for item in args.categories.split(",")
            if item.strip().lower() in CATEGORIES
        ]

    keywords = [
        item.strip()
        for item in args.keywords.split(",")
        if item.strip()
    ]

    queries = build_queries(
        domain,
        selected,
        keywords
    )

    for query in queries:
        print(query)

    if args.output:
        path = save_queries(
            queries,
            args.output
        )

        print(
            f"\n[+] Exported {len(queries)} queries to {path}"
        )


if __name__ == "__main__":
    cli()
