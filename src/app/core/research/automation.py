import os
import json
import logging
from datetime import datetime
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from pathlib import Path
import re
import platform
import subprocess
import time

import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import spacy
from transformers import pipeline
import networkx as nx
from labeeb.platform_core.platform_utils import get_input_handler

logger = logging.getLogger(__name__)

@dataclass
class ResearchEntry:
    topic: str
    url: str
    date: str
    content: str
    awareness_patterns: List[str]
    capability_code: str

class ResearchScraper:
    """Handles web scraping and content extraction for research topics."""
    
    def __init__(self):
        self.chrome_options = Options()
        self.chrome_options.add_argument('--headless')
        self.chrome_options.add_argument('--no-sandbox')
        self.chrome_options.add_argument('--disable-dev-shm-usage')
        
        # Initialize NLP models
        self.nlp = spacy.load("en_core_web_sm")
        self.summarizer = pipeline("summarization")
        self.ner = pipeline("ner")
        
    def scrape_topic(self, url: str, topic: str) -> Dict[str, Any]:
        """Scrape content from the given URL for the specified topic."""
        try:
            # Initialize web driver
            driver = webdriver.Chrome(options=self.chrome_options)
            driver.get(url)
            
            # Wait for content to load
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
            
            # Get page content
            content = driver.page_source
            soup = BeautifulSoup(content, 'html.parser')
            
            # Extract main content
            main_content = self._extract_main_content(soup)
            
            # Extract metadata
            metadata = self._extract_metadata(soup)
            
            # Extract images and diagrams
            images = self._extract_images(soup)
            
            driver.quit()
            
            return {
                'content': main_content,
                'metadata': metadata,
                'images': images,
                'status': 'success'
            }
            
        except Exception as e:
            logger.error(f"Failed to scrape {url}: {str(e)}")
            return {
                'content': '',
                'metadata': {},
                'images': [],
                'status': 'error',
                'error': str(e)
            }
    
    def _extract_main_content(self, soup: BeautifulSoup) -> str:
        """Extract the main content from the page."""
        # Remove unwanted elements
        for element in soup.find_all(['script', 'style', 'nav', 'footer', 'header']):
            element.decompose()
        
        # Try to find main content
        main_content = soup.find('main') or soup.find('article') or soup.find('div', class_=['content', 'main'])
        
        if main_content:
            return main_content.get_text(separator='\n', strip=True)
        return soup.get_text(separator='\n', strip=True)
    
    def _extract_metadata(self, soup: BeautifulSoup) -> Dict[str, str]:
        """Extract metadata from the page."""
        metadata = {}
        
        # Extract title
        title = soup.find('title')
        if title:
            metadata['title'] = title.string
        
        # Extract meta tags
        for meta in soup.find_all('meta'):
            name = meta.get('name', meta.get('property', ''))
            content = meta.get('content', '')
            if name and content:
                metadata[name] = content
        
        return metadata
    
    def _extract_images(self, soup: BeautifulSoup) -> List[Dict[str, str]]:
        """Extract images and their metadata from the page."""
        images = []
        for img in soup.find_all('img'):
            image_data = {
                'src': img.get('src', ''),
                'alt': img.get('alt', ''),
                'title': img.get('title', '')
            }
            if image_data['src']:
                images.append(image_data)
        return images

class ResearchManager:
    """Manages research topics and their content."""
    
    def __init__(self, research_dir: str = "research"):
        self.research_dir = Path(research_dir)
        self.scraper = ResearchScraper()
        self._ensure_directories()
    
    def _ensure_directories(self):
        """Ensure all necessary directories exist."""
        self.research_dir.mkdir(parents=True, exist_ok=True)
        (self.research_dir / "topics").mkdir(exist_ok=True)
    
    def add_topic(self, topic: str, url: str) -> bool:
        """Add a new research topic, prompt if duplicate."""
        try:
            topic_dir = self.research_dir / topic.lower().replace(" ", "_")
            if topic_dir.exists():
                resp = input(f"[Labeeb] Topic '{topic}' already exists. Overwrite? (y/n): ").strip().lower()
                if resp != 'y':
                    print("[Labeeb] Topic creation cancelled.")
                    return False
            topic_dir.mkdir(exist_ok=True)
            topic_file = topic_dir / "topic.txt"
            with open(topic_file, 'w') as f:
                f.write(f"{topic}\n{url}\n")
            return True
        except Exception as e:
            logger.error(f"Failed to add topic {topic}: {str(e)}")
            return False
    
    def process_topic(self, topic: str) -> bool:
        """Process a research topic with recursive link following and paper generation."""
        summary = {
            'topic': topic,
            'initial_rating': None,
            'initial_confidence': None,
            'fallback_used': False,
            'final_rating': None,
            'final_confidence': None,
            'files_created': [],
            'result': None
        }
        try:
            # Read topic file
            topic_dir = self.research_dir / topic.lower().replace(" ", "_")
            topic_file = topic_dir / "topic.txt"
            if not topic_file.exists():
                logger.error(f"Topic file not found: {topic_file}")
                summary['result'] = 'Topic file not found.'
                self._print_summary(summary)
                return False

            with open(topic_file, 'r') as f:
                lines = f.readlines()
                topic_name = lines[0].strip()
                url = lines[1].strip()

            # Start with fallback workflow (now includes recursive link following)
            print(f"[Labeeb] Starting comprehensive research for '{topic_name}'...")
            summary['fallback_used'] = True
            paper_content = self._fallback_human_like_browsing(url, topic_name)

            if not paper_content:
                print(f"[Labeeb] Research did not produce an excellent paper. Not learning as a capability.")
                summary['result'] = "Research did not produce an excellent paper."
                self._print_summary(summary)
                return False

            # If we have an excellent paper, create the capability
            doc = self.scraper.nlp(paper_content)
            patterns = self._generate_awareness_patterns(doc)
            capability_code = self._generate_capability_code(topic_name, doc, patterns)
            
            entry = ResearchEntry(
                topic=topic_name,
                url=url,
                date=datetime.now().strftime("%Y-%m-%d"),
                content=paper_content,
                awareness_patterns=patterns,
                capability_code=capability_code
            )
            
            self._save_research_entry(entry, topic_dir)
            summary['files_created'] = [
                f"content_{entry.date}.txt",
                f"patterns_{entry.date}.txt",
                f"capability_{entry.date}.py",
                "research_paper.md"
            ]
            
            summary['result'] = 'Learned and files created.'
            self._print_summary(summary)
            return True

        except Exception as e:
            logger.error(f"Failed to process topic {topic}: {str(e)}")
            summary['result'] = f"Exception: {str(e)}"
            self._print_summary(summary)
            return False

    def _rate_content_with_ai(self, content: str, topic: str) -> (str, float):
        """Ask the AI to rate the content in words and give a confidence score (0-100)."""
        prompt = (
            f"You are an expert researcher. Rate the following content for the topic '{topic}'. "
            f"Reply with a single word (excellent, good, fair, poor) and a confidence score (0-100) in this format: 'Rating: <word>, Confidence: <number>'.\n\nContent:\n{content[:4000]}"
        )
        try:
            from labeeb.core.ai_handler import AIHandler
            from labeeb.core.model_manager import ModelManager
            from labeeb.core.config_manager import ConfigManager
            ai_handler = AIHandler(model_manager=ModelManager(ConfigManager()))
            response = ai_handler.process_prompt(prompt)
            import re
            match = re.search(r'Rating:\s*(\w+),\s*Confidence:\s*(\d+)', response.text, re.IGNORECASE)
            if match:
                rating = match.group(1)
                confidence = float(match.group(2))
                return rating, confidence
            else:
                return 'unknown', 0.0
        except Exception as e:
            logger.error(f"AI rating failed: {str(e)}")
            return 'unknown', 0.0

    def _fallback_human_like_browsing(self, url: str, topic: str) -> str:
        """Robust, never-stopping, capability-executing research with full link traversal, focus filtering, and max 20 iterations."""
        print(f"[Labeeb] Fallback: Robust, never-stopping research for '{topic}' at {url}...")
        try:
            import difflib
            from urllib.parse import urlparse
            from datetime import datetime
            topic_dir = self.research_dir / topic.lower().replace(" ", "_")
            log_path = topic_dir / "research_log.md"
            with open(log_path, 'w') as logf:
                logf.write(f"# Research Log for {topic}\n\n")
            app = AppControlCapability()
            mouse = MouseControlCapability()
            keyboard = KeyboardControlCapability()
            page = PageContentCapability()
            nav = NavigationCapability()
            summary = {'AppControl': False, 'MouseControl': False, 'KeyboardControl': False, 'PageContent': [], 'Navigation': [], 'Analysis': [], 'Errors': [], 'CapabilityTests': {}}
            # Test all capabilities
            summary['CapabilityTests']['Mouse'] = mouse.move_and_click(10, 10)
            summary['CapabilityTests']['Keyboard'] = keyboard.type_and_enter('test')
            try:
                from labeeb.platform_core.platform_utils import get_input_handler
                handler = get_input_handler()
                summary['CapabilityTests']['Screen'] = handler.get_screen_size() is not None
            except Exception as e:
                summary['CapabilityTests']['Screen'] = False
                summary['Errors'].append(f"Screen test failed: {e}")
            # Initialize browser and visit initial URL
            summary['AppControl'] = app.launch_browser(url)
            screen_width, screen_height = 1920, 1080
            try:
                from labeeb.platform_core.platform_utils import get_input_handler
                screen_width, screen_height = get_input_handler().get_screen_size()
            except Exception:
                pass
            address_bar_x = screen_width // 2
            address_bar_y = 60 if platform.system().lower() == 'darwin' else 40
            summary['MouseControl'] = mouse.move_and_click(address_bar_x, address_bar_y)
            summary['KeyboardControl'] = keyboard.type_and_enter(url)
            import time
            time.sleep(4)
            # Track visited URLs and their content
            visited = set()
            to_visit = {url}
            all_content = []
            step = 0
            max_pages = 20
            focus_words = set()
            main_domain = urlparse(url).netloc
            while to_visit and len(visited) < max_pages:
                current_url = to_visit.pop()
                if current_url in visited:
                    continue
                visited.add(current_url)
                try:
                    page_title, main_text, links = page.extract(current_url)
                except Exception as e:
                    err_msg = f"[Error] Failed to extract {current_url}: {e}"
                    print(err_msg)
                    summary['Errors'].append(err_msg)
                    continue
                summary['PageContent'].append({'url': current_url, 'title': page_title, 'links': len(links)})
                all_content.append(main_text)
                # Extract focus words from first page
                if step == 0:
                    import re
                    words = re.findall(r'\b\w{5,}\b', main_text.lower())
                    from collections import Counter
                    common = Counter(words).most_common(10)
                    focus_words = set(w for w, _ in common)
                # Create per-link file
                def sanitize_filename(s):
                    import re
                    s = s or "untitled"
                    s = s.strip().replace(" ", "_")
                    s = re.sub(r"[^a-zA-Z0-9_\-]", "", s)
                    return s[:40]
                safe_title = sanitize_filename(page_title) if page_title else sanitize_filename(current_url)
                step_file = topic_dir / f"step{step+1}_{safe_title}.md"
                with open(step_file, 'w') as sf:
                    sf.write(f"# Step {step+1}: {page_title}\n\n")
                    sf.write(f"**URL:** [{current_url}]({current_url})\n\n")
                    sf.write(f"**Extracted Content:**\n\n{main_text}\n\n")
                with open(log_path, 'a') as logf:
                    logf.write(f"\n## Step {step+1}: [{page_title}]({current_url})\n\n")
                    logf.write(f"**URL:** [{current_url}]({current_url})\n\n")
                    logf.write(f"**Extracted Content:**\n\n{main_text}\n\n")
                    logf.write(f"**Links on Page:**\n\n")
                    for href, text in links:
                        if href and not href.startswith('#'):
                            logf.write(f"- [{text or href}]({href})\n")
                    logf.write("\n")
                # Analyze content
                ai_prompt = (
                    f"You are an expert research analyst. The topic is: '{topic}'.\n"
                    f"Here is the extracted content (truncated):\n{main_text}\n\n"
                    f"Links: {[l[0] for l in links]}\n\n"
                    f"Is this content relevant, comprehensive, and actionable for the topic? What is missing? What should be done next?\n"
                    f"Reply as either a JSON object with a 'plan' or as plain text.\n"
                    f"If JSON, use: {{'plan': [{{'action': 'follow_link', 'url': '<url>'}}, ...]}}.\n"
                    f"If text, use:\nAnalysis: [summary]\nMissing: [what is missing, if anything]\nNextActions: [comma-separated list of actions/capabilities to use or create, e.g. 'follow_link:<href>', 'extract_table', 'search:<term>', or 'none']\nConfidence: [0-100]\n"
                )
                ai_handler = self._get_ai_handler()
                try:
                    ai_response = ai_handler.process_prompt(ai_prompt).text
                except Exception as e:
                    err_msg = f"[Error] AI analysis failed for {current_url}: {e}"
                    print(err_msg)
                    summary['Errors'].append(err_msg)
                    ai_response = "AI analysis failed."
                # Save analysis to per-link file
                with open(step_file, 'a') as sf:
                    sf.write(f"**AI Analysis:**\n\n{ai_response}\n\n")
                with open(log_path, 'a') as logf:
                    logf.write(f"**AI Analysis:**\n\n{ai_response}\n\n")
                summary['Analysis'].append(ai_response)
                # Robust next actions extraction
                import re, json
                next_actions = []
                # --- Robust JSON extraction from AI response ---
                def extract_json_plan(text):
                    # Try to find a JSON object in the text
                    import re, json
                    match = re.search(r'(\{[\s\S]+\})', text)
                    if match:
                        try:
                            obj = json.loads(match.group(1))
                            if 'plan' in obj:
                                return obj['plan']
                        except Exception as e:
                            print(f"[DEBUG] Failed to parse embedded JSON: {e}")
                    return None
                plan = extract_json_plan(ai_response)
                if plan:
                    for step_obj in plan:
                        if isinstance(step_obj, dict) and step_obj.get('action') == 'follow_link' and 'url' in step_obj:
                            next_actions.append(f"follow_link:{step_obj['url']}")
                # Try text fallback
                if not next_actions:
                    try:
                        next_actions_line = re.search(r'NextActions:\s*([\w\W]+?)\n', ai_response)
                        if next_actions_line:
                            actions_str = next_actions_line.group(1).strip()
                            if actions_str.lower() != 'none':
                                next_actions = [a.strip() for a in actions_str.split(',') if a.strip()]
                    except Exception as e:
                        err_msg = f"[Error] Failed to parse next actions for {current_url}: {e}"
                        print(err_msg)
                        summary['Errors'].append(err_msg)
                # Fallback: if no next actions, add all page links (filtered)
                if not next_actions:
                    print(f"[DEBUG] No next actions from AI, falling back to all page links.")
                    for href, _ in links:
                        if href and not href.startswith('#'):
                            next_actions.append(f"follow_link:{href}")
                # --- Link filtering and logging ---
                print(f"[DEBUG] Considering {len(next_actions)} next actions from page: {current_url}")
                filtered_links = []
                for action in next_actions:
                    if action.startswith('follow_link:'):
                        href = action[len('follow_link:'):].strip()
                        resolved = nav.resolve_link(current_url, href)
                        # Only sublinks of main domain
                        if not resolved:
                            print(f"[DEBUG] Skipping link (could not resolve): {href}")
                            continue
                        if urlparse(resolved).netloc != main_domain:
                            print(f"[DEBUG] Skipping link (not sublink of main domain): {resolved}")
                            continue
                        # Similarity to topic or focus words (threshold now 0.3)
                        sim_topic = difflib.SequenceMatcher(None, topic.lower(), resolved.lower()).ratio()
                        sim_focus = max([difflib.SequenceMatcher(None, w, resolved.lower()).ratio() for w in focus_words] or [0])
                        if (sim_topic > 0.3 or sim_focus > 0.3) and resolved not in visited and resolved not in to_visit:
                            to_visit.add(resolved)
                            summary['Navigation'].append({'from': current_url, 'to': resolved})
                            filtered_links.append((resolved, sim_topic, sim_focus))
                            print(f"[DEBUG] Added link: {resolved} (sim_topic={sim_topic:.2f}, sim_focus={sim_focus:.2f})")
                        else:
                            print(f"[DEBUG] Skipping link: {resolved} (sim_topic={sim_topic:.2f}, sim_focus={sim_focus:.2f})")
                # Fallback: if no links were added, add top 3 sublinks by similarity
                if not filtered_links:
                    print(f"[DEBUG] No links passed similarity filter, using fallback to add top 3 sublinks.")
                    scored_links = []
                    for action in next_actions:
                        if action.startswith('follow_link:'):
                            href = action[len('follow_link:'):].strip()
                            resolved = nav.resolve_link(current_url, href)
                            if not resolved or urlparse(resolved).netloc != main_domain:
                                continue
                            sim_topic = difflib.SequenceMatcher(None, topic.lower(), resolved.lower()).ratio()
                            sim_focus = max([difflib.SequenceMatcher(None, w, resolved.lower()).ratio() for w in focus_words] or [0])
                            if resolved not in visited and resolved not in to_visit:
                                scored_links.append((resolved, sim_topic, sim_focus))
                    scored_links.sort(key=lambda x: max(x[1], x[2]), reverse=True)
                    for resolved, sim_topic, sim_focus in scored_links[:3]:
                        to_visit.add(resolved)
                        summary['Navigation'].append({'from': current_url, 'to': resolved})
                        print(f"[DEBUG] Fallback added link: {resolved} (sim_topic={sim_topic:.2f}, sim_focus={sim_focus:.2f})")
                step += 1
                time.sleep(2)  # Delay between links
            # Aggregate all step files for the final report
            print("\n[Labeeb] Aggregating all step files for the final research paper...")
            all_step_content = []
            for step_file in sorted(topic_dir.glob('step*.md')):
                try:
                    with open(step_file, 'r') as sf:
                        all_step_content.append(sf.read())
                except Exception as e:
                    print(f"[Error] Failed to read {step_file}: {e}")
            all_content_str = '\n\n'.join(all_step_content)
            # Enhanced final paper prompt
            research_date = datetime.now().strftime('%Y-%m-%d')
            paper_prompt = (
                f"You are an expert research paper writer. Before you write, think about what makes an excellent research paper: clarity, completeness, depth, synthesis, and actionable insights.\n"
                f"For each step, rate your own confidence (0-100) that the information gathered so far is sufficient for an excellent paper. If confidence is below 90, explain what is missing and what information would improve the paper.\n"
                f"Then, write a natural, human-readable research paper about '{topic}'.\n"
                f"Summarize and synthesize all the good, relevant text from the following research notes.\n"
                f"Do NOT include any links or URLs in the summary.\n"
                f"The paper should have:\n"
                f"- A clear, descriptive title\n"
                f"- The date of research: {research_date}\n"
                f"- A well-structured summary of the findings, written in natural language\n"
                f"- A signature line: 'Researched by Labeeb {research_date[:4]}'\n"
                f"- At the end, include: 'AI Rating: <percent>%' (leave <percent> as a placeholder to be filled in)\n"
                f"Here are the research notes and findings from all steps:\n\n{all_content_str[:12000]}\n\n"
                f"Format the paper in Markdown, but do not include any links."
            )
            paper_content = ai_handler.process_prompt(paper_prompt).text
            paper_file = topic_dir / "research_paper.md"
            with open(paper_file, 'w') as pf:
                pf.write(paper_content)
            # Rate the final paper
            rating_prompt = (
                f"You are an expert research evaluator. Rate the following research paper about '{topic}'.\n"
                f"Reply with a single word (excellent, good, fair, poor) and a confidence score (0-100) "
                f"in this format: 'Rating: <word>, Confidence: <number>'.\n\n"
                f"Paper:\n{paper_content[:4000]}"
            )
            rating_response = ai_handler.process_prompt(rating_prompt).text
            with open(paper_file, 'a') as pf:
                pf.write(f"\n\n## AI Rating\n\n{rating_response}\n")
            import re
            rating_match = re.search(r'Rating:\s*(\w+),\s*Confidence:\s*(\d+)', rating_response, re.IGNORECASE)
            if rating_match:
                rating = rating_match.group(1)
                confidence = float(rating_match.group(2))
                print(f"\n[Labeeb] Final paper rated as '{rating}' with confidence {confidence}%")
                # Patch the paper to include the actual rating percent and color
                with open(paper_file, 'r') as pf:
                    content = pf.read()
                color = 'green' if confidence >= 90 else 'red'
                patched = re.sub(r'AI Rating: <percent>%', f'<span style="color:{color};font-weight:bold">AI Rating: {int(confidence)}%</span>', content)
                with open(paper_file, 'w') as pf:
                    pf.write(patched)
            else:
                rating = 'unknown'
                confidence = 0
                print("\n[Labeeb] Could not parse final paper rating")
            print("\n[Labeeb] === Mini-Capability Usage Summary ===")
            for k, v in summary.items():
                print(f"{k}: {v}")
            print("[Labeeb] =====================================\n")
            return paper_content if rating.lower() == 'excellent' and confidence > 90 else ''
        except Exception as e:
            print(f"[Labeeb] Fallback browsing failed: {str(e)}")
            return ''

    def _get_ai_handler(self):
        from labeeb.core.ai_handler import AIHandler
        from labeeb.core.model_manager import ModelManager
        from labeeb.core.config_manager import ConfigManager
        return AIHandler(model_manager=ModelManager(ConfigManager()))
    
    def _generate_awareness_patterns(self, doc) -> List[str]:
        """Generate awareness patterns from the content."""
        patterns = []
        
        # Extract key phrases
        for chunk in doc.noun_chunks:
            if chunk.root.pos_ in ['NOUN', 'PROPN']:
                patterns.append(f"do you know (?:about|if) (?:my|the) {chunk.text}")
                patterns.append(f"what (?:is|are) (?:my|the) {chunk.text}")
                patterns.append(f"show me (?:my|the) {chunk.text}")
        
        # Extract named entities
        for ent in doc.ents:
            if ent.label_ in ['ORG', 'PRODUCT', 'GPE']:
                patterns.append(f"do you know (?:about|if) {ent.text}")
                patterns.append(f"what (?:is|are) {ent.text}")
        
        return list(set(patterns))
    
    def _generate_capability_code(self, topic: str, doc, patterns: List[str]) -> str:
        """Generate capability code for the topic, with sanitized class name."""
        # Sanitize topic for class name: remove non-alphanum, capitalize words, join
        def sanitize_class_name(name: str) -> str:
            # Remove non-alphanumeric, replace with space, then capitalize and join
            name = re.sub(r'[^a-zA-Z0-9]', ' ', name)
            name = ''.join(word.capitalize() for word in name.split())
            # Ensure it starts with a letter
            if not name or not name[0].isalpha():
                name = 'Topic' + name
            # Fallback if empty
            if not name:
                name = 'ResearchTopic'
            return name
        class_name = sanitize_class_name(topic) + 'Capability'
        # Check if class_name is a valid Python identifier
        if not class_name.isidentifier():
            # Try to fix by prepending 'Topic'
            class_name = 'Topic' + class_name
            if not class_name.isidentifier():
                raise ValueError(f"Cannot generate a valid Python class name from topic: '{topic}' (tried '{class_name}')")
        # Generate code
        code = f"""from typing import Dict, Any\nimport logging\n\nlogger = logging.getLogger(__name__)\n\nclass {class_name}:\n    \"\"\"Provides awareness of {topic}.\"\"\"\n    \n    def __init__(self):\n        self.patterns = {patterns}\n    \n    def process_query(self, query: str) -> Dict[str, Any]:\n        \"\"\"Process a query about {topic}.\"\"\"\n        try:\n            # TODO: Implement specific capability logic\n            return {{\n                \"status\": \"ok\",\n                \"message\": \"Capability not yet implemented\",\n                \"patterns\": self.patterns\n            }}\n        except Exception as e:\n            logger.error(f\"Failed to process {topic} query: {{str(e)}}\")\n            return {{\n                \"status\": \"error\",\n                \"message\": str(e)\n            }}\n"""
        return code
    
    def _save_research_entry(self, entry: ResearchEntry, topic_dir: Path):
        """Save the research entry to a file."""
        # Save content
        content_file = topic_dir / f"content_{entry.date}.txt"
        with open(content_file, 'w') as f:
            f.write(entry.content)
        
        # Save patterns
        patterns_file = topic_dir / f"patterns_{entry.date}.txt"
        with open(patterns_file, 'w') as f:
            for pattern in entry.awareness_patterns:
                f.write(f"{pattern}\n")
        
        # Save capability code
        code_file = topic_dir / f"capability_{entry.date}.py"
        with open(code_file, 'w') as f:
            f.write(entry.capability_code)
    
    def _save_images(self, images: List[Dict[str, str]], topic_dir: Path):
        """Save images from the research topic."""
        for img in images:
            try:
                response = requests.get(img['src'])
                if response.status_code == 200:
                    filename = f"image_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{img['src'].split('/')[-1]}"
                    with open(topic_dir / filename, 'wb') as f:
                        f.write(response.content)
            except Exception as e:
                logger.error(f"Failed to save image {img['src']}: {str(e)}")

    def _print_summary(self, summary: dict):
        print("\n[Labeeb] === Research Process Summary ===")
        for k, v in summary.items():
            print(f"{k}: {v}")
        print("[Labeeb] ===============================\n")

class AwarenessIntegrator:
    """Integrates research findings into Labeeb's awareness system."""
    
    def __init__(self, research_manager: ResearchManager):
        self.research_manager = research_manager
        self.awareness_managers = {}
    
    def integrate_topic(self, topic: str) -> bool:
        """Integrate a researched topic into the awareness system, with error handling for invalid files."""
        try:
            topic_dir = self.research_manager.research_dir / topic.lower().replace(" ", "_")
            # Find latest capability file
            capability_files = list(topic_dir.glob("capability_*.py"))
            if not capability_files:
                return False
            latest_capability = max(capability_files, key=lambda x: x.stat().st_mtime)
            # Try to import and instantiate the capability
            import importlib.util
            spec = importlib.util.spec_from_file_location(topic, latest_capability)
            module = importlib.util.module_from_spec(spec)
            try:
                spec.loader.exec_module(module)
            except SyntaxError as e:
                # Delete the invalid file and show a user-friendly error
                latest_capability.unlink(missing_ok=True)
                logger.error(f"Failed to integrate topic {topic}: {e}")
                print(f"[Labeeb] Error: The generated capability file for '{topic}' was invalid and has been removed. Please try again with a different topic name or contact support if this persists.")
                return False
            # Find the class (should end with 'Capability')
            class_name = None
            for attr in dir(module):
                if attr.endswith('Capability') and isinstance(getattr(module, attr), type):
                    class_name = attr
                    break
            if not class_name:
                logger.error(f"No valid capability class found in {latest_capability}")
                print(f"[Labeeb] Error: No valid capability class found in the generated file for '{topic}'. Please try again.")
                return False
            capability_class = getattr(module, class_name)
            self.awareness_managers[topic] = capability_class()
            return True
        except Exception as e:
            logger.error(f"Failed to integrate topic {topic}: {str(e)}")
            print(f"[Labeeb] Error: Could not integrate topic '{topic}': {str(e)}")
            return False
    
    def get_awareness_patterns(self, topic: str) -> List[str]:
        """Get awareness patterns for a topic."""
        if topic in self.awareness_managers:
            return self.awareness_managers[topic].patterns
        return []
    
    def process_query(self, topic: str, query: str) -> Dict[str, Any]:
        """Process a query using the topic's capability."""
        if topic in self.awareness_managers:
            return self.awareness_managers[topic].process_query(query)
        return {
            "status": "error",
            "message": f"Topic {topic} not integrated"
        }

class AppControlCapability:
    def launch_browser(self, url: str) -> bool:
        import platform, subprocess, time
        system = platform.system().lower()
        try:
            if system == 'darwin':
                subprocess.run(["open", url])
            elif system == 'windows':
                subprocess.run(["start", url], shell=True)
            elif system == 'linux':
                subprocess.run(["xdg-open", url])
            else:
                print(f"[AppControl] Unsupported OS: {system}")
                return False
            time.sleep(3)
            print(f"[AppControl] Browser launched for {url}")
            return True
        except Exception as e:
            print(f"[AppControl] Failed to launch browser: {e}")
            return False

class MouseControlCapability:
    def move_and_click(self, x: int, y: int) -> bool:
        try:
            from labeeb.platform_core.platform_utils import get_input_handler
            handler = get_input_handler()
            handler.move_mouse(x, y)
            time.sleep(1)
            handler.click_mouse(x, y)
            print(f"[MouseControl] Moved and clicked at ({x},{y})")
            return True
        except Exception as e:
            print(f"[MouseControl] Failed: {e}")
            return False

class KeyboardControlCapability:
    def type_and_enter(self, text: str) -> bool:
        try:
            from labeeb.platform_core.platform_utils import get_input_handler
            handler = get_input_handler()
            for c in text:
                handler.type_text(c)
                time.sleep(0.05)
            handler.press_key('enter')
            print(f"[KeyboardControl] Typed and entered: {text}")
            return True
        except Exception as e:
            print(f"[KeyboardControl] Failed: {e}")
            return False

class PageContentCapability:
    def extract(self, url: str):
        try:
            import requests
            from bs4 import BeautifulSoup
            resp = requests.get(url, timeout=10)
            soup = BeautifulSoup(resp.text, 'html.parser')
            page_title = soup.title.string if soup.title else url
            main_text = soup.get_text(separator='\n', strip=True)[:2000]
            links = [(a.get('href'), a.get_text(strip=True)) for a in soup.find_all('a', href=True)]
            print(f"[PageContent] Extracted content and {len(links)} links from {url}")
            return page_title, main_text, links
        except Exception as e:
            print(f"[PageContent] Failed: {e}")
            return None, '', []

class NavigationCapability:
    def resolve_link(self, current_url: str, link: str) -> str:
        from urllib.parse import urljoin
        if not link.startswith('http'):
            return urljoin(current_url, link)
        return link 