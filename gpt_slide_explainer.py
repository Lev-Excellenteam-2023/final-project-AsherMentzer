import sys
from typing import Dict
import asyncio
import openai

MAX_TOKENS = 200
TEMPERATURE = 0.7

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
        # openai.api_key = os.getenv("OPENAI_API_KEY")
        with open(r"C:\Users\USER\Downloads\api_key.txt", 'r') as f:
            openai.api_key = str(f.read())

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

        async def process_slide(index: int, slide):
            try:
                if slide:
                    explanation = await self.generate_explanation_for_slide(slide, presentation_topic)
                    self.expanded_slide_explanations[index] = explanation
            except Exception as e:
                explanation = f"An error occurred during processing this part: {str(e)}"
                self.expanded_slide_explanations[index] = explanation

        await asyncio.gather(*[process_slide(index, slide) for index, slide in enumerate(parsed_presentation.values())])

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
                gpt_response = await openai.ChatCompletion.acreate(
                    model="gpt-3.5-turbo",
                    max_tokens=MAX_TOKENS,
                    temperature=TEMPERATURE,
                    messages=messages
                )

                return gpt_response['choices'][0]['message']['content']
            except openai.error.AuthenticationError:
                pass
            except RuntimeError:
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
                gpt_response = await openai.ChatCompletion.acreate(
                    model="gpt-3.5-turbo",
                    max_tokens=MAX_TOKENS,
                    temperature=TEMPERATURE,
                    messages=messages
                )

                return gpt_response['choices'][0]['message']['content']
            except openai.error.AuthenticationError:
                pass
            except RuntimeError:
                pass
        else:
            return ''
