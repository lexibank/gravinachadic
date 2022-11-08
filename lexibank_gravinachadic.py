import pathlib
import attr
from clldutils.misc import slug
from pylexibank import Dataset as BaseDataset
from pylexibank import progressbar as pb
from pylexibank import Language, Concept
from pylexibank import FormSpec
import lingpy


@attr.s
class CustomLanguage(Language):
    SubGroup = attr.ib(default=None)


@attr.s
class CustomConcept(Concept):
    French_Gloss = attr.ib(default=None)


class Dataset(BaseDataset):
    dir = pathlib.Path(__file__).parent
    id = "gravinachadic"
    language_class = CustomLanguage
    concept_class = CustomConcept
    form_spec = FormSpec(
            separators="~;,/", 
            missing_data=["∅"],
            brackets={"(": ")", "[": "]"},
            replacements=[
                ("\u0300", ""), 
                ("\u0320", ""),
                ("\u0301", ""),
                (" ", "_")], 
            first_form_only=True)

    def cmd_makecldf(self, args):
        # add bib
        args.writer.add_sources()
        args.log.info("added sources")

        # add concept
        concepts = {}
        for concept in self.concepts:
            idx = concept["NUMBER"]+"_"+slug(concept["ENGLISH"])
            concepts[concept["ENGLISH"]] = idx
            args.writer.add_concept(
                    ID=idx,
                    Name=concept["ENGLISH"],
                    Concepticon_ID=concept["CONCEPTICON_ID"],
                    Concepticon_Gloss=concept["CONCEPTICON_GLOSS"],
                    French_Gloss=concept["FRENCH_GLOSS"],
                    )
        args.log.info("added concepts")

        # add language
        languages = args.writer.add_languages(lookup_factory="Name")
        args.log.info("added languages")

        # read in data
        wl = lingpy.Wordlist(str(self.raw_dir / "wordlist-short.tsv"))
        wl.renumber("cognacy", "cogid")

        # add data
        for idx in pb(wl, desc="cldfify", total=len(wl)):
            if wl[idx, 'concept'].strip() in concepts:
                for lex in args.writer.add_forms_from_value(
                        Local_ID=wl[idx, "wordid"],
                        Language_ID=languages[wl[idx, "language"]],
                        Parameter_ID=concepts[wl[idx, "concept"]],
                        Value=wl[idx, "value"],
                        Source="Gravina2014",
                        Cognacy=wl[idx, "cogid"]
                        ):
                    args.writer.add_cognate(
                            lexeme=lex,
                            Cognateset_ID=wl[idx, "cogid"],
                            Source="Gravina2014",
                            )

