nextflow.enable.dsl = 2

valid_entry_points = ['data_to_model', 'model_to_data']
if (!valid_entry_points.contains(params.entry)) {
    error "Invalid entry point: '${params.entry}'. Valid options are: ${valid_entry_points.join(', ')}"
}

// Evaluates data-to-model challenges hosted on Synapse
include { DATA_TO_MODEL } from './workflows/DATA_TO_MODEL.nf'
// Evaluates model-to-data challenges hosted on Synapse
include { MODEL_TO_DATA } from './workflows/MODEL_TO_DATA.nf'

workflow {
    if (params.entry == 'data_to_model') {
        DATA_TO_MODEL ()
    }
    else if (params.entry == 'model_to_data') {
        MODEL_TO_DATA ()
    }
}
