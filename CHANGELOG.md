# Changelog

What changed in `packvium-native` (Python), release by release. The format follows
[Keep a Changelog](https://keepachangelog.com/1.1.0/) and this project adheres to
[Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.7.0]

The native path now raises what the pure engine raises (see *Fixed*).

### Fixed

- **A native refusal raises `packvium`'s own class.** The native path raised `PackviumError`
  where the pure engine raises `InvalidRequestError`; it now maps the code onto `packvium`'s
  classes, and a missing or unmapped code falls back to the pure engine.
- **The native path writes canonical JSON and names its own version**, not `packvium` 0.1.0.
- **The `native` extra is pinned** to `packvium-native-rust==1.7.0`, the matching release.

`packvium-native` is still not published to PyPI, and neither is `packvium-native-rust`, so the
`native` extra cannot be installed yet. Use [`packvium`](https://pypi.org/project/packvium/1.7.0/)
directly.

## [1.6.0]

A version-alignment release of the source. No selector behavior changes.

`packvium-native` is still not published to PyPI: the native wheels it would select between
are not built yet. Use [`packvium`](https://pypi.org/project/packvium/1.6.0/) directly.

## [1.5.0]

A version-alignment release of the source. No selector behavior changes.

`packvium-native` is still not published to PyPI: the native wheels it would select between
are not built yet. Use [`packvium`](https://pypi.org/project/packvium/1.5.0/) directly.

## [1.4.0]

A version-alignment release of the source. No code changes.

`packvium-native` is still not published to PyPI: the native wheels it would select between
are not built yet. Use [`packvium`](https://pypi.org/project/packvium/1.4.0/) directly.

## [1.3.0]

A version-alignment release of the source. No code changes.

`packvium-native` is still not published to PyPI: the native wheels it would select between
are not built yet. Use [`packvium`](https://pypi.org/project/packvium/1.3.0/) directly.

## [1.2.0]

A version-alignment release of the source. No code changes.

`packvium-native` is not published to PyPI for this version: the native wheels it would select
between are not built yet, so a published selector would have nothing to choose. Use
[`packvium`](https://pypi.org/project/packvium/1.2.0/) directly.

## Earlier releases

Up to 1.1.0 one changelog covered every Packvium language. Those entries are kept in
this repository's GitHub Releases for each tag.
