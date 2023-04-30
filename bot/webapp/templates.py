import io

from lxml import etree

html_path = 'bot/webapp/html/'


def parse_html(path) -> etree.ElementTree:
    with open(html_path + path, 'rb') as f:
        return etree.parse(io.BytesIO(f.read()), etree.HTMLParser(encoding='utf-8'))


def read_html(path) -> str:
    with open(html_path + path, 'r', encoding='utf-8') as f:
        return f.read()


def load_from_base_template(path) -> str:
    base_tempalte = read_html('_base_template.html')
    html = read_html(path)
    section_str = html.split('<section>')[-1].split('</section>')[0]
    script_str = html.split('<script>')[-1].split('</script>')[0]
    return (
        base_tempalte
        .replace('<section>\n</section>', f'<section>{section_str}</section>')
        .replace('// INSERT SCRIPT HERE (this line is for templates.py)', script_str)
    )
