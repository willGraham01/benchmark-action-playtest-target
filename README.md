# benchmark-action-playtest-target
Target repo for testing benchmark actions when deployed to another repo

## Original repo
https://github.com/willGraham01/benchmark-action-playtest

## Pages Deployment
https://willgraham01.github.io/benchmark-action-playtest-target/

## What's going on?

The idea is that the original repo will push "profiling results" to the source branch, `target`, from which this repository will then build a website using the `website_build/build_site.py` script.
This script can be run locally to test the website that is created - just be sure to have the `target` branch (or a test branch you want to draw the source from) up-to-date and checked-out in your local clone/fork.
The `src` directory contains the website source that does not need to be updated - certain files have placeholder markers in them so that the script knows where to insert markdown.
There are currently two (well, three if you count the index page) pages generated by the script, plus a bunch of extra files that are linked to.
- The `index.md` page, which is just rendered markdown that points to the other pages.
- [The profiling results lookup table](#the-profiling-results-lookup-page)
- [The summary statistics page](#the-run-statistics-page)

### The profiling results lookup page

This lookup table on this page is auto-generated from the `pyisession` files that are pushed to the source branch.
The contents of this page are some flavour text, surrounding a lookup table that will redirect viewers to the results (in rendered HTML) of the given profile run.
The results of each run are themselves HTML files that are dumped into the `build/pyis_html` directory, and under the hood the script uses a `pandas.DataFrame` object to keep track of which `pyis` session corresponds to which `HTML` file.
This association is then parsed into a markdown table, and rendered in the placeholder section of the `src/profiling_index.md` template page.

### The run statistics page

The plots on this page are generated by reading the `pyisession` files and any associated meta-data files (currently these share the same name as their `pyisession` counterparts, but carry a `.stats.json` extension).
The plots are placed into the `build/plots` directory as `svg`s and image includes are written into the placeholder section of the `src/run_statistics.md` page.

It is also possible for us to export a per-profiling session table of statistics we are interested in, implementing this in much the same way as the table in the profiling lookup page.
This is currently not implemented.