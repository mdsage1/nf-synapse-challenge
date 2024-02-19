# This is a placeholder for the validation script for the Dynamic Challenge
# All it does is check if the predictions file is a tarball

#!/usr/bin/env python3

import json
import sys
import tarfile

if __name__ == "__main__":
    predictions_path = sys.argv[1]
    invalid_reasons = []
    if predictions_path is None:
        prediction_status = "INVALID"
        invalid_reasons.append("Predictions file not found")
    else:
        # check if predictions file is a tarball
        if tarfile.is_tarfile(predictions_path):
            prediction_status = "VALIDATED"
        else:
            prediction_status = "INVALID"
            invalid_reasons.append("Predictions file is not a tarball")
    result = {
        "validation_status": prediction_status,
        "validation_errors": ";".join(invalid_reasons),
    }

    with open("results.json", "w") as o:
        o.write(json.dumps(result))
    print(prediction_status)
