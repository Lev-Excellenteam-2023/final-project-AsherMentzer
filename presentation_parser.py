from pptx import Presentation
from typing import Dict, List


class PresentationParser:
    """A class for parsing text from PowerPoint presentations."""

    def __init__(self, path_to_presentation) -> None:
        """Initializes a new instance of the pptx_parser class.
        Args:
            path_to_presentation (str): The file path of the PowerPoint presentation to parse.
        Raises:
            FileNotFoundError: If the provided file path is not valid.
        """
        self.presentation = None
        try:
            self.presentation = Presentation(path_to_presentation)
        except FileNotFoundError:
            raise FileNotFoundError("Presentation path not found.")

        # dict[slide number : text extracted from slide]
        self.presentation_text: Dict[int, str] = {}

    def parse(self):
        self.presentation_text = PresentationParser.extract_text(self.presentation)

    @staticmethod
    def extract_text(presentation) -> Dict[int, str]:
        """
        Extracts the text from each shape in each slide of a PowerPoint presentation.

        Args:
            presentation (Presentation): The file path to the PowerPoint presentation.

        Returns:
           Dict[int, str] of string of the slides by slide number.
        """
        presentation_text: Dict[int, str] = {}
        slide_number = 0
        for slide in presentation.slides:
            slide_number = slide_number + 1
            text = ""
            for shape in slide.shapes:
                if not shape.has_text_frame:
                    continue
                for paragraph in shape.text_frame.paragraphs:
                    text += "".join(run.text.strip() for run in paragraph.runs)
                    text += "\n"
            if text.strip():
                presentation_text[slide_number] = text.strip()
        return presentation_text

    def get_all_presentation_text(self):
        """
        get all text from presentation concatenated into one single string.
        Returns:
        str: all the text of the presentation.
        """
        return ''.join([value + ' ' for value in self.presentation_text.values()])


if __name__ == "__main__":
    pres = PresentationParser("asyncio-intro.pptx")
    pres.presentation_text = pres.extract_text(pres.presentation)
    for i in pres.presentation_text:
        print(i, ":", pres.presentation_text[i])
