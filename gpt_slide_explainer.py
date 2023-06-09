import os
import sys
from typing import Dict
import asyncio
import openai


# Set up your OpenAI API credentials

WINDOWS_PLATFORM = 'win'


class GPTSlideExpander:

    def __init__(self):
        GPTSlideExpander.init_api_key()
        self.expanded_slide_explanations = {}
        if sys.platform.startswith(WINDOWS_PLATFORM):
            asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

    @staticmethod
    def init_api_key():
        """get the api key from the environment arguments"""
        openai.api_key = os.getenv("OPENAI_API_KEY")

    async def generate_explanation_for_presentation(self, parsed_presentation: Dict[int, str], presentation_topic: str
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

        tasks = []
        # Generate tasks for each slide
        for index, slide in enumerate(parsed_presentation.values()):
            task = asyncio.create_task(
                GPTSlideExpander.generate_explanation_for_slide(slide, presentation_topic))
            tasks.append(task)

        # Execute tasks concurrently
        results = await asyncio.gather(*[asyncio.shield(task) for task in tasks])

        # Assign results to slide explanations
        for slide_index, explanation in enumerate(results, start=1):
            self.expanded_slide_explanations[slide_index] = explanation

    @staticmethod
    async def generate_topic_for_presentation(presentation_text: str) -> str:
        """
        Generates an explanation for a slide topic within the context of the main topic.
        Args:
            presentation_text (str): the presentation text to find the topic.
        Returns:
            str: The presentation topic.
        """
        if presentation_text and presentation_text != "":
            messages = [
                {"role": "system",
                 "content": "You are a chatbot that generates the main topic of a presentation."},
                {"role": "user",
                 "content": f"Provide a topic of the presentation based on the content:{presentation_text},up to 3 "
                            f"words."},
            ]
            try:
                gpt_response = await openai.ChatCompletion.create(
                    model="gpt-3.5-turbo",
                    max_tokens=100,
                    temperature=0.7,
                    messages=messages
                )

                return gpt_response['choices'][0]['message']['content']
            except openai.error.AuthenticationError:
                pass
        else:
            return ''

    @staticmethod
    async def generate_explanation_for_slide(slide_text: str, presentation_topic: str) -> str:
        """
        Generates an explanation for a slide topic within the context of the main topic.
        Args:
            slide_text (str): the slide text to explain.
            presentation_topic (str): The main topic of the presentation.
        Returns:
            str: The generated expanded explanation.
        """
        if presentation_topic and presentation_topic != "":
            messages = [
                {"role": "system",
                 "content": "You are a chatbot that generates expanded explanations about slide of presentation."},
                {"role": "user",
                 "content": f"Provide an explanation of the slide based on the content:{slide_text}, within the "
                            f"context of the main topic:{presentation_topic} if applicable, in up to 3 sentences."},
            ]
            try:
                gpt_response = await openai.ChatCompletion.create(
                    model="gpt-3.5-turbo",
                    max_tokens=100,
                    temperature=0.7,
                    messages=messages
                )

                return gpt_response['choices'][0]['message']['content']
            except openai.error.AuthenticationError:
                pass
        else:
            return ''

    @staticmethod
    async def process_slide_task(slide_text: str, presentation_topic: str, max_retry: int,
                                 slide_index: int) -> str:
        """
        Process an individual slide task for generating an explanation.
        Args:
            slide_text: The text of the slide to generate an explanation for.
            presentation_topic: The topic or context of the presentation.
            max_retry: The maximum number of retries for generating the explanation.
            slide_index: The index of the slide being processed.
        Returns:
            The generated explanation for the slide, or an error message if an `openai.error` occurs.
        Raises:
            openai.error: If an OpenAI API error occurs during explanation generation for the slide.
        """
        try:
            return await GPTSlideExpander.generate_explanation_for_slide(slide_text, presentation_topic)

        except openai.error as e:
            return f"ERROR - explanation generation for slide {slide_index} failed: {str(e)}"
