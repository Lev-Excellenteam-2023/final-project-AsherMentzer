import argparse
import asyncio
import json
from typing import Dict
from presentation_parser import PresentationParser
from gpt_slide_explainer import GPTSlideExpander
from slide_expander import SlideExpander


def parse_args() -> argparse.Namespace:
    """Parse command-line arguments.
    Returns:
        argparse.Namespace: Parsed command-line arguments.
    """
    argument_parser = argparse.ArgumentParser(description="Generate slide explanations from a PPTX file")
    argument_parser.add_argument("pptx_file", help="Path to the PPTX file")
    # argument_parser.add_argument("-t", "--topic", help="Main topic of the presentation")
    return argument_parser.parse_args()


def output_to_json(output_path: str, expanded_slide_explanations: Dict[int, str]) -> None:
    """Output the expanded slide explanations to a JSON file.

    Args:
        output_path (str): Path to the output JSON file.
        expanded_slide_explanations (Dict[int, str]): Dictionary with slide numbers as keys and explanations as values.
    """
    with open(output_path, "w") as file:
        json.dump(expanded_slide_explanations, file, indent=4)


def main():
    args = parse_args()
    presentation_parser = PresentationParser("asyncio-intro.pptx")
    presentation_parser.parse()
    slide_expander = GPTSlideExpander()

    presentation_main_topic = "python"  # args.topic

    if not presentation_main_topic:
        presentation_main_topic = slide_expander.generate_topic_for_presentation(
            presentation_parser.get_all_presentation_text())

    # SlideExpander.generate_explanation_for_presentation(self=slide_expander,
    #                                                     parsed_presentation=presentation_parser.presentation_text,
    #                                                     presentation_topic=presentation_main_topic)
    asyncio.run(
        GPTSlideExpander.generate_explanation_for_presentation(slide_expander, presentation_parser.presentation_text,
                                                               presentation_main_topic)
    )

    # Output the explanations to a JSON file
    output_file = args.pptx_file.replace(".pptx", ".json")
    output_to_json(output_file, slide_expander.expanded_slide_explanations)


if __name__ == '__main__':
    main()

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
