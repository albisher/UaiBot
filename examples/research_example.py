import logging
from pathlib import Path
from uaibot.core.research.automation import ResearchManager, AwarenessIntegrator

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def main():
    try:
        # Initialize the research system
        research_manager = ResearchManager()
        awareness_integrator = AwarenessIntegrator(research_manager)
        
        # Example 1: Add a new topic
        topic = "MITRE ATT&CK Framework"
        url = "https://attack.mitre.org/"
        
        logger.info(f"Adding new topic: {topic}")
        if research_manager.add_topic(topic, url):
            logger.info(f"Successfully added topic: {topic}")
        else:
            logger.error(f"Failed to add topic: {topic}")
            return
        
        # Example 2: Process the topic
        logger.info(f"Processing topic: {topic}")
        if research_manager.process_topic(topic):
            logger.info(f"Successfully processed topic: {topic}")
        else:
            logger.error(f"Failed to process topic: {topic}")
            return
        
        # Example 3: Integrate the topic into awareness system
        logger.info(f"Integrating topic into awareness system: {topic}")
        if awareness_integrator.integrate_topic(topic):
            logger.info(f"Successfully integrated topic: {topic}")
            
            # Example 4: Get awareness patterns
            patterns = awareness_integrator.get_awareness_patterns(topic)
            logger.info("\nGenerated awareness patterns:")
            for pattern in patterns:
                logger.info(f"- {pattern}")
            
            # Example 5: Process a query
            query = "do you know about MITRE ATT&CK?"
            logger.info(f"\nProcessing query: {query}")
            result = awareness_integrator.process_query(topic, query)
            logger.info(f"Query result: {result}")
        else:
            logger.error(f"Failed to integrate topic: {topic}")
            return
            
    except Exception as e:
        logger.error(f"An error occurred: {str(e)}", exc_info=True)

if __name__ == "__main__":
    main() 