import os
import subprocess
from tempfile import NamedTemporaryFile
from textwrap import dedent


def latex_to_html(tex_source: str) -> str:
    """Convert LaTeX source to pretty HTML using Pandoc + MathJax.

    - If the source is a snippet (no \begin{document}), wrap it in a minimal
      document preamble.
    - If the source is a full document, pass it through as-is.
    In both cases ensure there is a closing \end{document}.
    """

    default_preamble = dedent(
        r"""
        \documentclass[11pt]{article}
        \usepackage{amsmath, amssymb}
        \usepackage{graphicx}
        \usepackage{hyperref}
        \usepackage{booktabs}
        \begin{document}
        """
    )

    has_begin = "\\begin{document}" in tex_source
    has_end = "\\end{document}" in tex_source

    if has_begin:
        tex_document = tex_source
    else:
        tex_document = default_preamble + tex_source

    if not has_end:
        tex_document += "\n\\end{document}\n"

    # Temporary .tex file for pandoc
    with NamedTemporaryFile(suffix=".tex", delete=False) as tf:
        tex_path = tf.name
        tf.write(tex_document.encode("utf-8"))

    try:
        # Call pandoc: LaTeX -> HTML with MathJax support
        result = subprocess.run(
            [
                "pandoc",
                tex_path,
                "--from=latex",
                "--to=html",
                "--mathjax",
                "--embed-resources",
                "--strip-comments",
            ],
            check=True,
            capture_output=True,
        )

        html = result.stdout.decode("utf-8")
    except Exception as e:
        # Fallback: show raw LaTeX if pandoc fails
        html = f"""
        <div style="border:1px solid #f00; padding:0.5rem;">
          <strong>LaTeX rendering error:</strong> {e}<br/>
          <pre>{tex_source}</pre>
        </div>
        """

    MATHJAX = """
    <script>
    window.MathJax = {
      tex: { inlineMath: [['$', '$'], ['\\(', '\\)']] },
      svg: { fontCache: 'global' }
    };
    </script>
    <script async src="https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-svg.js"></script>
    """

    styled_html = f"""
    {MATHJAX}
    <style>
      .lab-content {{
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
        line-height: 1.6;
        max-width: 800px;
        margin: 0 auto;
      }}
      .lab-content h1, .lab-content h2, .lab-content h3 {{
        margin-top: 1.5rem;
        margin-bottom: 0.5rem;
      }}
      .lab-content p {{
        margin: 0.4rem 0;
      }}
    </style>

    <div class="lab-content">
      {html}
    </div>
    """

    return styled_html
