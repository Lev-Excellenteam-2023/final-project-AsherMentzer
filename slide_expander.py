import os
from typing import Dict
import asyncio
import openai


# Set up your OpenAI API credentials


class SlideExpander:

    def __init__(self):
        SlideExpander.init_api_key()
        self.expanded_slide_explanations = {}

    @staticmethod
    def init_api_key():
        """get the api key from the environment arguments"""
        openai.api_key = os.getenv("OPENAI_API_KEY")

    def generate_explanation_for_presentation(self, parsed_presentation: Dict[int, str], presentation_topic: str
                                              ) -> None:
        """
        Generates explanations for each slide in a presentation.
        Args:
            parsed_presentation (Dict[int, str]): A dictionary mapping slide index to slide content.
            presentation_topic (str): main topic of presentation.
        Raises:
            RuntimeError: If the main topic retrieval from the API fails.
        Returns:
            None
        """
        # Execute tasks concurrently
        slide_index = 0
        for index, slide in enumerate(parsed_presentation.values()):
            try:
                slide_index += 1
                explanation = SlideExpander.generate_explanation_for_slide(slide, presentation_topic)
                self.expanded_slide_explanations[slide_index] = explanation
            except openai.error:
                self.expanded_slide_explanations[slide_index] = "ERROR - explanation generation for this slide failed\n"

    @staticmethod
    def generate_topic_for_presentation(presentation_text: str) -> str:
        """
        Generates an explanation for a slide topic within the context of the main topic.
        Args:
            presentation_text (str): the presentation text to find the topic.
        Returns:
            str: The presentation topic.
        """
        if presentation_text:
            messages = [
                {"role": "system",
                 "content": "You are a chatbot that generates the main topic of a presentation."},
                {"role": "user",
                 "content": f"Provide a topic of the presentation based on the content:{presentation_text},up to 3 "
                            f"words."},
            ]
            gpt_response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                max_tokens=100,
                temperature=0.7,
                messages=messages
            )

            return gpt_response['choices'][0]['message']['content']
        else:
            return ''

    @staticmethod
    def generate_explanation_for_slide(slide_text: str, presentation_topic: str) -> str:
        """
        Generates an explanation for a slide topic within the context of the main topic.
        Args:
            slide_text (str): the slide text to explain.
            presentation_topic (str): The main topic of the presentation.
        Returns:
            str: The generated expanded explanation.
        """
        if presentation_topic:
            messages = [
                {"role": "system",
                 "content": "You are a chatbot that generates expanded explanations about slide of presentation."},
                {"role": "user",
                 "content": f"Provide an explanation of the slide based on the content:{slide_text}, within the "
                            f"context of the main topic:{presentation_topic} if applicable, in up to 3 sentences."},
            ]
            gpt_response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                max_tokens=100,
                temperature=0.7,
                messages=messages
            )

            return gpt_response['choices'][0]['message']['content']
        else:
            return ''
