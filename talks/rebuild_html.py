#!/usr/bin/env python3
"""Rebuild talks/index.html with correct titles, keywords, no ZIPs, no topic categories."""

import os
import re
import json
import glob

TALKS_DIR = "/Users/davidspivak/Google Drive/My Drive/_Actual Drive/Math/Talks"
REPO_TALKS = "/Users/davidspivak/VersionControl/dspivak.github.io/talks"

# Manual title overrides for cases where LaTeX-to-plain-text conversion is imperfect
MANUAL_TITLES = {
    "20250715-topos-int-poly": "The double category Int(Poly_+) models control flow and data flow",
    "20230804-act2023": "All concepts are Cat^#",
    "20200707-act": "Poly: an abundant categorical setting for mode-dependent dynamics",
    "20210204-toposcolloquium": "Poly: a category of remarkable abundance",
    "20230109-fra2": "Poly is an unreasonably effective abstraction; Might it relate to healthy systems?",
    # These three had their titles changed because LaTeX had multiple \title{} declarations.
    # The last was the correct one but some may have been given for a specific venue.
    # Use the last (active) \title{}.
    "20150616-nist2015-matriarch": "Protein materials architecture by design",
    "20150605-fmcs2015": "Operads as a language for modular design",
    "20150129-afosr2015review": "A mathematical language for modular systems",
    # Lightning talk with no .tex file
    "20260123-nitmb-lightning-talk": "Achieving answerability",
    # Old talks that embedded venue+date in \title{}
    "20160407-suny-binghamton20160407": "Calculating steady states of nonlinear dynamical systems using matrix arithmetic",
    "20120000-ut": "Categorical databases",
    "20110000-uiuc": "Categorical Information Theory",
    "20110000-jhu": "Categorical Information Theory",
    "20100915-mit-linguistics": "Communication networks",
    "20100000-chicago": "Topology and information",
}

# Venue display names for all talks.
# Sources: extracted from \includevenue{}, \institute{}, \date{}, \begin{center} on title slides,
# or inferred from directory names where no venue appears in the .tex file.
VENUE_OVERRIDES = {
    # 2026
    "20260317-nitmb-colloquium": "NITMB Colloquium",
    "20260123-nitmb-lightning-talk": "NITMB: Expanding the Palette of Mathematics in Biology",
    "20260121-nitmb-tutorial": "NITMB: Expanding the Palette of Mathematics in Biology",
    # 2025
    "20250715-topos-int-poly": "Topos Berkeley Seminar",
    # 2024
    "20241202-mit": "MIT CEE: ACT4ED",
    "20241105-ipam-naturalisticai": "IPAM Naturalistic Approaches to AI",
    "20241009-mathgov": "MathGov",
    "20240815-agi": "AGI 2024",
    "20240709-fmcs": "FMCS 2024",
    "20240617-act2024": "ACT 2024",
    "20240417-princeton-astera": "Princeton Neuroscience of Cognitive Control and Astera",
    "20240410-princeton-astera": "Princeton Neuroscience of Cognitive Control and Astera",
    "20240307-calgary": "Annual Mathematics and Philosophy Lecture, University of Calgary",
    # 2023
    "20231214-caltech": "Caltech, Special Seminar in Mechanical and Civil Engineering",
    "20231011-chevron": "Chevron Systems Engineering Community of Practice",
    "20230804-act2023": "Applied Category Theory 2023",
    "20230725-societymfr": "Society for Multidisciplinary and Fundamental Research, Interdisciplinary School",
    "20230416-consciousness": "Category Theory for Consciousness Science",
    "20230323-catsforai": "Categories for AI",
    "20230221-topos": "Topos Berkeley Seminar",
    "20230109-fra2": "Finding the Right Abstractions for Healthy Systems",
    "20230105-jmm": "Joint Mathematics Meetings, Special Session on Applied Category Theory",
    # 2022
    "20221212-topos": "Topos Berkeley Seminar",
    "20221103-nist": "NIST, Compositional Structures in Systems Engineering and Design Workshop",
    "20221020-nasa-pce3": "NASA Prebiotic Chemistry and Evolution on the Early Earth (PCE3)",
    "20220913-actinf": "Active Inference Institute",
    "20220719-act": "ACT 2022",
    "20220614-topos-scotttopology": "Topos Institute, Berkeley Seminar",
    "20220607-levin": "Allen Discovery Center",
    "20220513-scse": "Symposium on Categorical Semantics of Entropy",
    "20220406-pisa": "University of Pisa, Computer Science Department",
    "20220318-pfunc": "Workshop on Polynomial Functors",
    "20220219-ipam": "Mathematics of Collective Intelligence",
    "20220125-intercats": "Seminar on Categorical Interaction",
    # 2021
    "20210921-toposinternal": "Topos Internal Seminar",
    "20210315-pfunc": "Workshop on Polynomial Functors",
    "20210217-unam": "Seminario de categorias UNAM",
    "20210204-toposcolloquium": "Topos Colloquium",
    "20210202-pnnl": "PNNL",
    "20210000-topos-fra-workshop-tutorial": "Finding the Right Abstractions, Topos Institute",
    "20210000-topos-fra-workshop-cultivatingstrategies": "Finding the Right Abstractions, Topos Institute",
    # 2020
    "20200707-act": "ACT 2020",
    "20200625-tallinn": "Tallinn CS Theory Seminar",
    "20200612-agi": "AGI 2020",
    "20200607-internalvaluations2020": "Categorical Probability and Statistics",
    "20200528-mit": "MIT Categories Seminar",
    "20200305-modedependent": "MIT",
    # 2019
    "20190925-eth": "ETH Zurich",
    "20190719-act2019-short": "ACT 2019",
    "20190711-ct2019": "CT 2019",
    "20190624-compose20190625": "Compose Conference",
    "20190523-monadicdecisionprocesses": "MIT CT Seminar",
    "20190509-oxford-fhi": "Oxford, Future of Humanity Institute",
    "20190509-mit-aso": "MIT ASO",
    "20190509-bridgewater": "Bridgewater",
    "20190422-uber": "Uber",
    "20190411-mit20190411": "MIT ACT Seminar",
    "20190311-ut-austin": "UT Austin",
    "20190227-moderna": "Moderna",
    "20190227-kensho": "Kensho",
    "20190110-petribanks": "MIT",
    "20190109-bae": "BAE Systems",
    "20190000-riverside2019": "UC Riverside",
    "20190000-mit20190502": "MIT CT Seminar",
    "20190000-mit2019": "MIT",
    "20190000-mcgill2019": "McGill University",
    # 2018
    "20181027-graphicallogic-octoberfest201810": "Octoberfest",
    "20181001-institutions": "MIT",
    "20180928-umcp-isr": "Institute of Systems Research, UMD",
    "20180823-doublecategories": "MIT Applied CT Seminar",
    "20180719-decompositionspaces": "MIT CT Seminar",
    "20180709-ct2018": "Category Theory Conference",
    "20180506-maxplanck2018": "Max Planck Institute",
    "20180502-act-lorentz2018": "Applied Category Theory Workshop, Lorentz Center",
    "20180426-discrete": "MIT CT Seminar",
    "20180412-graphicallogic-mit201804": "MIT",
    "20180316-toposescomo2018-talk": "Toposes in Como",
    "20180316-nist2018": "NIST Applied Category Theory Workshop",
    "20180316-cmu2019": "CMU",
    "20180316-barcelona2018": "Barcelona",
    "20180222-metricrealization": "MIT Applied CT Seminar",
    "20180201-oxford2018": "Oxford OASIS",
    "20180000-graphicallogic-mit201811": "MIT CT Seminar",
    # 2017
    "20171212-salemstate": "Salem State University",
    "20171104-uc-riverside2017": "AMS Fall Sectional, Riverside CA",
    "20171024-harvardmathtable": "Harvard Math Table",
    "20171002-mit-del-vecchio": "MIT",
    "20171002-mcgill": "McGill Applied Mathematics Seminar",
    "20171002-caltech": "Caltech, AMBER Lab Seminar",
    "20170905-mit-ct-seminar": "MIT CT Seminar",
    "20170713-siam-pa-2017": "SIAM",
    "20170712-siam2017": "SIAM, Novel Approaches for Systems of Systems",
    "20170612-barcelona2017": "UAB Topology Seminar, Barcelona",
    "20170608-lorentz2017": "Emerging Topics in Network Dynamical Systems, Lorentz Center",
    "20170329-broad": "Broad Institute",
    "20170130-iap2017": "MIT Mathematics IAP Lecture Series",
    "20170000-lambdaconf": "LambdaConf",
    # 2016
    "20161205-simons2016-presentation": "Compositionality Workshop, Simons Institute for the Theory of Computing",
    "20161110-telecombretagne-2": "Telecom Bretagne",
    "20161110-telecombretagne": "Telecom Bretagne",
    "20161026-numericalpde-mit": "MIT Numerical Methods for PDE Seminar",
    "20161004-sandia": "Sandia National Labs",
    "20160629-daytonafrl2016-06-29": "Air Force Research Laboratory, Dayton",
    "20160615-socg2016": "5th Mini-Symposium on Computational Topology, SoCG",
    "20160407-suny-binghamton20160407": "Binghamton University Mathematics Colloquium",
    "20160322-ohiombi2016": "Mathematical Biosciences Institute, The Ohio State University",
    "20160000-siam2016-didnt-occur": "SIAM (did not occur)",
    "20160000-ct2016-talk": "Toposes in Como",
    "20160000-ct2016": "Category Theory 2016",
    # 2015
    "20151028-nist2015-cct": "NIST Computational Category Theory Workshop",
    "20150617-nist2015-modularity": "NIST",
    "20150616-nist2015-matriarch": "NIST",
    "20150605-fmcs2015": "FMCS 2015",
    "20150403-upenn2015": "University of Pennsylvania, Complex Systems Seminar",
    "20150129-afosr2015review": "AFOSR Program Review",
    "20150126-design-theory-sig-2015": "8th Design Theory SIG Paris Workshop",
    "20150000-turin2015": "Workshop in Turin",
    "20150000-lids": "MIT LIDS",
    "20150000-lausanne": "Ecole Polytechnique Federale de Lausanne",
    # 2014
    "20140320-ias": "Institute for Advanced Study",
    "20140304-amgen": "Amgen",
    "20140303-parc": "PARC",
    "20140228-oracle": "Oracle",
    "20140225-uiuc2014-02-25": "UIUC",
    "20140219-statemachines": "MIT",
    "20140219-old-usingsafe": "MIT",
    "20140219-old-frp": "MIT",
    "20140219-mit20140415": "MIT (PLV Lunch)",
    "20140219-harvard2014-02-19": "Harvard University",
    "20140219-amgen": "Amgen",
    "20140123-cmu2014-01-23": "Carnegie Mellon University",
    # 2013
    "20130613-nist-2013-06-12": "National Institute of Standards and Technology",
    # 2012
    "20120804-mathfest": "MathFest",
    "20120726-stanford": "Stanford Center for Biomedical Research",
    "20120613-onr-2012-06-13": "Office of Naval Research",
    "20120124-amgen": "Amgen",
    "20120113-j-j": "Johnson & Johnson",
    "20120113-introductory-talk": "MIT",
    "20120000-ut": "Special Geometry Seminar, UT Austin",
    # 2011
    "20110118-cmu": "Carnegie Mellon University",
    "20110000-uiuc": "MSS Colloquium, UIUC",
    "20110000-jhu": "Topology Seminar, JHU",
    # 2010
    "20101103-harvard": "Harvard University",
    "20101022-galois": "Galois",
    "20100916-csail": "MIT CSAIL",
    "20100915-mit-linguistics": "MIT Linguistics, Semantics Reading Group",
    "20100603-galois": "Galois",
    "20100000-chicago": "University of Chicago",
    # 2009
    "20091107-quasi-categories": "University of Oregon",
}

# Slugs that are NOT beamer slides (outlines, notes, articles)
# These get "Outline (PDF)" instead of "Slides (PDF)"
NON_SLIDES = {
    # memoir class
    "20250715-topos-int-poly",
    "20230221-topos",
    "20221212-topos",
    "20220614-topos-scotttopology",
    "20200305-modedependent",
    "20190523-monadicdecisionprocesses",
    "20190110-petribanks",
    "20190000-mit20190502",
    "20190000-mcgill2019",
    "20181001-institutions",
    "20180823-doublecategories",
    "20180719-decompositionspaces",
    "20180506-maxplanck2018",
    "20180426-discrete",
    "20180412-graphicallogic-mit201804",
    "20180316-toposescomo2018-talk",
    "20180222-metricrealization",
    "20180201-oxford2018",
    "20180000-graphicallogic-mit201811",
    "20171024-harvardmathtable",
    "20170905-mit-ct-seminar",
    "20170000-lambdaconf",
    "20160615-socg2016",
    "20160407-suny-binghamton20160407",
    "20151028-nist2015-cct",
    "20150000-lausanne",
    # article class
    "20241009-mathgov",
    "20160000-ct2016",
    "20150000-turin2015",
    "20150000-lids",
    # amsart class
    "20140320-ias",
    "20140225-uiuc2014-02-25",
    "20120000-ut",
    "20110000-uiuc",
    "20110000-jhu",
    "20100915-mit-linguistics",
    "20100000-chicago",
    # no documentclass / no tex
    "20160629-daytonafrl2016-06-29",
    "20160000-siam2016-didnt-occur",
}

# YouTube links keyed by PDF slug prefix (YYYYMMDD-venue)
YOUTUBE = {
    "20260317-nitmb-colloquium": "https://www.youtube.com/watch?v=1VmsZC8SNTM",
    "20260121-nitmb-tutorial": "https://www.youtube.com/watch?v=gibW0NzbZk0",
    "20241202-mit": "https://www.youtube.com/watch?v=sa50SYMHE90",
    "20241105-ipam-naturalisticai": "https://www.youtube.com/watch?v=wDB26DFATAU",
    "20240815-agi": "https://www.youtube.com/live/Me187k6RQlQ?t=17223s",
    "20230725-societymfr": "https://www.youtube.com/watch?v=K3NYTZxXbgM",
    "20230416-consciousness": "https://www.youtube.com/watch?v=QGGQRO0OSaI",
    "20230323-catsforai": "https://www.youtube.com/watch?v=Z5fdB6aUNBw",
    "20220913-actinf": "https://www.youtube.com/watch?v=aN1GXOZp6xY",
    "20220607-levin": "https://www.youtube.com/watch?v=DpAi-rtnjTM",
    "20220513-scse": "https://www.youtube.com/watch?v=3UtjRs3TsqQ",
    "20220318-pfunc": "https://www.youtube.com/watch?v=bzBbOV2pCGE",
    "20210315-pfunc": [
        ("Video Part 1", "https://www.youtube.com/watch?v=B8STLcbEGrE"),
        ("Video Part 2", "https://www.youtube.com/watch?v=_cckUQB6r-I"),
    ],
    "20210217-unam": "https://www.youtube.com/watch?v=A-ZrWMEpR7U",
    "20210204-toposcolloquium": "https://www.youtube.com/watch?v=Cp5_o2lDqj0",
    "20190624-compose20190625": "https://www.youtube.com/watch?v=Ft0_l_PPO4w",
    "20180502-act-lorentz2018": "https://www.youtube.com/watch?v=KCrlm8WsItE",
}

# LaTeX math macro expansions for plain text rendering
MATH_REPLACEMENTS = [
    # Common custom macros in Spivak's talks
    (r'\\catsharp', 'Cat^#'),
    (r'\\Cat\{Poly\}', 'Poly'),
    (r'\\Cat\{Set\}', 'Set'),
    (r'\\Cat\{Cat\}', 'Cat'),
    (r'\\Cat\{Org\}', 'Org'),
    (r'\\Cat\{Grph\}', 'Grph'),
    (r'\\Cat\{Coalg\}', 'Coalg'),
    (r'\\Cat\{CoAlg\}', 'CoAlg'),
    (r'\\Cat\{Copara\}', 'Copara'),
    (r'\\Cat\{Para\}', 'Para'),
    (r'\\Cat\{Lens\}', 'Lens'),
    (r'\\Cat\{Optic\}', 'Optic'),
    (r'\\Cat\{Fin\}', 'Fin'),
    (r'\\Cat\{FinSet\}', 'FinSet'),
    (r'\\Cat\{Rel\}', 'Rel'),
    (r'\\Cat\{Mon\}', 'Mon'),
    (r'\\Cat\{Cmd\}', 'Cmd'),
    (r'\\Cat\{Ccmd\}', 'Ccmd'),
    (r'\\Cat\{Mnd\}', 'Mnd'),
    (r'\\Cat\{Cmnd\}', 'Cmnd'),
    (r'\\Cat\{Alg\}', 'Alg'),
    (r'\\IInt', 'Int'),
    (r'\\Cat\{Int\}', 'Int'),
    (r'\\Cat\{Aut\}', 'Aut'),
    (r'\\Cat\{Comon\}', 'Comon'),
    (r'\\Cat\{Span\}', 'Span'),
    (r'\\Cat\{Cospan\}', 'Cospan'),
    (r'\\poly\b(\[\])?', 'Poly'),
    (r'\\sspan', 'Span'),
    (r'\\ccospan', 'Cospan'),
    (r'\\NN', 'N'),
    (r'\\RR', 'R'),
    (r'\\ZZ', 'Z'),
    (r'\\QQ', 'Q'),
    (r'\\CC', 'C'),
    (r'\\FF', 'F'),
    (r'\\BB', 'B'),
    (r'\\oo', 'o'),
    (r'\\shp', '^#'),
    (r'\\sharp', '#'),
    (r'\\flat', 'b'),
    (r'\\natural', 'nat'),
    # Standard LaTeX
    (r'\\mathbb\{([^}]+)\}', r'\1'),
    (r'\\mathbf\{([^}]+)\}', r'\1'),
    (r'\\mathcal\{([^}]+)\}', r'\1'),
    (r'\\mathrm\{([^}]+)\}', r'\1'),
    (r'\\mathsf\{([^}]+)\}', r'\1'),
    (r'\\textbf\{([^}]+)\}', r'\1'),
    (r'\\textit\{([^}]+)\}', r'\1'),
    (r'\\textsf\{([^}]+)\}', r'\1'),
    (r'\\emph\{([^}]+)\}', r'\1'),
    (r'\\operatorname\{([^}]+)\}', r'\1'),
    (r'\\text\{([^}]+)\}', r'\1'),
    (r'\\ensuremath\{([^}]+)\}', r'\1'),
    (r'\\quad', ' '),
    (r'\\qquad', '  '),
    (r'\\;', ' '),
    (r'\\,', ''),
    (r'\\!', ''),
    (r'\\&', '&'),
    (r'\\\\', ' '),
    (r'\\smallskip', ''),
    (r'\\medskip', ''),
    (r'\\bigskip', ''),
    (r'\\Huge\b', ''),
    (r'\\huge\b', ''),
    (r'\\large\b', ''),
    (r'\\Large\b', ''),
    (r'\\LARGE\b', ''),
    (r'\\small\b', ''),
    (r'\\footnotesize\b', ''),
    (r'\\tiny\b', ''),
    (r'\\normalsize\b', ''),
    (r'\\vspace\{[^}]*\}', ''),
    (r'\\hspace\{[^}]*\}', ''),
    (r'\\noindent\b', ''),
    (r'\^\{\\sharp\}', '^#'),
    (r'\^\{\\#\}', '^#'),
    (r'\$([^$]*)\$', r'\1'),  # strip dollar signs last
    (r'\\to\b', '->'),
    (r'\\rightarrow\b', '->'),
    (r'\\leftarrow\b', '<-'),
    (r'\\Rightarrow\b', '=>'),
    (r'\\Leftarrow\b', '<='),
    (r'\\times\b', 'x'),
    (r'\\otimes\b', 'x'),
    (r'\\oplus\b', '+'),
    (r'\\circ\b', 'o'),
    (r'\\sim\b', '~'),
    (r'\\approx\b', '~'),
    (r'\\cong\b', '~='),
    (r'\\simeq\b', '~='),
    (r'\\equiv\b', '='),
    (r'\\leq\b', '<='),
    (r'\\geq\b', '>='),
    (r'\\neq\b', '!='),
    (r'\\infty\b', 'infinity'),
    (r'\\ldots\b', '...'),
    (r'\\cdots\b', '...'),
    (r'\\dots\b', '...'),
    (r'\\forall\b', 'for all'),
    (r'\\exists\b', 'exists'),
    (r'\\in\b', 'in'),
    (r'\\subset\b', 'subset'),
    (r'\\subseteq\b', 'subset'),
    (r'\\cup\b', 'U'),
    (r'\\cap\b', 'cap'),
    (r'\\emptyset\b', 'emptyset'),
    (r'\\lambda\b', 'lambda'),
    (r'\\Lambda\b', 'Lambda'),
    (r'\\alpha\b', 'alpha'),
    (r'\\beta\b', 'beta'),
    (r'\\gamma\b', 'gamma'),
    (r'\\delta\b', 'delta'),
    (r'\\epsilon\b', 'epsilon'),
    (r'\\sigma\b', 'sigma'),
    (r'\\Sigma\b', 'Sigma'),
    (r'\\pi\b', 'pi'),
    (r'\\Pi\b', 'Pi'),
    (r'\\omega\b', 'omega'),
    (r'\\Omega\b', 'Omega'),
    (r'\\mu\b', 'mu'),
    (r'\\eta\b', 'eta'),
    (r'\\theta\b', 'theta'),
    (r'\\kappa\b', 'kappa'),
    (r'\\tau\b', 'tau'),
    (r'\\phi\b', 'phi'),
    (r'\\psi\b', 'psi'),
    (r'\\chi\b', 'chi'),
    (r'\\rho\b', 'rho'),
    (r'\\nu\b', 'nu'),
    (r'\\varphi\b', 'phi'),
    (r'\\varepsilon\b', 'epsilon'),
    (r'  +', ' '),
]


def latex_to_plain(s):
    """Convert LaTeX string to plain text."""
    if not s:
        return s
    # First resolve any \Cat{...} with optional subscript
    for pattern, repl in MATH_REPLACEMENTS:
        s = re.sub(pattern, repl, s)
    # Remove remaining LaTeX commands we didn't catch
    s = re.sub(r'\\[a-zA-Z]+\b\s*', '', s)
    # Clean up braces
    s = s.replace('{', '').replace('}', '')
    # Clean up multiple spaces
    s = re.sub(r'\s+', ' ', s).strip()
    # Clean up weird artifacts
    s = s.replace(' ,', ',').replace(' .', '.').replace(' :', ':')
    # Fix double colons from linebreak removal
    s = re.sub(r':\s*:', ':', s)
    return s


def extract_title_from_tex(tex_content):
    """Extract the LAST \\title{...} from a .tex file (last one wins in LaTeX).
    Skips commented-out \\title lines."""
    # First, remove all comment lines (lines starting with %)
    lines = tex_content.split('\n')
    clean_lines = []
    for line in lines:
        # Remove inline comments but keep the part before %
        # Be careful not to strip \% (escaped percent)
        stripped = line.lstrip()
        if stripped.startswith('%'):
            continue  # skip fully commented lines
        clean_lines.append(line)
    tex_clean = '\n'.join(clean_lines)

    # Find all \title{...} or \title[...]{...} occurrences
    titles = []
    idx = 0
    while True:
        # Match \title optionally followed by [...] then {
        match = re.search(r'\\title\s*(?:\[[^\]]*\])?\s*\{', tex_clean[idx:])
        if not match:
            break
        start = idx + match.end()  # position after the opening {
        # Find the matching closing brace
        depth = 1
        pos = start
        while pos < len(tex_clean) and depth > 0:
            if tex_clean[pos] == '{':
                depth += 1
            elif tex_clean[pos] == '}':
                depth -= 1
            pos += 1
        if depth == 0:
            title_content = tex_clean[start:pos-1]
            # Remove any remaining inline comments
            title_content = re.sub(r'(?<!\\)%.*$', '', title_content, flags=re.MULTILINE)
            titles.append(title_content.strip())
        idx = pos

    if titles:
        # Use the last \title{} (that's what LaTeX does)
        raw_title = titles[-1]
        return latex_to_plain(raw_title)
    return None


def extract_frame_titles(tex_content):
    """Extract frame titles from \\ft{...}{, \\fst{...}{, \\frametitle{...}, \\begin{frame}{...}."""
    frame_titles = []

    # Pattern 1: \ft{Title}{ or \fst{Title}{
    for m in re.finditer(r'\\f(?:s)?t\{', tex_content):
        start = m.end()
        depth = 1
        pos = start
        while pos < len(tex_content) and depth > 0:
            if tex_content[pos] == '{':
                depth += 1
            elif tex_content[pos] == '}':
                depth -= 1
            pos += 1
        if depth == 0:
            title = tex_content[start:pos-1].strip()
            if title and title != 'Outline':
                frame_titles.append(latex_to_plain(title))

    # Pattern 2: \frametitle{...}
    for m in re.finditer(r'\\frametitle\{', tex_content):
        start = m.end()
        depth = 1
        pos = start
        while pos < len(tex_content) and depth > 0:
            if tex_content[pos] == '{':
                depth += 1
            elif tex_content[pos] == '}':
                depth -= 1
            pos += 1
        if depth == 0:
            title = tex_content[start:pos-1].strip()
            if title and title != 'Outline' and title not in [latex_to_plain(t) for t in frame_titles[:5]]:
                frame_titles.append(latex_to_plain(title))

    # Pattern 3: \begin{frame}{Title}
    for m in re.finditer(r'\\begin\{frame\}\{', tex_content):
        start = m.end()
        depth = 1
        pos = start
        while pos < len(tex_content) and depth > 0:
            if tex_content[pos] == '{':
                depth += 1
            elif tex_content[pos] == '}':
                depth -= 1
            pos += 1
        if depth == 0:
            title = tex_content[start:pos-1].strip()
            if title and title != 'Outline':
                frame_titles.append(latex_to_plain(title))

    return frame_titles


def summarize_keywords(frame_titles, max_keywords=8):
    """From a list of frame titles, produce a concise keyword list."""
    if not frame_titles:
        return []

    # Filter out meta/structural titles
    skip_patterns = [
        r'^plan\b', r'^outline\b', r'^overview\b', r'^summary\b',
        r'^why am i here', r'^who am i', r'^about me', r'^thank',
        r'^references\b', r'^bibliography\b', r'^acknowledgment',
        r'^questions\b', r'^discussion\b', r'^conclusion\b',
        r'^brainstorm\b', r'^plan for', r'^plan of',
        r'^what will we', r'^what we\'ll', r'^goals?\b',
        r'^review\b', r'^recap\b', r'^reminder\b',
        r'^the end\b', r'^end\b', r'^$',
    ]
    filtered = []
    for t in frame_titles:
        t_lower = t.lower().strip()
        if any(re.search(p, t_lower) for p in skip_patterns):
            continue
        if len(t) < 3:
            continue
        filtered.append(t)

    # Deduplicate
    seen = set()
    unique = []
    for t in filtered:
        t_norm = t.lower().strip()
        if t_norm not in seen:
            seen.add(t_norm)
            unique.append(t)

    # Take a selection of titles spread across the talk
    if len(unique) <= max_keywords:
        return unique

    # Pick evenly spaced titles
    step = len(unique) / max_keywords
    selected = []
    for i in range(max_keywords):
        idx = int(i * step)
        selected.append(unique[idx])
    return selected


def find_tex_files(directory):
    """Find all .tex files in a directory."""
    tex_files = []
    for f in os.listdir(directory):
        if f.endswith('.tex') and not f.startswith('.'):
            tex_files.append(os.path.join(directory, f))
    return tex_files


def read_manifest():
    """Read the existing manifest.json for structure info."""
    manifest_path = os.path.join(REPO_TALKS, "manifest.json")
    if os.path.exists(manifest_path):
        with open(manifest_path) as f:
            return json.load(f)
    return []


def find_source_tex(source_dir):
    """Find and read .tex file(s) for a talk source directory."""
    full_path = os.path.join(TALKS_DIR, source_dir)
    if not os.path.isdir(full_path):
        return None
    tex_files = find_tex_files(full_path)
    if not tex_files:
        return None
    # Prefer the main .tex file (largest, or the one with \documentclass)
    best = None
    best_size = 0
    for tf in tex_files:
        try:
            with open(tf, 'r', errors='replace') as f:
                content = f.read()
            if '\\documentclass' in content or '\\begin{document}' in content:
                size = len(content)
                if size > best_size:
                    best = content
                    best_size = size
        except:
            continue
    if best is None and tex_files:
        # Just use the largest one
        for tf in tex_files:
            try:
                with open(tf, 'r', errors='replace') as f:
                    content = f.read()
                if len(content) > best_size:
                    best = content
                    best_size = len(content)
            except:
                continue
    return best


def html_escape(s):
    """Escape HTML special characters."""
    return (s.replace('&', '&amp;')
             .replace('<', '&lt;')
             .replace('>', '&gt;')
             .replace('"', '&quot;')
             .replace("'", '&#x27;'))


def generate_html(entries):
    """Generate the complete index.html."""
    header = """
<html>

<head>

<title>David Spivak -- Talks</title>

<meta name="description" content="Talks and presentations by David Spivak on category theory, polynomial functors, databases, wiring diagrams, and related topics.">

<meta name="keywords" content="David Spivak, category theory, talks, presentations,
polynomial functors, applied category theory, databases, wiring diagrams">

<script type="text/javascript">

  var _gaq = _gaq || [];
  _gaq.push(['_setAccount', 'UA-28355043-1']);
  _gaq.push(['_trackPageview']);

  (function() {
    var ga = document.createElement('script'); ga.type =
'text/javascript'; ga.async = true;
    ga.src = ('https:' == document.location.protocol ? 'https://ssl' :
'http://www') + '.google-analytics.com/ga.js';
    var s = document.getElementsByTagName('script')[0];
s.parentNode.insertBefore(ga, s);
  })();

</script>
</head>

<body>

<img src="../David_Cropped.jpg" align=right width="270"/>
<h1><a href="http://dspivak.net/">David
Spivak</a></h1>

<h2>Talks</h2>

A chronological listing of talks and presentations. Each entry includes a downloadable PDF of the slides or outline.

<hr>

"""

    footer = """
<hr>

<br><br>

<a rel="license"
href="http://creativecommons.org/licenses/by-sa/3.0/"><img alt="Creative
Commons License" style="border-width:0"
src="http://i.creativecommons.org/l/by-sa/3.0/88x31.png" /></a><br />This
<span xmlns:dc="http://purl.org/dc/elements/1.1/"
href="http://purl.org/dc/dcmitype/Text" rel="dc:type">work</span> by <span
xmlns:cc="http://creativecommons.org/ns#"
property="cc:attributionName">David I. Spivak</span> is licensed under a
<a rel="license"
href="http://creativecommons.org/licenses/by-sa/3.0/">Creative Commons
Attribution-Share Alike 3.0 Unported License</a>.

</body>
</html>
"""

    lines = [header]
    current_year = None

    for entry in entries:
        date = entry["date"]
        year = date[:4] if date else "0000"

        if year != current_year:
            if current_year is not None:
                lines.append("")
            lines.append(f"\n<h3>{year}</h3>\n")
            current_year = year

        title = html_escape(entry.get("title_corrected", entry.get("title", "(Untitled)")))
        venue = html_escape(entry.get("venue_display", entry.get("venue", "")))
        slug = entry["slug"]
        pdf_file = entry.get("pdf_file", "")

        # Date display
        if date.endswith("0000") or date == "0000":
            date_display = year
        else:
            date_display = date

        lines.append("<p>")
        lines.append(f"<b>{title}</b><br>")
        if date_display == year:
            lines.append(f"{venue}, {year}")
        else:
            lines.append(f"{venue}, {date_display}")

        # Links line
        link_parts = []
        if pdf_file:
            pdf_label = "Outline (PDF)" if slug in NON_SLIDES else "Slides (PDF)"
            link_parts.append(f'<a href="./pdfs/{pdf_file}">{pdf_label}</a>')

        # YouTube link
        yt = YOUTUBE.get(slug)
        if yt:
            if isinstance(yt, list):
                for label, url in yt:
                    link_parts.append(f'<a href="{url}">{label}</a>')
            else:
                link_parts.append(f'<a href="{yt}">Video (YouTube)</a>')

        if link_parts:
            lines.append("<br>" + " | ".join(link_parts))

        # Keywords
        keywords = entry.get("keywords_new", [])
        if keywords:
            kw_str = html_escape(", ".join(keywords))
            lines.append(f'<br><small>Keywords: {kw_str}</small>')

        lines.append("</p>\n")

    lines.append(footer)
    return "\n".join(lines)


def main():
    manifest = read_manifest()
    print(f"Loaded {len(manifest)} entries from manifest")

    updated_entries = []
    title_changes = []

    for entry in manifest:
        source_dir = entry.get("source_dir", "")
        old_title = entry.get("title", "(Untitled)")

        # Read .tex file
        tex_content = find_source_tex(source_dir)
        new_title = None
        keywords = []

        if tex_content:
            new_title = extract_title_from_tex(tex_content)
            frame_titles = extract_frame_titles(tex_content)
            keywords = summarize_keywords(frame_titles)

        # Check for manual override first
        slug = entry["slug"]
        if slug in MANUAL_TITLES:
            entry["title_corrected"] = MANUAL_TITLES[slug]
            if MANUAL_TITLES[slug] != old_title:
                title_changes.append((slug, old_title, MANUAL_TITLES[slug], "MANUAL"))
        elif new_title and new_title.strip():
            entry["title_corrected"] = new_title
            if new_title != old_title:
                title_changes.append((slug, old_title, new_title, "TEX"))
        else:
            entry["title_corrected"] = old_title

        entry["keywords_new"] = keywords

        # Use VENUE_OVERRIDES (comprehensive for all talks)
        if slug in VENUE_OVERRIDES:
            venue_display = VENUE_OVERRIDES[slug]
        else:
            # Fallback: derive from directory name
            source_dir = entry.get("source_dir", "")
            parts = source_dir.split("/")
            venue_part = parts[1] if len(parts) >= 2 else (parts[0] if parts else entry.get("venue", ""))
            venue_display = re.sub(r'^\d{4,8}\s*-+\s*', '', venue_part)
            venue_display = re.sub(r'_(?![+\-\d])', ' ', venue_display)
            venue_display = re.sub(r'--', ', ', venue_display)
            print(f"  WARNING: No venue override for {slug}, using fallback: {venue_display}")
        entry["venue_display"] = venue_display

        updated_entries.append(entry)

    # Print title changes for review
    print(f"\n=== TITLE CHANGES ({len(title_changes)}) ===")
    for item in title_changes:
        slug, old, new, source = item
        print(f"\n{slug} [{source}]:")
        print(f"  OLD: {old}")
        print(f"  NEW: {new}")

    # Generate HTML
    html = generate_html(updated_entries)
    out_path = os.path.join(REPO_TALKS, "index.html")
    with open(out_path, 'w') as f:
        f.write(html)
    print(f"\nWrote {len(html)} bytes to {out_path}")
    print(f"Total entries: {len(updated_entries)}")
    entries_with_keywords = sum(1 for e in updated_entries if e.get("keywords_new"))
    print(f"Entries with keywords: {entries_with_keywords}")


if __name__ == "__main__":
    main()
