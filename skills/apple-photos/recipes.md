# Apple Photos recipes

## Installed toolchain

- `osxphotos`: Python library (auto-installed via UV script)
- `exiftool`: useful for EXIF inspection after export
- `sqlite3`: direct Photos.db access (rarely needed)

## Common commands

### List libraries

```bash
osxphotos list
```

### Show active library info

```bash
osxphotos info
```

### List people

```bash
apple-photos people --limit 100
```

### Query recent photos of a person

```bash
apple-photos query --person "<NAME>" --after 2026-01-01 --limit 100 --json
```

### Export recent photos of a person

```bash
apple-photos export ~/Desktop/exports --person "<NAME>" --after 2026-01-01 --limit 50
```

### Export from an album

```bash
apple-photos export ~/Desktop/exports --album "Favorites" --limit 50
```

### Dry-run export to preview

```bash
apple-photos export ~/Desktop/exports --person "<NAME>" --after 2025-06-01 --dry-run
```

## Notes

- The Python API (`osxphotos.PhotosDB`) is more reliable than `osxphotos query --json`,
  which can error on some CLI theme/config combinations.
- `osxphotos persons` and `osxphotos query --count` still work for spot checks.
- Export copies files out of the library — it never mutates Photos.app.
