import os
import json
import logging
from datetime import datetime
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from pathlib import Path

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
        """Add a new research topic."""
        try:
            # Create topic directory
            topic_dir = self.research_dir / topic.lower().replace(" ", "_")
            topic_dir.mkdir(exist_ok=True)
            
            # Create initial topic file
            topic_file = topic_dir / "topic.txt"
            with open(topic_file, 'w') as f:
                f.write(f"{topic}\n{url}\n")
            
            return True
        except Exception as e:
            logger.error(f"Failed to add topic {topic}: {str(e)}")
            return False
    
    def process_topic(self, topic: str) -> bool:
        """Process a research topic."""
        try:
            # Read topic file
            topic_dir = self.research_dir / topic.lower().replace(" ", "_")
            topic_file = topic_dir / "topic.txt"
            
            if not topic_file.exists():
                logger.error(f"Topic file not found: {topic_file}")
                return False
            
            with open(topic_file, 'r') as f:
                lines = f.readlines()
                topic_name = lines[0].strip()
                url = lines[1].strip()
            
            # Scrape content
            result = self.scraper.scrape_topic(url, topic_name)
            if result['status'] != 'success':
                return False
            
            # Process content with NLP
            content = result['content']
            doc = self.scraper.nlp(content)
            
            # Generate awareness patterns
            patterns = self._generate_awareness_patterns(doc)
            
            # Generate capability code
            capability_code = self._generate_capability_code(topic_name, doc, patterns)
            
            # Create research entry
            entry = ResearchEntry(
                topic=topic_name,
                url=url,
                date=datetime.now().strftime("%Y-%m-%d"),
                content=content,
                awareness_patterns=patterns,
                capability_code=capability_code
            )
            
            # Save research entry
            self._save_research_entry(entry, topic_dir)
            
            # Save images
            self._save_images(result['images'], topic_dir)
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to process topic {topic}: {str(e)}")
            return False
    
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
        """Generate capability code for the topic."""
        # Create a basic capability class
        code = f"""from typing import Dict, Any
import logging

logger = logging.getLogger(__name__)

class {topic.replace(" ", "")}Capability:
    \"\"\"Provides awareness of {topic}.\"\"\"
    
    def __init__(self):
        self.patterns = {patterns}
    
    def process_query(self, query: str) -> Dict[str, Any]:
        \"\"\"Process a query about {topic}.\"\"\"
        try:
            # TODO: Implement specific capability logic
            return {{
                "status": "ok",
                "message": "Capability not yet implemented",
                "patterns": self.patterns
            }}
        except Exception as e:
            logger.error(f"Failed to process {topic} query: {{str(e)}}")
            return {{
                "status": "error",
                "message": str(e)
            }}
"""
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

class AwarenessIntegrator:
    """Integrates research findings into UaiBot's awareness system."""
    
    def __init__(self, research_manager: ResearchManager):
        self.research_manager = research_manager
        self.awareness_managers = {}
    
    def integrate_topic(self, topic: str) -> bool:
        """Integrate a researched topic into the awareness system."""
        try:
            topic_dir = self.research_manager.research_dir / topic.lower().replace(" ", "_")
            
            # Find latest capability file
            capability_files = list(topic_dir.glob("capability_*.py"))
            if not capability_files:
                return False
            
            latest_capability = max(capability_files, key=lambda x: x.stat().st_mtime)
            
            # Import and instantiate the capability
            import importlib.util
            spec = importlib.util.spec_from_file_location(topic, latest_capability)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            
            capability_class = getattr(module, f"{topic.replace(' ', '')}Capability")
            self.awareness_managers[topic] = capability_class()
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to integrate topic {topic}: {str(e)}")
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