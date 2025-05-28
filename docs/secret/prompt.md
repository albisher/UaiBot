LabeebAgent is master agent, its backed with a choosen local llm set it now for gemma3:latest it should be able to interact and choose the needed tools and models for further interactions. it should be able learn, memorize, gain a skill or capabilities. labeeb must follow the rule of Do not pass anything to the internet while preccessing any task unless it is clearly asking for it.a

run main app and audit it
find the needed actions

solve the list one by one .. do not create script to solve.

the project name is now : labeeb or Labeeb
old name that we are taking out which is wrong : uaibot, Uaibot, uAIbot, uaiagent, uAI Agent, UaiAgent

Run:
@audit_project.py

you may pass commands to main using --fast .. it will help you in checking details
PYTHONPATH=srcpython3src/app/main.py

tools sudit will test file itself and will test its usecase through passing the related human like request to main.py using --fast
by checking the path where the communicaiton is happening you can also learn about what is being used for each call.
@tools_audit.py

make it all work, check if it is working as intended following A2A, MCP, SmolAgents.

you should code all todo .. you should check if it is codded correctly! also you chould test its logic.

you should find and  solve
issues, warnings, problems, and bugs right away.
especially if they are blocking the progress or found in terminal problems.

follow the /.cursor/rules  and updating the /todo files and /README.md as you go. Test the results to confirm files created are worrking and functional.

you are developping proffitionally, you are developping for multi language and multi system

update docs and todos with requirements for each install you need to do

check the systema nd os we are working on now, all os related  changes on the solution should be kept isolated from affecting other os functionality.

our project is now named Labeeb .. so correct naming when found. thus RTL, Arabic (in all its versions, Kuwait, Saudi, Morocco, Egypt) is an important language as the main input for this project.  other languages comes next

# ---

Note: Clipboard tool is now fully functional and multi-lingual on Linux using pyperclip. All actions (copy, get, paste, clear) are mapped for English and Arabic (Kuwaiti, Moroccan, MSA, etc.). See README for details.

Note: PyAutoGUI is the official and default technology for all screenshots, mouse, and keyboard automation in Labeeb. All workflows, tools, and tests should use PyAutoGUI for these tasks to ensure cross-platform compatibility (Linux, macOS, Windows). Use of other libraries (MSS, gnome-screenshot, etc.) is only permitted for special cases or future enhancements.
