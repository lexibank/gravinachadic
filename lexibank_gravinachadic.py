import pathlib
import attr
from clldutils.misc import slug
from pylexibank import Dataset as BaseDataset
from pylexibank import progressbar as pb
from pylexibank import Language, Concept, Lexeme
from pylexibank import FormSpec
import lingpy


@attr.s
class CustomLanguage(Language):
    SubGroup = attr.ib(default=None)
    Sources = attr.ib(default=None)



@attr.s
class CustomLexeme(Lexeme):
    English_Gloss_in_Source = attr.ib(default=None)
    French_Gloss_in_Source = attr.ib(default=None)



class Dataset(BaseDataset):
    dir = pathlib.Path(__file__).parent
    id = "gravinachadic"
    language_class = CustomLanguage
    lexeme_class = CustomLexeme
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
        for concept in self.conceptlists[0].concepts.values():
            idx = concept.number+"_"+slug(concept.english)
            concepts[concept.english] = idx
            args.writer.add_concept(
                    ID=idx,
                    Name=concept.english,
                    Concepticon_ID=concept.concepticon_id,
                    Concepticon_Gloss=concept.concepticon_gloss,
                    )
            for itm in concept.attributes["lexibank_gloss_english"]:
                concepts["e: "+itm] = idx
            for itm in concept.attributes["lexibank_gloss_french"]:
                concepts["f: "+itm] = idx
        args.log.info("added concepts")

        # add language
        languages, sources = {}, {}
        for language in self.languages:
            args.log.info("adding language {0}".format(language["Name"]))
            args.writer.add_language(**language)
            languages[language["Name"]] = language["ID"]
            sources[language["Name"]] = language["Sources"].split(",")
        args.log.info("added languages")

        # read in data
        wl = lingpy.Wordlist(str(self.raw_dir / "wordlist-short.tsv"))
        wl.renumber("cognacy", "cogid")

        # add data
        errors = set()
        for idx in pb(wl, desc="cldfify", total=len(wl)):
            if wl[idx, "language"] in languages:
                prm = concepts.get("f: "+wl[idx, "french"], concepts.get("e: "+wl[idx, "english"]))
                if prm:
                    if wl[idx, 'concept'].strip() in concepts:
                        for lex in args.writer.add_forms_from_value(
                                Local_ID=wl[idx, "wordid"],
                                Language_ID=languages[wl[idx, "language"]],
                                Parameter_ID=prm,
                                Value=wl[idx, "value"],
                                Source=sources[wl[idx, "language"]],
                                English_Gloss_in_Source=wl[idx, "english"],
                                French_Gloss_in_Source=wl[idx, "french"],
                                Cognacy=wl[idx, "cogid"]
                                ):
                            args.writer.add_cognate(
                                    lexeme=lex,
                                Cognateset_ID=wl[idx, "cogid"],
                                Source="Gravina2014",
                                )
            else:
                errors.add(("language", wl[idx, 'language']))
        for a, b in errors:
            print(a, b)


