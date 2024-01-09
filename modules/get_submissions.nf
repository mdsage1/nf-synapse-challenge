// Gets submissions from view
process GET_SUBMISSIONS {
    secret "SYNAPSE_AUTH_TOKEN"
    container "sagebionetworks/synapsepythonclient:v2.7.0"

    input:
    val view_id

    output:
    path "images.csv"

    script:
    """
    get_submissions.py '${view_id}'
    """
}
