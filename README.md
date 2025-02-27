An experiement with weather and sunrise times.

## tl;dr
```
uvx acme-weather
```

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

```
cd clw
uv build
# insert testing here
uv publish
```

To make `uv publish` smooth, I set the env var `UV_PUBLISH_TOKEN` with a valid PyPI token:
```
export UV_PUBLISH_TOKEN=pypi-yourReallyLongPyPIPublishingToken
```

## To Do

Current near-term implementation plans:
- [x] day-or-night based on sun rise/set times
- [ ] clean up visuals, provide external CSS
- [x] published to PyPI - https://pypi.org/project/acme-weather/
- [x] commandline app packaging with uv support
- [ ] add release management, to bump version, test and publish
- [ ] visual high and low temps: hottest, hot, warm, average, cool, cold, coldest
- [ ] visual percipitation ???
- [ ] add moon rise, zenith, set and phase
- [ ] add icons for dawn, sunrise, noon, sunset, dusk
- [ ] add images overlay for weather + sun/moon states
- [ ] better text-only *report*
- [ ] 15-minute version
- [ ] live-update mini-version
- [ ] standard set of widgets for [Textual](https://github.com/Textualize/textual)

### Thoughts on build automation

1. work in dev branch (or any)
2. completed pr/merge in `main` triggers **publish** pipline
3. bump version, build, test publish.

On commit or merge to and non-main branch, just run validate pipeline: test, coverage, format, ruff, etc.
