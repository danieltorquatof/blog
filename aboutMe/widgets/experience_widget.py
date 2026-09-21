from datetime import date
from typing import List

from IPython.display import Markdown

from .schemas import ExperienceSchema, PositionSchema


def calculateMonths(startDate: date, endDate: date) -> str:
    totalMonths: int = (endDate.year - startDate.year) * 12 + (
        endDate.month - startDate.month + 1
    )

    years, months = divmod(
        totalMonths,
        12,
    )

    return f"{years} years and {months} months" if years > 0 else f"{months} months"


def formatLocation(position: PositionSchema) -> str:
    return " · ".join(
        part for part in [position.location, position.locationType.value] if part
    )


def generateTitle(experience: ExperienceSchema) -> str:
    firstPosition: PositionSchema = experience.positions[0]

    totalTime: str = calculateMonths(
        experience.positions[-1].startDate,
        experience.positions[0].endDate,
    )

    return (
        f"""> ##### **{experience.company}**  \n"""
        f"> {firstPosition.employmentType.value}{f" · {totalTime}" if not firstPosition.present else ""}  \n"
        f"> {formatLocation(firstPosition)} \n"
        "> \n"
    )


def formatPositions(experience: ExperienceSchema) -> str:
    response: str = ""

    positions: List[PositionSchema] = experience.positions

    if len(positions) > 1:
        for position in positions:
            time: str = calculateMonths(
                position.startDate,
                position.endDate,
            )

            startDateFormatted: str = position.startDate.strftime("%B %Y")
            endDateFormatted: str = position.endDate.strftime("%B %Y")

            response += (
                f"> > **{position.title}**  \n"
                f"> > {startDateFormatted} - {"Present" if position.present else endDateFormatted}{f" · {time}" if not position.present else ""}  \n"
                "> \n"
            )

        return response

    position: PositionSchema = positions[0]

    time: str = calculateMonths(
        position.startDate,
        position.endDate,
    )

    startDateFormatted: str = position.startDate.strftime("%B %Y")
    endDateFormatted: str = position.endDate.strftime("%B %Y")

    response += (
        f"""> ##### **{experience.company} · {position.employmentType.value}**\n"""
        f"> {startDateFormatted} - {"Present" if position.present else endDateFormatted} · {time}  \n"
        f"> {formatLocation(position)}  \n"
        "> \n"
    )

    return response


def experienceWidget(experience: ExperienceSchema) -> Markdown:
    title: str = (
        generateTitle(experience=experience)
        if len(experience.positions) > 1
        else f"""> ##### **{experience.positions[0].title}**\n"""
    )

    content: str = formatPositions(experience=experience)

    return Markdown(title + content)
