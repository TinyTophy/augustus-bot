from sympy import preview, symbols


preamble = r'\documentclass{article}\usepackage{xcolor}\begin{document}\color{white}'
tex = r'$$\int_0^1 e^x,dx$$'
f = open('test.tex', 'r').read()
tex = fr'{f}'
print(tex)
# tex = r"""\tableofcontents\pagebreak
# \section{Chapter 1: Basic Notations}
# \subsection{Vector Spaces}
# \begin{problem}{1.1}
# Let $x = (1, 2, 3)^T$, $y = (y_1, y_2, y_3)^T$, $z = (4, 2, 1)^T$. Compute $2x$, $3y$, $x + 2y - 3z$.
# \end{problem}
# \begin{proof}[Solution]
# \begin{align*}
#     2x &= \begin{bmatrix} 2 \\ 4 \\ 6 \end{bmatrix} \\
#     3y &= \begin{bmatrix} 3y_{1} \\ 3y_{2} \\ 3y_{3} \end{bmatrix} \\
#     x + 2y - 3z &= \begin{bmatrix} 1 \\ 2 \\ 3 \end{bmatrix} + 2\begin{bmatrix} y_1 \\ y_2 \\ y_3 \end{bmatrix} - 3\begin{bmatrix} 4 \\ 2 \\ 1 \end{bmatrix} = \begin{bmatrix} 2y_1 - 11 \\ 2y_2 - 4 \\ 2y_3 \end{bmatrix}
# \end{align*}
# \end{proof}"""

preview(tex, viewer='file', filename='tex.png', preamble=preamble, dvioptions=["-T", "tight", "-D 500", "-bg", "Transparent"])
# x, y = symbols("x,y")
# preview(x + y, outputTexFile="sample.tex")

        