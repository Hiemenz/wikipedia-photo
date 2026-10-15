# wikipedia-photo

Wikipedia Picture of the Day on a Waveshare 7.5in e-ink display. Imported from an untracked folder on a Raspberry Pi (code only; image/movie frames were not kept).

The code imports `waveshare_epd` (previously vendored). Switch the import to the shared driver
`from hiemenz_utils.eink.waveshare import epd7in5_V2` (installed via `uv sync --extra eink`;
the hiemenz-utils repo is private, so this needs GitHub access).
