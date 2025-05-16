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
