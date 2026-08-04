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
    hymn_text_new: Optional[str] = None,
    hymn_text_original: Optional[str] = None,
    api_key: Optional[str] = None
) -> HymnComparisonResult:
    """
    Compares available versions of a hymn (1985 LDS Hymnal, New Release, Traditional Original)
    and returns a structured JSON analysis result.
    """
    key = api_key or os.getenv("GEMINI_API_KEY")
    if not key:
        raise ValueError("GEMINI_API_KEY environment variable is missing.")

    client = genai.Client(api_key=key)

    user_prompt = f"""
1985 LDS HYMNAL VERSION (Base):
{hymn_text_1985}
"""
    if hymn_text_new:
        user_prompt += f"""
NEW DIGITAL RELEASE ("Hymns—for Home and Church"):
{hymn_text_new}
"""
    else:
        user_prompt += "\nNEW DIGITAL RELEASE: Not yet released in new digital batches.\n"

    if hymn_text_original:
        user_prompt += f"""
HISTORICAL TRADITIONAL CHRISTIAN PRECURSOR ORIGINAL:
{hymn_text_original}
"""
    else:
        user_prompt += "\nHISTORICAL TRADITIONAL PRECURSOR: No precursor linked.\n"

    user_prompt += "\nPlease perform the full theological comparison across all available versions and return the strict JSON output."

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

class OriginalHymnDiscovery(BaseModel):
    is_traditional_christian: bool = Field(description="True if this hymn originates from broader Western Christian hymnody/psalmody, false if LDS-specific")
    title: str = Field(description="Original traditional Christian hymn title")
    original_author: Optional[str] = Field(default="Traditional", description="Original poet/author, e.g. Isaac Watts, Charles Wesley, John Newton, etc.")
    publication_year: Optional[int] = Field(default=None, description="Original publication year if known, e.g. 1719")
    original_source: Optional[str] = Field(default="Christian Hymnal", description="Original collection/source if known")
    lyrics: str = Field(description="Original traditional Christian lyrics before LDS adaptation")
    minor_theme: str = Field(default="General Worship", description="Minor theme, e.g. Praise and Thanksgiving, Easter/Christmas, Sacrament")

DISCOVERY_SYSTEM_PROMPT = """You are an expert Hymnologist and Taxonomist specializing in Western Christian hymnody and psalmody.
Your task is to analyze a hymn title and lyrics to determine if it is a traditional Christian hymn (e.g. Watts, Wesley, Newton, Luther, Heber, English/French carols, etc.).
If it is a traditional Christian hymn, provide its original author, publication year, original publication source, original lyrics, and minor theme.
If it is an LDS-specific original hymn, set is_traditional_christian to false.
"""

def discover_original_christian_hymn(title: str, lyrics: str, api_key: Optional[str] = None) -> Optional[OriginalHymnDiscovery]:
    key = api_key or os.getenv("GEMINI_API_KEY")
    if not key:
        return None
    try:
        client = genai.Client(api_key=key)
        prompt = f"HYMN TITLE: {title}\nLYRICS:\n{lyrics}"
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt,
            config=types.GenerateContentConfig(
                system_instruction=DISCOVERY_SYSTEM_PROMPT,
                response_mime_type="application/json",
                response_schema=OriginalHymnDiscovery,
                temperature=0.1,
            ),
        )
        result_dict = json.loads(response.text)
        obj = OriginalHymnDiscovery.model_validate(result_dict)
        return obj if obj.is_traditional_christian else None
    except Exception as e:
        print(f"Error discovering original Christian hymn: {e}")
        return None
