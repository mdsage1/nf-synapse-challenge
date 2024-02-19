// validate submission results
process SCORE {
    secret "SYNAPSE_AUTH_TOKEN"
    container "python:3.12.0rc1"

    input:
    tuple val(submission_id), path(predictions), val(status), path(results)
    path staged_path
    val status_ready
    val annotate_ready
    val scoring_script

    output:
    tuple val(submission_id), path(predictions), stdout, path("results.json")

    script:
    """
    ${scoring_script} '${submission_id}' '${status}' '${predictions}' '${staged_path}' '${results}'
    """
}
