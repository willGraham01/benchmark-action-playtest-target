import os
from pathlib import Path

from pyinstrument.session import Session
from pyinstrument.renderers import HTMLRenderer


def render_html(pyis_in: str | Path, html_out: str | Path):
    """
    Renders a pyis session file as HTML for visual output.
    """
    pyi_session = Session.load(pyis_in)
    if not os.path.exists(html_out.parent):
        os.makedirs(html_out.parent)

    renderer = HTMLRenderer(show_all=False, timeline=False)

    print(f"Writing {html_out}", end="...", flush=True)
    with open(html_out, "w") as f:
        f.write(renderer.render(pyi_session))
    print("done")
    return
