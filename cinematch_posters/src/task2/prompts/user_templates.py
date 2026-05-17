# -*- coding: utf-8 -*-
"""Templates de prompts utilisateur pour GPT-4o par style d'affiche"""

USER_TEMPLATE_REALISTIC = """
ðŸŽ¬ MOVIE METADATA:
â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”
Title: {title}
Genres: {genres}
Year: {year}
Language: {language}
â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”

ðŸ“– STORY ESSENCE:
{overview}
â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”

ðŸŽ¯ YOUR TASK:
Create a masterful visual direction for a movie poster featuring realistic human characters.

Focus on:
â€¢ Character appearance (age, features, expression)
â€¢ Wardrobe and textures
â€¢ Lighting that reveals natural skin and eyes
â€¢ Composition that emphasizes emotion

Describe ONLY the visual elements. Create original characters (no celebrities).
"""

USER_TEMPLATE_ABSTRACT = """
ðŸŽ¬ MOVIE METADATA:
â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”
Title: {title}
Genres: {genres}
Year: {year}
Language: {language}
â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”

ðŸ“– STORY ESSENCE:
{overview}
â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”

ðŸŽ¯ YOUR TASK:
Create a masterful visual direction for a movie poster that captures 
the emotional core and unique atmosphere of this film.

Think deeply about:
â€¢ What visual metaphor best represents this story?
â€¢ What color palette evokes the right emotions?
â€¢ What lighting technique fits the mood?
â€¢ What composition creates the most impact?

Describe ONLY the visual elements.  text, no characters,  titles.
"""

USER_TEMPLATE_MINIMAL = """
Movie: {title}
Genres: {genres}
Year: {year}
Story: {overview}

Generate a minimalist visual concept for a movie poster.
Focus: core emotion, dominant color, simple composition.
Single paragraph, no text.
"""


def get_user_template(style: str = "realistic") -> str:
    """Retourne le template utilisateur selon le style"""
    templates = {
        "realistic": USER_TEMPLATE_REALISTIC,
        "abstract": USER_TEMPLATE_ABSTRACT,
        "minimal": USER_TEMPLATE_MINIMAL
    }
    return templates.get(style, USER_TEMPLATE_REALISTIC)
