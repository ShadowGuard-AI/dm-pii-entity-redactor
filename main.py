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
        self.patterns = patterns or self._default_patterns()  # Use custom patterns or default if none provided
        self.faker = faker_instance or Faker() #Use provided or default faker
        self.logger = logging.getLogger(__name__)

    def _default_patterns(self):
        """
        Defines a set of default regex patterns for common PII entities.

        Returns:
            dict: A dictionary containing regex patterns for name, address, and phone number.
        """
        return {
            "name": r"([A-Z][a-z]+) ([A-Z][a-z]+)", # Simple name regex
            "address": r"\d+ [A-Za-z]+ St(?:reet)?", # Simple address regex
            "phone_number": r"\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}" # Simple phone regex
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
            for entity_type, pattern in self.patterns.items():
                redacted_text = re.sub(pattern, self._get_replacement(entity_type), redacted_text)
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
            if entity_type == "name":
                return self.faker.name()
            elif entity_type == "address":
                return self.faker.address()
            elif entity_type == "phone_number":
                return self.faker.phone_number()
            else:
                self.logger.warning(f"No replacement defined for entity type: {entity_type}. Returning empty string.")
                return ""
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