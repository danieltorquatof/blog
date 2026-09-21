from pathlib import Path

import yaml
from IPython.display import Markdown

from .education_widget import educationWidget
from .experience_widget import experienceWidget
from .schemas import ResumeSchema


def loadResume(path: str | Path) -> ResumeSchema:
    with open(path, encoding="utf-8") as file:
        return ResumeSchema.model_validate(yaml.safe_load(file))


def renderExperience(resume: ResumeSchema) -> Markdown:
    return Markdown(
        "\n\n".join(experienceWidget(experience).data for experience in resume.experience)
    )


def renderEducation(resume: ResumeSchema) -> Markdown:
    return Markdown(
        "\n\n".join(educationWidget(education).data for education in resume.education)
    )
