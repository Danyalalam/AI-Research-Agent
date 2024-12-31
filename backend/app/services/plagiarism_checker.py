import os
import random
from dotenv import load_dotenv
from copyleaks.copyleaks import Copyleaks
from copyleaks.exceptions.command_error import CommandError
from copyleaks.models.submit.ai_detection_document import NaturalLanguageDocument
import logging

# Load environment variables from .env file
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Retrieve credentials from environment variables
EMAIL_ADDRESS = os.getenv('COPYLEAKS_EMAIL')
KEY = os.getenv('COPYLEAKS_KEY')

if not EMAIL_ADDRESS or not KEY:
    logger.error("Copyleaks credentials are not set.")
    exit(1)


class AIDetector:
    def __init__(self, email: str, api_key: str):
        self.email = email
        self.api_key = api_key
        self.auth_token = None
        self.login()

    def login(self):
        """
        Authenticates with Copyleaks API and retrieves the authentication token.
        """
        try:
            self.auth_token = Copyleaks.login(self.email, self.api_key)
            logger.info("Successfully authenticated with Copyleaks.")
            logger.debug(f"Authentication Token: {self.auth_token}")
        except CommandError as ce:
            response = ce.get_response()
            logger.error(f"An error occurred (HTTP status code {ce.status_code}):")
            logger.error(response.content)
            exit(1)
        except Exception as e:
            logger.error(f"Unexpected error during authentication: {str(e)}")
            exit(1)

    def detect_ai(self, text: str) -> dict:
        """
        Performs AI detection on the provided text using Copyleaks Writer Detector.

        :param text: The text to be analyzed for AI-generated content.
        :return: A dictionary containing the detection results or an error message.
        """
        if len(text.strip().split()) < 50:
            logger.error("Input text is too short for plagiarism check.")
            return {"success": False, "error": "Input text must be at least 50 words long."}

        try:
            scan_id = random.randint(100000, 999999)
            natural_language_submission = NaturalLanguageDocument(text)
            natural_language_submission.set_sandbox(True)  # Set to False in production

            logger.info(f"Submitting AI detection scan with ID: {scan_id}")
            response = Copyleaks.AiDetectionClient.submit_natural_language(
                self.auth_token,
                scan_id,
                natural_language_submission
            )
            logger.info(f"Scan submitted successfully with ID: {scan_id}")
            logger.debug(f"Scan Response: {response}")

            # Parse the response and extract relevant information
            summary = response.get('summary', {})
            scanned_document = response.get('scannedDocument', {})
            ai_prob = summary.get('ai')
            human_prob = summary.get('human')
            total_words = scanned_document.get('totalWords', 0)

            if ai_prob is not None and human_prob is not None:
                return {
                    "success": True,
                    "ai_probability": float(ai_prob),
                    "human_probability": float(human_prob),
                    "scan_id": str(scan_id),
                    "total_words": int(total_words)
                }
            else:
                logger.error("Missing probability fields in response.")
                return {"success": False, "error": "Incomplete response from Copyleaks."}

        except CommandError as ce:
            response = ce.get_response()
            logger.error(f"API Error (HTTP {ce.status_code}): {response.content}")
            return {"success": False, "error": f"API Error: {response.content.decode()}"}
        except Exception as e:
            logger.error(f"Unexpected error during AI detection: {str(e)}")
            return {"success": False, "error": f"Unexpected error: {str(e)}"}
        
        
# if __name__ == "__main__":
#     # Instantiate the AIDetector
#     detector = AIDetector(email=EMAIL_ADDRESS, api_key=KEY)

#     # Sample text for plagiarism checking
#     sample_text = (
#         "Lions are social animals, living in groups called prides, typically consisting of "
#         "several females, their offspring, and a few males. Female lions are the primary "
#         "several females, their offspring, and a few males. Female lions are the primary "
#         "hunters, working together to catch prey. Lions are known for their strength, "
#         "teamwork, and complex social structures."
#     )

#     # Perform AI detection
#     result = detector.detect_ai(sample_text)

#     # Output the results
#     if result.get("success"):
#         print("Plagiarism Check Results:")
#         print(f"AI Probability: {result['ai_probability'] * 100:.2f}%")
#         print(f"Human Probability: {result['human_probability'] * 100:.2f}%")
#         print(f"Scan ID: {result['scan_id']}")
#         print(f"Total Words Analyzed: {result['total_words']}")
#     else:
#         print("Plagiarism Check Failed:")
#         print(f"Error: {result.get('error')}")