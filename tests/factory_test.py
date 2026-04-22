from pipeline_lib.core.factory import create_module

module = create_module({
    "type": "SentenceChunkerFunction",
    "language": "en"
})

print(module)
print(module.run("Created SentenceChunker module"))