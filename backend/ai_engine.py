import os
import json
from typing import List, Literal, Optional
from pydantic import BaseModel, Field
from google import genai
from google.genai import types

# Define strict Pydantic schemas for LLM Structured Output
MajorThemeType = Literal["Taken from Christianity", "LDS-specific", "National/Patriotic", "Other"]

class AlteredPhrase(BaseModel):
    original: str = Field(description="The original line or phrase text")
    new: str = Field(description="The modified line or phrase text in the target hymn")

class HymnClassification(BaseModel):
    major_theme: MajorThemeType = Field(
        description="Must be exactly one of: 'Taken from Christianity', 'LDS-specific', 'National/Patriotic', 'Other'"
    )
    minor_theme: str = Field(
        description="A string identifying the specific sub-category (e.g., Restoration, Pioneer, Praise and Thanksgiving, Sacrament, Easter/Christmas)"
    )

class HymnComparisonResult(BaseModel):
    omitted_verses: List[str] = Field(
        default_factory=list,
        description="An array of strings listing any verses or stanzas present in the source text but omitted in the target text"
    )
    altered_phrases: List[AlteredPhrase] = Field(
        default_factory=list,
        description="An array of objects specifying original vs modified phrasing"
    )
    change_categories: List[str] = Field(
        default_factory=list,
        description="An array of strings categorizing the nature of changes (e.g., 'Gender-inclusive language', 'Theological refinement', 'Archaic grammar update', 'Restoration of original Christian verse')"
    )
    summary: str = Field(
        description="A short paragraph explaining why the changes were likely made and their theological implications"
    )
    classification: HymnClassification = Field(
        description="Thematic categorization of the hymn"
    )

SYSTEM_PROMPT = """You are an expert Theological Editor, Hymnologist, and Taxonomist specializing in the hymnody of Latter-day Saint (LDS) tradition and general Western Christian hymnology.

Your task is to analyze and compare two versions of a hymn text:
1. Source Text (e.g., Traditional Christian Original or 1985 LDS Hymnal version)
2. Target Text (e.g., 1985 LDS Hymnal version or New "Hymns—for Home and Church" release)

Analyze all differences between the two texts carefully:
- Identify any omitted verses or stanzas.
- Identify altered phrases line by line.
- Categorize the underlying theological, linguistic, or cultural reasons for the shifts.
- Write a concise summary explaining the rationale for the edits.
- Classify the hymn's primary theme into one of the exact major theme options and provide a detailed minor theme sub-category.

Strictly adhere to the requested JSON structure.
"""

def analyze_hymn_comparison(
    hymn_text_1985: str,
    hymn_text_new: str,
    hymn_text_original: Optional[str] = None,
    api_key: Optional[str] = None
) -> HymnComparisonResult:
    """
    Compares two hymn texts (e.g. 1985 LDS Hymnal vs New Hymnal) and returns a structured JSON analysis result.
    If hymn_text_original is provided, it incorporates 3-way historical context.
    """
    key = api_key or os.getenv("GEMINI_API_KEY")
    if not key:
        raise ValueError("GEMINI_API_KEY environment variable is missing.")

    client = genai.Client(api_key=key)

    user_prompt = f"""
SOURCE HYMN TEXT (1985 Version / Base):
{hymn_text_1985}

TARGET HYMN TEXT (New / Comparison Version):
{hymn_text_new}
"""
    if hymn_text_original:
        user_prompt += f"""
HISTORICAL ORIGINAL CHRISTIAN HYMN TEXT:
{hymn_text_original}
"""

    user_prompt += "\nPlease perform the full theological comparison and return the strict JSON output."

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=user_prompt,
        config=types.GenerateContentConfig(
            system_instruction=SYSTEM_PROMPT,
            response_mime_type="application/json",
            response_schema=HymnComparisonResult,
            temperature=0.2,
        ),
    )

    # Parse and validate returned JSON content
    result_dict = json.loads(response.text)
    return HymnComparisonResult.model_validate(result_dict)

if __name__ == "__main__":
    # Test script standalone functionality with sample input
    sample_1985 = """Verse 1: Joy to the world, the Lord is come! Let earth receive her King;
Let ev'ry heart prepare him room, And heav'n and nature sing.
Verse 2: Joy to the earth, the Savior reigns! Let men their songs employ;
Verse 3: Rejoice! Rejoice when Jesus reigns, And saints their songs employ;"""

    sample_new = """Verse 1: Joy to the world, the Lord is come! Let earth receive her King;
Let ev'ry heart prepare him room, And heav'n and nature sing.
Verse 2: Joy to the earth, the Savior reigns! Let all their songs employ;
Verse 3: No more let sins and sorrows grow, Nor thorns infest the ground;
He comes to make his blessings flow Far as the curse is found."""

    print("Running test run of AI Comparison Engine...")
    api_key_env = os.getenv("GEMINI_API_KEY")
    if api_key_env:
        res = analyze_hymn_comparison(sample_1985, sample_new)
        print("Success! Result:")
        print(res.model_dump_json(indent=2))
    else:
        print("GEMINI_API_KEY not set. AI engine script structure verified.")
