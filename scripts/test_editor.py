from pipeline_lib.config.state import ConfigurationState
from pipeline_lib.config.editor import ConfigEditor
from pipeline_lib.config.validator import validate_config

state = ConfigurationState()

editor = ConfigEditor(state)

editor.set_chunker(
    {
        "type": "SentenceChunkerFunction",
        "language": "en"
    }
)

editor.set_cleaner(
    {
        "type": "NoClean"
    }
)
print(state.config)

