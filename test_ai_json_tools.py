from app.utils.ai_json_tools import build_ai_prompt, process_ai_json_output

user_input = 'Import the CommandProcessor class from the command_processor module'
prompt = build_ai_prompt(user_input)
print('PROMPT TO AI:')
print(prompt)

ai_json = '''{
  "module": "app.command_processor.command_processor",
  "class": "CommandProcessor",
  "import_statement": "from app.command_processor.command_processor import CommandProcessor"
}'''

print('\nAI JSON OUTPUT:')
print(ai_json)

print('\nPROCESSED IMPORT STATEMENT:')
print(process_ai_json_output(ai_json)) 