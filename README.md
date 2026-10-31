![Banner](banner.png)

# dm-pii-entity-redactor
Identifies and redacts Personally Identifiable Information (PII) entities (names, addresses, phone numbers) in structured or semi-structured data using regular expressions or NLP techniques. Supports configuration with custom PII patterns. - Focused on Tools designed to generate or mask sensitive data with realistic-looking but meaningless values

## Install
`git clone https://github.com/ShadowStrikeHQ/dm-pii-entity-redactor`

## Usage
`./dm-pii-entity-redactor [params]`

## Parameters
- `-h`: Show help message and exit
- `-p`: Path to a JSON file containing custom regex patterns.
- `-o`: Path to the output file. If not provided, prints to stdout.
- `-l`: Path to the log file. If not provided, logs to console.

## License
Copyright (c) ShadowStrikeHQ

Default name patterns cover upper case, lower case, and title case names, hyphenated and apostrophe names, Mc and Mac surnames, and names with a middle initial. A single name is covered only when the context marks it, for example after "name is", "named", or "called", or after an honorific such as Dr. Default address patterns cover common street suffixes, including St, Street, Ave, Avenue, Rd, Road, Blvd, Boulevard, Ln, Lane, Dr, Drive, Ct, Court, Pl, Place, Way, Highway, Parkway, Circle, and Terrace, multi word street names, and PO Box forms.
Every run prints a per type replacement count, so a run that replaced nothing is visible in the counts.
A custom pattern file is merged over the defaults: a custom type is added, a custom pattern for a default type replaces that one pattern, and the other defaults stay active. A type with no Faker replacement, such as a custom email type, is replaced with the fixed marker [REDACTED] instead of being deleted.
A residue of the Titlecase pair false positive remains by design: the patterns are regular expressions with a small list of common non name words excluded, so an unusual pair of ordinary words in name shape can still be taken as a name, and a name in an unusual shape can still be missed. Read the per type counts and check the output.
