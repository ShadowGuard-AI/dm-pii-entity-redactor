![Studio floor](intro-banner.png)

> Inventory entry. Medium: gesso white, gold size, bole red, and lapis on studio boards. A small jar vignette stands at the left of this entry, and a paint tube leans against the heading below.

# dm-pii-entity-redactor

Identifies and redacts Personally Identifiable Information (PII) entities (names, addresses, phone numbers) in structured or semi-structured data using regular expressions or NLP techniques. Supports configuration with custom PII patterns. - Focused on Tools designed to generate or mask sensitive data with realistic-looking but meaningless values

![Banner](banner.png)

![Studio scene](scene.svg)

![Heavy separator](sep-heavy.svg)

## Install

`git clone https://github.com/ShadowStrikeHQ/dm-pii-entity-redactor`

> Inventory slip: the housed clone line names an older organisation. It stands here exactly as housed, and the correction lives on the website, labelled as a correction.

![Light separator](sep-light.svg)

## Usage

`./dm-pii-entity-redactor [params]`

## Parameters

- `-h`: Show help message and exit
- `-p`: Path to a JSON file containing custom regex patterns.
- `-o`: Path to the output file. If not provided, prints to stdout.
- `-l`: Path to the log file. If not provided, logs to console.

> Kit wording, carried in full. Primary control: Sweep the Floor. Pattern field: Custom Patterns, JSON Path. Tally title: Replacements by Type. Residue title: What the Patterns Still Miss.

![Heavy separator](sep-heavy.svg)

## License

Copyright (c) ShadowStrikeHQ

![Light separator](sep-light.svg)

### Plate one: name patterns

Default name patterns cover upper case, lower case, and title case names, hyphenated and apostrophe names, Mc and Mac surnames, and names with a middle initial. A single name is covered only when the context marks it, for example after "name is", "named", or "called", or after an honorific such as Dr. Default address patterns cover common street suffixes, including St, Street, Ave, Avenue, Rd, Road, Blvd, Boulevard, Ln, Lane, Dr, Drive, Ct, Court, Pl, Place, Way, Highway, Parkway, Circle, and Terrace, multi word street names, and PO Box forms.

> Inventory slip: solitary names qualify solely when context flags them.

### Plate two: addresses, tallies, layering, and residue

Every run prints a per type replacement count, so a run that replaced nothing is visible in the counts.

> Inventory slip: each execution prints tallies split by type.

A custom pattern file is merged over the defaults: a custom type is added, a custom pattern for a default type replaces that one pattern, and the other defaults stay active. A type with no Faker replacement, such as a custom email type, is replaced with the fixed marker [REDACTED] instead of being deleted.

> Inventory slip: types lacking any Faker substitute become [REDACTED], never deleted.

A residue of the Titlecase pair false positive remains by design: the patterns are regular expressions with a small list of common non name words excluded, so an unusual pair of ordinary words in name shape can still be taken as a name, and a name in an unusual shape can still be missed. Read the per type counts and check the output.

![Heavy separator](sep-heavy.svg)

### Floor notes: what the record does not say

The record leaves silences, and they are carried here as absences. When NLP applies versus regular expressions is never stated. No JSON shape or pattern syntax is printed. No input path control, no exit behaviour, and no output identity guard is named. Nothing has been invented to fill those spaces, and no example of any entity kind is exhibited anywhere on this page: kinds and categories only, values never.

![Logo](logo.png)
