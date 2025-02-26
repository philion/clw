A quick experiement with weather and sunrise times.

**WIP**: This is currently under development, in main branch. Don't expect too much.

## Run

Currently using `uv` for development. See [uv install instructions](https://docs.astral.sh/uv/getting-started/installation/)

```sh
git clone https://github.com/philion/clw
cd clw
uv run clw
```

![screenshot of clw tool showing the 12 hour weather forecast](./screenshot.png)


## Build

Standard [uv build and publish](https://docs.astral.sh/uv/guides/projects/) tools are used.


### To Do

Current near-term implementation plans:
- [x] day-or-night based on sun rise/set times
- [ ] clean up visuals, provide external CSS
- [ ] published to PyPI
- [ ] commandline app packaging with uv support
- [ ] visual high and low temps: hottest, hot, warm, average, cool, cold, coldest
- [ ] visual percipitation ???
- [ ] add moon rise, zenith, set and phase
- [ ] add icons for dawn, sunrise, noon, sunset, dusk
- [ ] add images overlay for weather + sun/moon states
- [ ] better text-only *report*
- [ ] 15-minute version
- [ ] live-update mini-version
- [ ] standard set of widgets for [Textual](https://github.com/Textualize/textual)
