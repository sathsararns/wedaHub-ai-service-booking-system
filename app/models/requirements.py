from pydantic import BaseModel, Field, ConfigDict


class Requirement(BaseModel):
    """
    Structured requirements extracted from the user's message.
    """

    model_config = ConfigDict(
        extra="ignore",
        str_strip_whitespace=True,
    )

    service: str = Field(
        default="",
        description="Requested service category (Electrician, Plumber, Carpenter, etc.)",
    )

    location: str = Field(
        default="",
        description="Requested city or location.",
    )

    date: str = Field(
        default="",
        description="Requested booking date.",
    )

    description: str = Field(
        default="",
        description="Description of the work to be done.",
    )