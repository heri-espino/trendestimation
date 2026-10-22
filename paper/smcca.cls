\ProvidesClass{smcca}[2026/01/01 Estilo para el Boletín de la SMCCA]

% ============================================================
% 1) Base
% ============================================================
\NeedsTeXFormat{LaTeX2e}
\LoadClass{article}


% ============================================================
% 2) Opciones de la clase
% ============================================================
\newif\if@articleinenglish
\DeclareOption{english}{\@articleinenglishtrue}
\DeclareOption{spanish}{\@articleinenglishfalse}
\DeclareOption{espanol}{\@articleinenglishfalse}
\ExecuteOptions{espanol} % default
\ProcessOptions\relax


% ============================================================
% 3) Idioma y autores
% ============================================================
\RequirePackage{authblk}
\setlength{\affilsep}{4pt}
\renewcommand\Authfont{\normalsize\bfseries}
\renewcommand\Affilfont{\small\normalfont}

\if@articleinenglish
  \RequirePackage[english]{babel}
\else
  \RequirePackage[spanish,es-tabla]{babel}
  \renewcommand\Authand{ y }
  \renewcommand\Authands{ y }
  \renewcommand\Authsep{, }
\fi


% ============================================================
% 4) Tipografía y microtipografía (pdfLaTeX)
% ============================================================
\RequirePackage[T1]{fontenc}
\RequirePackage{iftex}
\ifPDFTeX
  \RequirePackage[utf8]{inputenc}
\fi
\RequirePackage{lmodern}
\RequirePackage[protrusion=true,expansion=true]{microtype}


% ============================================================
% 5) Matemáticas y gráficos
% ============================================================
\RequirePackage{amsmath,amsfonts,amssymb}
\RequirePackage{graphicx}
\graphicspath{{./figures/}{./Figures/}{./images/}{./figuras/}{./Figuras/}{./imagenes/}}
\RequirePackage{epstopdf}


% ============================================================
% 6) Layout (márgenes y columnas)
% ============================================================
\RequirePackage[margin=2.5cm,headheight=14.5pt]{geometry}
\setlength{\columnsep}{10pt}
\setlength{\parindent}{0pt}
\setlength{\parskip}{6pt plus 2pt minus 1pt}
\setlength{\emergencystretch}{2em}


% ============================================================
% 7) Hipervínculos y bibliografía
% ============================================================
\RequirePackage{xcolor}
\RequirePackage[hidelinks]{hyperref}
\RequirePackage[numbers,sort&compress]{natbib}


% ============================================================
% 8) Figuras, tablas y flotantes
% ============================================================
\RequirePackage{float}
\RequirePackage{caption}
\RequirePackage{subcaption}
\captionsetup{
  font=small,
  labelfont={sf,bf}
}
\setlength{\captionmargin}{10pt}


% ============================================================
% 9) Títulos y espaciados de secciones
% ============================================================
\RequirePackage{titlesec}

\titleformat{\section}
  {\normalfont\large\bfseries}{\thesection}{0.7em}{}
\titlespacing*{\section}{0pt}{2.5ex plus 1ex minus .2ex}{1.2ex plus .2ex}

\titleformat{\subsection}
  {\normalfont\normalsize\bfseries}{\thesubsection}{0.7em}{}
\titlespacing*{\subsection}{0pt}{2.0ex plus .8ex minus .2ex}{0.9ex plus .2ex}


% ============================================================
% 10) Encabezado
% ============================================================
\RequirePackage{fancyhdr}

% Estilo principal
\fancypagestyle{customheader}{
  \fancyhf{}
  \setlength{\headheight}{16pt}
  \fancyhead[L]{Boletín Sociedad Mexicana de Computación Científica y sus Aplicaciones}
  \fancyhead[R]{\thepage}
}

% Usar siempre este estilo
\pagestyle{customheader}

% Estilo para primera página
\fancypagestyle{plain}{
  \fancyhf{}
  \setlength{\headheight}{14.5pt}
  \fancyhead[L]{Boletín Sociedad Mexicana de Computación Científica y sus Aplicaciones}
  \fancyhead[R]{\thepage}
}

\endinput