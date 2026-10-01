# GhostReader+ Annotation Model v1

GhostReader+ stores bookmarks, highlights, and notes in an internal format that is independent of the source format.

## Storage

- Primary runtime storage: IndexedDB database `ghostreader-annotations-v1`.
- Object store: `annotations`.
- `book_id` identifies the imported content using a SHA-256 fingerprint of normalized title/author/sections.
- A small localStorage compatibility path exists only for older builds/private browsing and is migrated when possible.

## Annotation schema

Each record contains at minimum:

```json
{
  "annotation_id": "ann_...",
  "book_id": "sha256:...",
  "type": "bookmark | highlight | note",
  "location": {
    "scheme": "text | image",
    "page_index": 0,
    "resource": "chapter-03.xhtml"
  },
  "created_at": "2026-09-29T00:00:00Z",
  "updated_at": "2026-09-29T00:00:00Z"
}
```

### Text formats: EPUB, MOBI, TXT

Highlights additionally retain:

- `quote`
- `prefix`
- `suffix`

The quote is the primary recovery hint when pagination/reflow changes. Page index is only a fallback/navigation hint.

### PDF

The current reader treats PDF pages as image resources. Bookmark/note locations therefore remain stable by page/resource. A future PDF text-layer adapter can add text quotes and rectangle coordinates without changing the annotation schema.

### Comic ZIP

Comic pages use an image resource and page index. Visual annotations should use normalized coordinates (`0..1`) when that UI is added, rather than pixel coordinates.

## Migration

Older bookmark and page-note values stored under per-book localStorage keys are migrated to IndexedDB on reader startup. Existing data is not intentionally discarded during migration.
