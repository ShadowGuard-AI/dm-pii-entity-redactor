import argparse
import logging
import re
import json
import sys
from faker import Faker

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class PIIEntityRedactor:
    """
    A class for identifying and redacting Personally Identifiable Information (PII) entities in text.
    """

    def __init__(self, patterns=None, faker_instance=None):
        """
        Initializes the PIIEntityRedactor with optional custom patterns and a Faker instance.

        Args:
            patterns (dict, optional): A dictionary of regex patterns for PII entities. Defaults to None.
            faker_instance (Faker, optional): An instance of the Faker library for generating fake data. Defaults to None.
        """
        if patterns:
            # Custom patterns merge over the defaults, and dict order is
            # part of the behavior: a key that overrides a default keeps the
            # default's position in the pass order below, while a brand new
            # key is appended and runs last, over text the earlier passes
            # already rewrote.
            merged = self._default_patterns()
            merged.update(patterns)
            self.patterns = merged
        else:
            self.patterns = self._default_patterns()
        # These counts are never reset by redact_text. On an instance that
        # redacts two texts, last_counts describes both runs added together,
        # despite the name suggesting the last one only.
        self.last_counts = {}
        self.faker = faker_instance or Faker() #Use provided or default faker
        self.logger = logging.getLogger(__name__)

    def _default_patterns(self):
        """
        Defines a set of default regex patterns for common PII entities.

        Returns:
            dict: A dictionary containing regex patterns for name, address, and phone number.
        """
        # The name patterns are heuristics held back by the stop word list
        # below: a two word name is two capitalized tokens whose words are
        # not on that list, and a single name is only caught after words
        # like is, named, or called, or after an honorific. A name that
        # shares a word with the list, or stands alone mid sentence with no
        # context word, is missed by design, and an ordinary capitalized
        # pair that is not on the list is taken for a name. I accept both
        # errors rather than pretend a regex can tell names from prose.
        common = ["the","this","that","these","those","hello","dear","please","thank","thanks","good","new","first","last","next","name","is","was","has","have","had","and","but","or","for","with","from","lives","live","lived","works","worked","said","says","went","came","here","there","where","when","what","who","how","why","not","all","any","my","your","his","her","their","our","its","it","in","on","at","to","of","a","an","i","you","he","she","we","they","me","him","them","us","do","does","did","will","would","can","could","should","may","might","be","been","being","am","are","were","email","phone","contact","address","reached","reach","call","called","today","tomorrow","yesterday","one","two","three","person","people","home","work","no","quick","brown","lazy","fox","jumps","street","avenue","road","boulevard","lane","drive","court","place","way","highway","parkway","circle","terrace"]
        def variants(words, form):
            if form == "title":
                return "(?:" + "|".join(w.capitalize() for w in words) + ")"
            if form == "upper":
                return "(?:" + "|".join(w.upper() for w in words) + ")"
            return "(?:" + "|".join(words) + ")"
        title_token = r"(?:Mc[A-Z][a-z]+|Mac[A-Z][a-z]+|O'[A-Za-z]+|[A-Z][a-z]+(?:[-'][A-Za-z]+)*)"
        upper_token = r"(?:[A-Z]{2,}(?:[-'][A-Z]+)*)"
        lower_token = r"(?:[a-z]+(?:[-'][a-z]+)*)"
        mid = r"(?:\s+[A-Z]\.\s+|\s+)"
        name = (
            r"(?<!\w)(?:"
            + r"(?!" + variants(common, "title") + r"\b)" + title_token + mid + r"(?!" + variants(common, "title") + r"\b)" + title_token
            + r"|(?!" + variants(common, "upper") + r"\b)" + upper_token + mid + r"(?!" + variants(common, "upper") + r"\b)" + upper_token
            + r"|(?!" + variants(common, "lower") + r"\b)" + lower_token + r"\s+" + r"(?!" + variants(common, "lower") + r"\b)" + lower_token
            + r")(?!\w)"
        )
        single = r"(?!" + variants(common, "title") + r"\b)(?!" + variants(common, "upper") + r"\b)(?:" + title_token + r"|" + upper_token + r")"
        suffix = r"(?i:Street|St|Avenue|Ave|Road|Rd|Boulevard|Blvd|Lane|Ln|Drive|Dr|Court|Ct|Place|Pl|Way|Highway|Hwy|Parkway|Pkwy|Circle|Cir|Terrace|Ter)"
        return {
            "phone_number": r"\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}",
            "address": r"(?:\bP\.?\s?O\.?\s+Box\s+\d+|\b\d+\s+(?:[A-Za-z0-9.'-]+\s+){0,3}" + suffix + r"\b\.?)",
            "name": name,
            "name_context_is": r"(?<=(?:is |Is |IS ))" + single + r"(?!\w)",
            "name_context_named": r"(?<=(?:named |Named |NAMED ))" + single + r"(?!\w)",
            "name_context_called": r"(?<=(?:called |Called |CALLED ))" + single + r"(?!\w)",
            "name_honorific": r"(?:Mr\.|Mrs\.|Ms\.|Dr\.)\s+" + title_token + r"(?!\w)"
        }

    def redact_text(self, text):
        """
        Redacts PII entities in the given text using the configured patterns.

        Args:
            text (str): The text to redact.

        Returns:
            str: The redacted text.
        """
        redacted_text = text
        try:
            # The passes run in dict order over each other's output, not
            # over the original text. That ordering cuts both ways: a phone
            # number is already replaced before the name pass can see its
            # digits, but a fake address written by the address pass still
            # contains a street line and words the later name patterns can
            # match, so a replacement can itself be partly re-redacted and
            # counted twice. Each match also draws a fresh fake, so the
            # same person named twice in one text gets two different fake
            # names; nothing here keeps one identity consistent.
            for entity_type, pattern in self.patterns.items():
                # Pass a callable, not a precomputed string. With a string,
                # one fake value was drawn once and stamped on every match,
                # so two different people in a text collapsed into a single
                # fake identity and the output implied they were one person.
                # A callable also avoids re.sub template processing, which
                # would reinterpret backslashes in a generated address.
                redacted_text, count = re.subn(pattern, lambda _m: self._get_replacement(entity_type), redacted_text)
                self.last_counts[entity_type] = self.last_counts.get(entity_type, 0) + count
        except re.error as e:
            self.logger.error(f"Regex error: {e}")
            raise
        except Exception as e:
            self.logger.exception("An unexpected error occurred during redaction.")
            raise
        return redacted_text

    def _get_replacement(self, entity_type):
        """
        Returns a replacement string for a given entity type using Faker.

        Args:
            entity_type (str): The type of PII entity being replaced (e.g., "name", "address").

        Returns:
            str: A fake replacement value for the entity.
        """
        try:
            if entity_type == "name" or entity_type.startswith("name_") or entity_type.startswith("name"):
                return self.faker.name()
            elif entity_type == "address":
                return self.faker.address()
            elif entity_type == "phone_number":
                return self.faker.phone_number()
            else:
                self.logger.warning(f"No replacement defined for entity type: {entity_type}. Returning a redaction marker.")
                return "[REDACTED]"
        except Exception as e:
            self.logger.exception(f"Error generating fake data for {entity_type}: {e}")
            return "[REDACTED]"

def setup_argparse():
    """
    Sets up the argument parser for the command-line interface.

    Returns:
        argparse.ArgumentParser: The argument parser object.
    """
    parser = argparse.ArgumentParser(description="Identifies and redacts PII entities in text.")
    parser.add_argument("input_text", nargs="?", type=str, help="The input text to redact.  If not provided, reads from stdin.")
    parser.add_argument("-p", "--patterns", type=str, help="Path to a JSON file containing custom regex patterns.")
    parser.add_argument("-o", "--output", type=str, help="Path to the output file. If not provided, prints to stdout.")
    parser.add_argument("-l", "--log_file", type=str, help="Path to the log file. If not provided, logs to console.")

    return parser

def load_patterns(file_path):
    """Loads regex patterns from a JSON file.

    Args:
        file_path (str): The path to the JSON file.

    Returns:
        dict: A dictionary of regex patterns.

    Raises:
        FileNotFoundError: If the file is not found.
        json.JSONDecodeError: If the file contains invalid JSON.
        TypeError: If the loaded data is not a dictionary.
    """
    try:
        with open(file_path, 'r') as f:
            patterns = json.load(f)
            if not isinstance(patterns, dict):
                raise TypeError("The JSON file must contain a dictionary of patterns.")
            return patterns
    except FileNotFoundError:
        logging.error(f"Pattern file not found: {file_path}")
        raise
    except json.JSONDecodeError:
        logging.error(f"Invalid JSON in file: {file_path}")
        raise
    except TypeError as e:
        logging.error(e)
        raise
    except Exception as e:
        logging.error(f"An unexpected error occurred while loading patterns: {e}")
        raise

def main():
    """
    The main function that parses arguments, redacts the input text, and prints the output.
    """
    parser = setup_argparse()
    args = parser.parse_args()

    # Handle logging configuration
    if args.log_file:
        file_handler = logging.FileHandler(args.log_file)
        file_handler.setLevel(logging.INFO)
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        file_handler.setFormatter(formatter)
        logging.getLogger().addHandler(file_handler)

    try:
        # Load custom patterns if provided
        patterns = None
        if args.patterns:
            patterns = load_patterns(args.patterns)

        # Initialize the PII entity redactor
        redactor = PIIEntityRedactor(patterns=patterns)

        # Read input text from stdin or from the argument
        input_text = args.input_text
        if not input_text:
            if not sys.stdin.isatty(): # Check if input is coming from a pipe
                input_text = sys.stdin.read()
            else:
                 parser.print_help()
                 sys.exit(1)



        # Redact the text
        redacted_text = redactor.redact_text(input_text)
        counts = getattr(redactor, "last_counts", {})
        count_line = "Replacement counts: " + ", ".join(f"{k}: {counts.get(k, 0)}" for k in redactor.patterns)
        logging.info(count_line)
        print(count_line, file=sys.stderr)

        # Write the output to a file or stdout
        if args.output:
            try:
                with open(args.output, "w") as f:
                    f.write(redacted_text)
                logging.info(f"Redacted text written to {args.output}")
            except IOError as e:
                logging.error(f"Error writing to output file: {e}")
                sys.exit(1)


        else:
            print(redacted_text)
    except FileNotFoundError as e:
        logging.error(e)
        sys.exit(1)
    except json.JSONDecodeError as e:
        logging.error(e)
        sys.exit(1)
    except TypeError as e:
        logging.error(e)
        sys.exit(1)
    except Exception as e:
        logging.exception("An unhandled error occurred.")
        sys.exit(1)


if __name__ == "__main__":
    main()

#Example Usage:
# 1. Redact text from stdin and print to stdout:
#    echo "My name is John Doe and my address is 123 Main St and my phone number is 555-123-4567" | python main.py
#
# 2. Redact text from argument and print to stdout:
#    python main.py "My name is John Doe and my address is 123 Main St and my phone number is 555-123-4567"
#
# 3. Redact text from stdin and write to file:
#    echo "My name is John Doe and my address is 123 Main St and my phone number is 555-123-4567" | python main.py -o output.txt
#
# 4. Redact text from argument and write to file:
#    python main.py "My name is John Doe and my address is 123 Main St and my phone number is 555-123-4567" -o output.txt
#
# 5. Use custom patterns from a file:
#   Create a file patterns.json with contents like:
#   {
#      "email": "[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\\.[a-zA-Z]{2,}"
#   }
#  python main.py "My email is test@example.com" -p patterns.json
#
# 6.  Using a log file:
#   python main.py "My name is John Doe" -l myapp.log