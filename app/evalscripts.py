from enum import Enum

class EvalScripts(Enum):
    TRUE_COLOR = """
        //VERSION=3

        function setup() {
            return {
                input: [{
                    bands: ["B02", "B03", "B04"],
                    units: "DN"
                }],
                output: {
                    bands: 3,
                    sampleType: "INT16"
                }
            };
        }
        
        function updateOutputMetadata(scenes, inputMetadata, outputMetadata) {
            outputMetadata.userData = { "norm_factor":  inputMetadata.normalizationFactor }
        }

        function evaluatePixel(sample) {
            return [sample.B04, sample.B03, sample.B02];
        }
    """