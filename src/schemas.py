from typing import List, Optional
from pydantic import BaseModel, Field

class Reaction(BaseModel):
    """ Represents an adverse reaction coded in MedDRA. """
    pt_term: str = Field(...,description="MedDRA Preferred Term")
    outcome: Optional[str] = Field(default="Unspecified", description="Outcome code")

class Drug(BaseModel):
    """ Represents a drug administered to the patient. """
    medicinal_product: str
    indication: Optional[str] = "Unspecified"
    role_code: Optional[str] = "Unspecified" # 1 = Suspect, 2 = Concomitant

class SafetyReport(BaseModel):
    """ Parsed and validated Adverse Event Case Report. """
    report_id: str
    receive_date: Optional[str] = None
    drugs: List[Drug] = Field(default_factory=list)
    reactions: List[Reaction] = Field(default_factory=list)

    @classmethod
    def from_openfda_dict(cls, raw: dict) -> "SafetyReport":
        """
        Custom parser extracting only the fields relevant to safety signal detection.
        """
        patient = raw.get("patient",{})

        # Parse drugs
        parsed_drugs = []
        for d in patient.get("drug", []):
            parsed_drugs.append(
                Drug(
                    medicinal_product=d.get("medicinalproduct", "Unknown"),
                    indication=d.get("drugindication", "Unspecified"),
                    role_code=str(d.get("drugcharacterization", "Unspecified")),
                )
            )

        # Parse reactions
        parsed_reactions = []
        for r in patient.get("reaction", []):
            pt = r.get("reactionmeddrapt")
            if pt:
                parsed_reactions.append(
                    Reaction(
                        pt_term=pt,
                        outcome=str(r.get("reactionoutcome", "Unspecified")),
                    )
                )

        return cls(
            report_id=str(raw.get("safetyreportid", "N/A")),
            receive_date=raw.get("receivedate"),
            drugs=parsed_drugs,
            reactions=parsed_reactions,
        )


if __name__ == "__main__":
    from src.api_client import fetch_events

    raw_events = fetch_events("SPIRONOLACTONE", limit=1)
    if raw_events:
        report = SafetyReport.from_openfda_dict(raw_events[0])
        print(" Validation Pydantic réussie !")
        print(f"Report ID: {report.report_id}")
        print(f"Nombre de molécules: {len(report.drugs)}")
        print(f"Effets observés: {[r.pt_term for r in report.reactions]}")