# Blind-packet locator index (convenience only)

The complete frozen corpus in corpus/ is authoritative; this index is a
finding aid, not a substitute. Key sections in
corpus/xacml-3.0-core-spec-cos01-en.html (stripped-text lines):
- Data-flow model (PEP/handler/PDP): lines 1755-1784; glossary 931/1007/1016
- Sec. 5.29 AttributeDesignator: lines 406-407; Sec. 5.30 Selector: 409-410
- MustBePresent semantics: lines 6292-6294
- Sec. 7.3.5 Attribute Retrieval: lines 8405-8424
- Sec. 7.6 Match evaluation: lines 8577-8594
- Rule True/False/error semantics + target mismatch: lines 2308-2322
- StatusDetail/MissingAttributeDetail elements: lines 491-494
Fixture corpus: corpus/fixture/{pdp.xml,request.xml,response.xml,
policies/policy.xml}; corpus/RELEASE.json, COMMIT.txt, MANIFEST.json.
Candidate mappings under candidates/ (blind-safe: no touch/K/outcomes).
