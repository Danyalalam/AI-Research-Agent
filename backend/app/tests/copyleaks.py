from services.plagiarism_checker import PlagiarismChecker
import random

checker = PlagiarismChecker()
scan_id = f'scan-{random.randint(1000,9999)}'
text = 'This is a test text to analyze for AI content and writing quality.'

ai_result = checker.check_ai_content(text, scan_id)
print('AI Detection Result:', ai_result)

writing_result = checker.get_writing_score(text, scan_id)
print('Writing Score Result:', writing_result)