# Semantic entity extraction

Use the following codebook as the complete specification for annotation. Your task is to extract literal words or short spans from the supplied target sentences and classify them into its ten categories. Operational and maintenance notes describe the service workflow; perform only extraction and classification for the current input.

Apply the codebook to every sentence in `target_input.sentences`. Extract only literal spans from those sentences, preserving their original language, and record each valid occurrence. Copy `document_id` and the corresponding `sentence_id` exactly. Return the complete annotations through `submit_entity_annotations`, with only `label`, `text`, `sentence_id`, and `ambiguity` for each annotation. If no mentions qualify, return an empty `annotations` array.

Do not annotate stopwords or discourse words as entities. In particular, never return isolated pronouns, determiners, conjunctions, prepositions, or adverbs such as “misma”, “así”, “además”, or “también”: they do not identify an actor, place, or any other category on their own. Before submitting, check that every span names a concrete referent or category-specific content supported by context. A function word may remain inside a longer valid span when it is necessary to preserve the literal designation or a proper name.

Specific PRAC rule: when “agroforestry”, “agroforestería” (also “agroforesteria”), or “AFSs” is the whole candidate mention, always label it PRAC, regardless of capitalization; never label that standalone mention CHAR, LOC, or another category. If the term is part of a longer expression that identifies a different component, classify that complete expression instead: “agroforestry farmers” is CHAR. Do not also extract the embedded word “agroforestry” as a separate, overlapping PRAC mention.

Confirmed category examples: “Wyss Academy” and “WA SAM Hub” are CHAR, including when a sentence mentions their area of work; “agroforestry systems” is PRAC, never LOC. Resolve shorter acronyms such as “WA” from context.

Brazil nut rule: when the source names the nut or biological resource, extract the complete literal “Brazil nut” or “Brazil nuts” (preserving original case, spelling and hyphens) as eco_INFRA. Never extract the embedded “Brazil” or “Brazi” as LOC. A separate reference to the country Brazil remains LOC, even if Brazil nuts occur elsewhere in the same sentence. Longer expressions such as “Brazil nut harvesting” describe a practice and remain PRAC; do not add an overlapping location inside them.

<codebook>
$codebook
</codebook>

<target_input>$json_input</target_input>
